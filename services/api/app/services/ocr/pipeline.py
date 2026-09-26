from uuid import UUID

from supabase import Client

from app.schemas.application import (
    ApplicationStatus,
    OCRStatus,
)
from app.services.ai.extraction_provider import (
    ExtractionError,
)
from app.services.ai.extraction_service import (
    get_extraction_service,
)
from app.services.matching.matching_service import (
    has_conflict,
    match_documents,
)
from app.services.ocr.ocr_service import (
    OCRProcessingError,
    run_ocr,
)
from app.services.risk.risk_service import (
    calculate_risk,
)
from app.services.validation.validation_service import (
    validate_extraction,
)


STORAGE_BUCKET = "application-documents"


def _persist_validation_results(
    application_id: UUID,
    validation_results,
    supabase: Client,
) -> None:
    """
    Persist deterministic validation results.

    The database stores rule_id rather than rule_name.
    rule_name is derived by the validation API from rule_id.
    """

    for result in validation_results:
        validation_data = {
            "application_id": str(application_id),
            "rule_id": result.rule_id,
            "passed": result.passed,
            "extracted_value": result.extracted_value,
            "expected_condition": result.expected_condition,
            "reasoning": result.reasoning,
            "severity": (
                result.severity.value
                if result.severity is not None
                else None
            ),
        }

        supabase.table("validations").insert(
            validation_data
        ).execute()


def _persist_match_results(
    application_id: UUID,
    match_results,
    supabase: Client,
) -> None:
    """
    Persist cross-document matching results.
    """

    for result in match_results:
        match_data = {
            "application_id": str(application_id),
            "left_document_id": result.left_document_id,
            "right_document_id": result.right_document_id,
            "field_name": result.field_name,
            "similarity": result.similarity,
            "match_status": result.match_status.value,
            "reasoning": result.reasoning,
        }

        supabase.table(
            "student_document_matches"
        ).insert(
            match_data
        ).execute()


