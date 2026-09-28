from uuid import UUID

from supabase import Client

from app.schemas.application import (
    ApplicationStatus,
    OCRStatus,
)
from app.schemas.extraction import DocumentExtraction
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
from app.services.risk.duplicate_service import (
    has_duplicate_application,
)
from app.services.risk.risk_service import (
    calculate_risk,
)
from app.services.validation.validation_service import (
    validate_extraction,
    validate_required_documents,
)
from app.services.workflow.workflow_service import (
    transition_application,
)


STORAGE_BUCKET = "application-documents"


# ============================================================
# VALIDATION PERSISTENCE
# ============================================================


def _persist_validation_results(
    application_id: UUID,
    validation_results,
    supabase: Client,
) -> None:
    """
    Persist deterministic validation results.

    The database stores rule_id rather than rule_name.
    rule_name is derived by the validation API.
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


# ============================================================
# MATCHING PERSISTENCE
# ============================================================


def _persist_match_results(
    application_id: UUID,
    match_results,
    supabase: Client,
) -> None:
    """
    Persist cross-document matching results in a single batch insert.

    Batch insertion reduces repeated PostgREST connections and keeps
    the matching persistence operation atomic at the application level.
    """

    if not match_results:
        return

    match_rows = []

    for result in match_results:
        match_rows.append(
            {
                "application_id": str(application_id),
                "left_document_id": result.left_document_id,
                "right_document_id": result.right_document_id,
                "field_name": result.field_name,
                "similarity": result.similarity,
                "match_status": result.match_status.value,
                "reasoning": result.reasoning,
            }
        )

    supabase.table(
        "student_document_matches"
    ).insert(
        match_rows
    ).execute()


# ============================================================
# APPLICATION-LEVEL EVIDENCE AGGREGATION
# ============================================================


def _build_application_extraction(
    extracted_documents: list[dict],
) -> DocumentExtraction:
    """
    Build one consolidated evidence object for application-level
    deterministic eligibility validation.

    Individual document extractions remain available for:
    - auditability
    - OCR/extraction display
    - cross-document matching
    - AI reasoning

    This consolidated object is used only by the deterministic
    scheme validation engine.

    Eligibility evidence is sourced explicitly from the document
    type that is authoritative for that field.

    Current prototype source mapping:

        student_name
            IDENTITY_DOCUMENT
            ACADEMIC_RECORD
            INCOME_CERTIFICATE
            CASTE_CERTIFICATE

        category
            CASTE_CERTIFICATE
            IDENTITY_DOCUMENT

        annual_income
            INCOME_CERTIFICATE

        academic_level
            ACADEMIC_RECORD

        institution
            ACADEMIC_RECORD

        course
            ACADEMIC_RECORD

        document_number
            IDENTITY_DOCUMENT
            CASTE_CERTIFICATE
            INCOME_CERTIFICATE
            ACADEMIC_RECORD
    """

    # --------------------------------------------------------
    # Explicit evidence-source priority
    # --------------------------------------------------------

    field_priority = {
        "student_name": [
            "IDENTITY_DOCUMENT",
            "ACADEMIC_RECORD",
            "INCOME_CERTIFICATE",
            "CASTE_CERTIFICATE",
        ],
        "category": [
            "CASTE_CERTIFICATE",
            "IDENTITY_DOCUMENT",
        ],
        "annual_income": [
            "INCOME_CERTIFICATE",
        ],
        "academic_level": [
            "ACADEMIC_RECORD",
        ],
        "institution": [
            "ACADEMIC_RECORD",
        ],
        "course": [
            "ACADEMIC_RECORD",
        ],
        "document_number": [
            "IDENTITY_DOCUMENT",
            "CASTE_CERTIFICATE",
            "INCOME_CERTIFICATE",
            "ACADEMIC_RECORD",
        ],
    }

    # --------------------------------------------------------
    # Index successful extractions by document type
    # --------------------------------------------------------

    by_type: dict[str, DocumentExtraction] = {}

    for item in extracted_documents:
        document_type = item["document_type"]
        extraction = item["extraction"]

        by_type[document_type] = extraction

    # --------------------------------------------------------
    # Resolve a field only from its configured source documents
    # --------------------------------------------------------

    def first_value(field_name: str):
        for document_type in field_priority[field_name]:
            extraction = by_type.get(document_type)

            if extraction is None:
                continue

            value = getattr(
                extraction,
                field_name,
                None,
            )

            if value is None:
                continue

            if isinstance(value, str) and not value.strip():
                continue

            return value

        return None

    # --------------------------------------------------------
    # Preserve evidence with document source
    # --------------------------------------------------------

    evidence: list[str] = []

    for item in extracted_documents:
        document_type = item["document_type"]
        extraction = item["extraction"]

        for evidence_item in extraction.evidence:
            evidence.append(
                f"{document_type}: {evidence_item}"
            )

    # --------------------------------------------------------
    # Consolidated confidence
    # --------------------------------------------------------

    confidence_values = [
        item["extraction"].confidence
        for item in extracted_documents
    ]

    confidence = (
        sum(confidence_values) / len(confidence_values)
        if confidence_values
        else 0.0
    )

    # --------------------------------------------------------
    # Consolidated reasoning
    # --------------------------------------------------------

    reasoning_parts: list[str] = []

    for item in extracted_documents:
        document_type = item["document_type"]
        extraction = item["extraction"]

        if extraction.reasoning:
            reasoning_parts.append(
                f"{document_type}: {extraction.reasoning}"
            )

    # --------------------------------------------------------
    # Return normalized application evidence
    # --------------------------------------------------------

    return DocumentExtraction(
        student_name=first_value("student_name"),
        category=first_value("category"),
        annual_income=first_value("annual_income"),
        academic_level=first_value("academic_level"),
        institution=first_value("institution"),
        course=first_value("course"),
        document_number=first_value("document_number"),
        confidence=confidence,
        reasoning=(
            " ".join(reasoning_parts)
            if reasoning_parts
            else None
        ),
        evidence=evidence,
    )


# ============================================================
# MAIN APPLICATION PROCESSING PIPELINE
# ============================================================


def process_application_documents(
    application_id: UUID,
    supabase: Client,
) -> None:
    """
    Process all documents belonging to an application.

    Flow:

    1. Fetch application and scheme.
    2. Detect duplicate application.
    3. Move SUBMITTED/RESUBMITTED -> PROCESSING.
    4. Fetch application documents.
    5. Validate required documents from prototype configuration.
    6. Download each document from private storage.
    7. Run LlamaCloud OCR.
    8. Persist OCR result.
    9. Run configured extraction provider.
    10. Aggregate application-level evidence.
    11. Run deterministic eligibility validation once.
    12. Cross-match extracted values between documents.
    13. Persist matching results.
    14. Calculate prototype risk score.
    15. Persist risk score.
    16. Move PROCESSING -> final workflow state.

    Required-document mappings are prototype configuration
    and are not presented as complete official MoTA rules.

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
        .select(
            "id, student_id, scheme_id, status"
        )
        .eq(
            "id",
            str(application_id),
        )
        .limit(1)
        .execute()
    )

    application_rows = application_result.data or []

    if not application_rows:
        return

    application = application_rows[0]

    student_id = application["student_id"]
    scheme_id = application["scheme_id"]

    current_status = ApplicationStatus(
        application["status"]
    )

    # ---------------------------------------------------------
    # 2. Detect duplicate application
    # ---------------------------------------------------------

    duplicate_detected = has_duplicate_application(
        student_id=student_id,
        scheme_id=scheme_id,
        application_id=application_id,
        supabase=supabase,
    )

    # ---------------------------------------------------------
    # 3. Ensure processing state
    # ---------------------------------------------------------

    if current_status in {
        ApplicationStatus.SUBMITTED,
        ApplicationStatus.RESUBMITTED,
    }:
        transition_application(
            application_id=application_id,
            from_status=current_status,
            to_status=ApplicationStatus.PROCESSING,
            reason="Document processing started",
            supabase=supabase,
        )

    elif current_status != ApplicationStatus.PROCESSING:
        return

    # ---------------------------------------------------------
    # 4. Fetch configured extraction provider
    # ---------------------------------------------------------

    extraction_service = get_extraction_service()

    # ---------------------------------------------------------
    # 5. Fetch documents
    # ---------------------------------------------------------

    documents_result = (
        supabase.table("documents")
        .select(
            "id, storage_path, document_type, ocr_status"
        )
        .eq(
            "application_id",
            str(application_id),
        )
        .execute()
    )

    documents = documents_result.data or []

    # ---------------------------------------------------------
    # 6. Required-document validation
    # ---------------------------------------------------------

    uploaded_document_types = [
        document["document_type"]
        for document in documents
    ]

    required_document_result = (
        validate_required_documents(
            scheme_id=scheme_id,
            uploaded_document_types=uploaded_document_types,
        )
    )

    _persist_validation_results(
        application_id=application_id,
        validation_results=[
            required_document_result,
        ],
        supabase=supabase,
    )

    missing_document = (
        required_document_result.passed is False
    )

    # ---------------------------------------------------------
    # 7. No documents -> DEFICIENT
    # ---------------------------------------------------------

    if not documents:
        risk_assessment = calculate_risk(
            match_results=[],
            duplicate=duplicate_detected,
            missing_document=True,
            unreadable_document=False,
        )

        (
            supabase.table("applications")
            .update(
                {
                    "risk_score": risk_assessment.score,
                }
            )
            .eq(
                "id",
                str(application_id),
            )
            .execute()
        )

        transition_application(
            application_id=application_id,
            from_status=ApplicationStatus.PROCESSING,
            to_status=ApplicationStatus.DEFICIENT,
            reason=(
                "Required application documents "
                "are missing"
            ),
            supabase=supabase,
        )

        return

    any_unreadable = False
    validation_failed = False

    # Each successfully extracted document is stored exactly once.
    #
    # This collection is used for:
    # - application-level evidence aggregation
    # - cross-document matching
    # - auditability
    extracted_documents = []

    # ---------------------------------------------------------
    # 8. Process every document
    # ---------------------------------------------------------

    for document in documents:
        document_id = document["id"]
        storage_path = document["storage_path"]
        document_type = document["document_type"]

        # -----------------------------------------------------
        # 8a. Download document
        # 8b. Get filename
        # 8c. Run OCR
        # -----------------------------------------------------

        try:
            file_bytes = (
                supabase.storage
                .from_(STORAGE_BUCKET)
                .download(storage_path)
            )

            filename = storage_path.rsplit(
                "/",
                1,
            )[-1]

            ocr_text = run_ocr(
                file_bytes=file_bytes,
                filename=filename,
            )

        except OCRProcessingError:
            # -------------------------------------------------
            # OCR actually failed.
            #
            # This is the only OCR-specific failure path that
            # marks the document UNREADABLE.
            # -------------------------------------------------

            any_unreadable = True

            (
                supabase.table("documents")
                .update(
                    {
                        "ocr_status": OCRStatus.UNREADABLE.value,
                    }
                )
                .eq(
                    "id",
                    document_id,
                )
                .execute()
            )

            continue

        except Exception:
            # -------------------------------------------------
            # Storage/download/system failure.
            #
            # Do NOT label this document as OCR unreadable.
            # OCR was not necessarily attempted or failed.
            # -------------------------------------------------

            validation_failed = True

            continue

        # -----------------------------------------------------
        # 8d. Persist successful OCR result
        # -----------------------------------------------------

        (
            supabase.table("documents")
            .update(
                {
                    "ocr_status": OCRStatus.READABLE.value,
                    "ocr_text": ocr_text,
                }
            )
            .eq(
                "id",
                document_id,
            )
            .execute()
        )

        try:
            # -------------------------------------------------
            # 8e. Structured extraction
            # -------------------------------------------------

            extraction = (
                extraction_service.extract_document(
                    text=ocr_text,
                    document_type=document_type,
                )
            )

            # -------------------------------------------------
            # 8f. Keep extraction for application-level
            #     validation and cross-document matching
            #
            # IMPORTANT:
            # Append exactly once.
            # -------------------------------------------------

            extracted_documents.append(
                {
                    "document_id": document_id,
                    "document_type": document_type,
                    "extraction": extraction,
                }
            )

        except ExtractionError:
            # -------------------------------------------------
            # OCR succeeded but extraction failed.
            # The document remains READABLE because OCR itself
            # succeeded.
            # -------------------------------------------------

            validation_failed = True

            (
                supabase.table("documents")
                .update(
                    {
                        "ocr_status": OCRStatus.READABLE.value,
                    }
                )
                .eq(
                    "id",
                    document_id,
                )
                .execute()
            )

        except Exception:
            # -------------------------------------------------
            # Downstream processing failed after OCR.
            #
            # Preserve READABLE because OCR succeeded.
            # Do not misclassify the document as UNREADABLE.
            # -------------------------------------------------

            validation_failed = True

            (
                supabase.table("documents")
                .update(
                    {
                        "ocr_status": OCRStatus.READABLE.value,
                    }
                )
                .eq(
                    "id",
                    document_id,
                )
                .execute()
            )

    # ---------------------------------------------------------
    # 9. Application-level deterministic validation
    # ---------------------------------------------------------
    #
    # All documents have now been OCR'd and structurally
    # extracted.
    #
    # Eligibility rules operate on the consolidated application
    # evidence rather than independently on every document.
    #
    # This prevents unrelated documents from generating
    # "Not evaluable" copies of rules they do not contain.
    # ---------------------------------------------------------

    application_validation_results = []

    if extracted_documents:
        application_extraction = (
            _build_application_extraction(
                extracted_documents
            )
        )

        application_validation_results = (
            validate_extraction(
                extraction=application_extraction,
                scheme_id=scheme_id,
            )
        )

        _persist_validation_results(
            application_id=application_id,
            validation_results=application_validation_results,
            supabase=supabase,
        )

        # Every result here is an application-level eligibility
        # rule.
        #
        # True  -> rule passed
        # False -> rule failed
        # None  -> required evidence was not evaluable
        #
        # Neither False nor None can result in approval.

        if any(
            result.passed is not True
            for result in application_validation_results
        ):
            validation_failed = True

    # ---------------------------------------------------------
    # 10. Cross-document matching
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
    # 11. Determine matching conflict
    # ---------------------------------------------------------

    matching_conflict = has_conflict(
        match_results
    )

    # ---------------------------------------------------------
    # 12. Calculate prototype risk
    # ---------------------------------------------------------

    risk_assessment = calculate_risk(
        match_results=match_results,
        duplicate=duplicate_detected,
        missing_document=missing_document,
        unreadable_document=any_unreadable,
    )

    # ---------------------------------------------------------
    # 13. Persist risk score
    # ---------------------------------------------------------

    (
        supabase.table("applications")
        .update(
            {
                "risk_score": risk_assessment.score,
            }
        )
        .eq(
            "id",
            str(application_id),
        )
        .execute()
    )

    # ---------------------------------------------------------
    # 14. Determine final workflow state
    # ---------------------------------------------------------

    if (
        any_unreadable
        or validation_failed
        or missing_document
    ):
        final_status = ApplicationStatus.DEFICIENT
        reason = (
            "Application requires document or "
            "eligibility corrections"
        )

    elif matching_conflict:
        final_status = (
            ApplicationStatus.FLAGGED_FOR_REVIEW
        )
        reason = (
            "Cross-document inconsistency requires "
            "human review"
        )

    else:
        final_status = ApplicationStatus.APPROVED
        reason = (
            "Documents processed and deterministic "
            "validation completed successfully"
        )

    # ---------------------------------------------------------
    # 15. Persist final workflow transition
    # ---------------------------------------------------------

    transition_application(
        application_id=application_id,
        from_status=ApplicationStatus.PROCESSING,
        to_status=final_status,
        reason=reason,
        supabase=supabase,
    )