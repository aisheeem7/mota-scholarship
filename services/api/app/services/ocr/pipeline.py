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

    The student_document_matches table stores:
    - left_document_id
    - right_document_id
    - field_name
    - similarity
    - match_status
    - reasoning
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
    12. Route conflicts to FLAGGED_FOR_REVIEW.
    13. Keep unreadable cases DEFICIENT.

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
            # 5h. Keep successful extraction for matching
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

        # -----------------------------------------------------
        # 6a. Persist match evidence
        # -----------------------------------------------------

        _persist_match_results(
            application_id=application_id,
            match_results=match_results,
            supabase=supabase,
        )

    # ---------------------------------------------------------
    # 7. Determine whether matching found a conflict
    # ---------------------------------------------------------

    matching_conflict = has_conflict(
        match_results
    )

    # ---------------------------------------------------------
    # 8. Final application status
    # ---------------------------------------------------------

    if any_unreadable:
        final_status = ApplicationStatus.DEFICIENT.value

    elif matching_conflict:
        # -----------------------------------------------------
        # Cross-document mismatch requires human review.
        # It is NOT treated as automatic rejection or fraud.
        # -----------------------------------------------------
        final_status = (
            ApplicationStatus.FLAGGED_FOR_REVIEW.value
        )

    else:
        # Validation failures, risk scoring, and full workflow
        # transitions will be handled by the next stages.
        final_status = ApplicationStatus.PROCESSING.value

    # ---------------------------------------------------------
    # 9. Persist application status
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