def process_application_documents(
    application_id: UUID,
    supabase: Client,
) -> None:
    """
    Process all documents belonging to an application.

    Current flow:

    1. Fetch application and scheme.
    2. Fetch application documents.
    3. Download each document from private storage.
    4. Run LlamaCloud OCR.
    5. Persist OCR text and OCR status.
    6. Run configured extraction provider.
    7. Validate extracted data against canonical scheme config.
    8. Persist deterministic validation results.
    9. Collect successful extractions.
    10. Cross-match extracted values between documents.
    11. Persist cross-document match results.
    12. Calculate prototype risk score.
    13. Persist applications.risk_score.
    14. Route conflicts to FLAGGED_FOR_REVIEW.
    15. Keep unreadable cases DEFICIENT.

    Extraction providers:
    - mock
    - gpt4o

    Eligibility decisions are made by deterministic rules,
    not by the AI extraction provider.
    """

    # ---------------------------------------------------------
    # 1. Fetch application
    # ---------------------------------------------------------

    application_result = (
        supabase.table("applications")
        .select("id, scheme_id, status")
        .eq("id", str(application_id))
        .limit(1)
        .execute()
    )

    application_rows = application_result.data or []

    if not application_rows:
        return

    application = application_rows[0]
    scheme_id = application["scheme_id"]

    # ---------------------------------------------------------
    # 2. Fetch configured extraction provider
    # ---------------------------------------------------------

    extraction_service = get_extraction_service()

    # ---------------------------------------------------------
    # 3. Fetch documents
    # ---------------------------------------------------------

    documents_result = (
        supabase.table("documents")
        .select(
            "id, storage_path, document_type, ocr_status"
        )
        .eq("application_id", str(application_id))
        .execute()
    )

    documents = documents_result.data or []

    # ---------------------------------------------------------
    # 4. No documents -> DEFICIENT
    # ---------------------------------------------------------

    if not documents:
        (
            supabase.table("applications")
            .update(
                {
                    "status": ApplicationStatus.DEFICIENT.value,
                    "risk_score": 20,
                }
            )
            .eq("id", str(application_id))
            .execute()
        )

        return

    any_unreadable = False
    extracted_documents = []

    # ---------------------------------------------------------
    # 5. Process every document
    # ---------------------------------------------------------

    for document in documents:
        document_id = document["id"]
        storage_path = document["storage_path"]
        document_type = document["document_type"]

        try:
            # -------------------------------------------------
            # 5a. Download document
            # -------------------------------------------------

            file_bytes = (
                supabase.storage
                .from_(STORAGE_BUCKET)
                .download(storage_path)
            )

            # -------------------------------------------------
            # 5b. Get filename
            # -------------------------------------------------

            filename = storage_path.rsplit(
                "/",
                1,
            )[-1]

            # -------------------------------------------------
            # 5c. Run OCR
            # -------------------------------------------------

            ocr_text = run_ocr(
                file_bytes=file_bytes,
                filename=filename,
            )

            # -------------------------------------------------
            # 5d. Persist OCR result
            # -------------------------------------------------

            (
                supabase.table("documents")
                .update(
                    {
                        "ocr_status": OCRStatus.READABLE.value,
                        "ocr_text": ocr_text,
                    }
                )
                .eq("id", document_id)
                .execute()
            )

            # -------------------------------------------------
            # 5e. Structured extraction
            # -------------------------------------------------

            extraction = (
                extraction_service.extract_document(
                    text=ocr_text,
                    document_type=document_type,
                )
            )

            # -------------------------------------------------
            # 5f. Deterministic validation
            # -------------------------------------------------

            validation_results = validate_extraction(
                extraction=extraction,
                scheme_id=scheme_id,
            )

            # -------------------------------------------------
            # 5g. Persist validation evidence
            # -------------------------------------------------

            _persist_validation_results(
                application_id=application_id,
                validation_results=validation_results,
                supabase=supabase,
            )

            # -------------------------------------------------
            # 5h. Keep extraction for matching
            # -------------------------------------------------

            extracted_documents.append(
                {
                    "document_id": document_id,
                    "document_type": document_type,
                    "extraction": extraction,
                }
            )

        except OCRProcessingError:
            # -------------------------------------------------
            # OCR failed
            # -------------------------------------------------

            any_unreadable = True

            (
                supabase.table("documents")
                .update(
                    {
                        "ocr_status": OCRStatus.UNREADABLE.value,
                    }
                )
                .eq("id", document_id)
                .execute()
            )

        except ExtractionError:
            # -------------------------------------------------
            # OCR succeeded but extraction failed
            # -------------------------------------------------

            (
                supabase.table("documents")
                .update(
                    {
                        "ocr_status": OCRStatus.READABLE.value,
                    }
                )
                .eq("id", document_id)
                .execute()
            )

        except Exception:
            # -------------------------------------------------
            # Unexpected processing failure
            # -------------------------------------------------

            any_unreadable = True

            (
                supabase.table("documents")
                .update(
                    {
                        "ocr_status": OCRStatus.UNREADABLE.value,
                    }
                )
                .eq("id", document_id)
                .execute()
            )

    # ---------------------------------------------------------
    # 6. Cross-document matching
    # ---------------------------------------------------------

    match_results = []

    if len(extracted_documents) >= 2:
        match_results = match_documents(
            extracted_documents
        )

        _persist_match_results(
            application_id=application_id,
            match_results=match_results,
            supabase=supabase,
        )

    # ---------------------------------------------------------
    # 7. Determine match conflict
    # ---------------------------------------------------------

    matching_conflict = has_conflict(
        match_results
    )

    # ---------------------------------------------------------
    # 8. Calculate prototype risk
    # ---------------------------------------------------------

    risk_assessment = calculate_risk(
        match_results=match_results,
        duplicate=False,
        missing_document=False,
        unreadable_document=any_unreadable,
    )

    # ---------------------------------------------------------
    # 9. Persist risk score
    # ---------------------------------------------------------

    (
        supabase.table("applications")
        .update(
            {
                "risk_score": risk_assessment.score,
            }
        )
        .eq("id", str(application_id))
        .execute()
    )

    # ---------------------------------------------------------
    # 10. Determine final application status
    # ---------------------------------------------------------

    if any_unreadable:
        final_status = ApplicationStatus.DEFICIENT.value

    elif matching_conflict:
        # Cross-document conflict requires human review.
        # It is not automatic rejection or fraud.
        final_status = (
            ApplicationStatus.FLAGGED_FOR_REVIEW.value
        )

    else:
        # Full workflow decision comes after risk/workflow
        # integration is completed.
        final_status = ApplicationStatus.PROCESSING.value

    # ---------------------------------------------------------
    # 11. Persist final application status
    # ---------------------------------------------------------

    (
        supabase.table("applications")
        .update(
            {
                "status": final_status,
            }
        )
        .eq("id", str(application_id))
        .execute()
    )