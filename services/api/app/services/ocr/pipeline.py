from uuid import UUID

from supabase import Client

from app.schemas.application import ApplicationStatus, OCRStatus
from app.services.ai.extraction_service import get_extraction_service
from app.services.ai.gpt4o_provider import ExtractionError
from app.services.ocr.ocr_service import OCRProcessingError, run_ocr


STORAGE_BUCKET = "application-documents"


def process_application_documents(
    application_id: UUID,
    supabase: Client,
) -> None:
    """
    Process all documents belonging to an application.

    Flow:
    1. Fetch application documents.
    2. Download each document from private storage.
    3. Run LlamaCloud OCR.
    4. Persist OCR text and OCR status.
    5. Run the configured extraction provider.
    6. Keep structured extraction available for downstream stages.
    7. Update application status.

    The extraction provider can be:
    - mock
    - gpt4o
    """

    # ---------------------------------------------------------
    # 1. Fetch extraction provider
    # ---------------------------------------------------------
    extraction_service = get_extraction_service()

    # ---------------------------------------------------------
    # 2. Fetch documents
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
    # 3. No documents -> DEFICIENT
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
    extractions = []

    # ---------------------------------------------------------
    # 4. Process each document
    # ---------------------------------------------------------
    for document in documents:
        document_id = document["id"]
        storage_path = document["storage_path"]
        document_type = document["document_type"]

        try:
            # -------------------------------------------------
            # 4a. Download document from private storage
            # -------------------------------------------------
            file_bytes = (
                supabase.storage
                .from_(STORAGE_BUCKET)
                .download(storage_path)
            )

            # -------------------------------------------------
            # 4b. Get filename
            # -------------------------------------------------
            filename = storage_path.rsplit("/", 1)[-1]

            # -------------------------------------------------
            # 4c. Run OCR
            # -------------------------------------------------
            ocr_text = run_ocr(
                file_bytes=file_bytes,
                filename=filename,
            )

            # -------------------------------------------------
            # 4d. Persist OCR result
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
            # 4e. Structured extraction
            # -------------------------------------------------
            extraction = extraction_service.extract_document(
                text=ocr_text,
                document_type=document_type,
            )

            # -------------------------------------------------
            # 4f. Keep structured result for downstream stages
            # -------------------------------------------------
            extractions.append(
                {
                    "document_id": document_id,
                    "document_type": document_type,
                    "extraction": extraction,
                }
            )

        except OCRProcessingError:
            # OCR itself failed.
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
            # OCR succeeded, but structured extraction failed.
            # Keep the document marked as READABLE because the
            # document itself was successfully processed by OCR.
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
            # Unexpected storage or processing failure.
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
    # 5. Final application status
    # ---------------------------------------------------------
    final_status = (
        ApplicationStatus.DEFICIENT.value
        if any_unreadable
        else ApplicationStatus.PROCESSING.value
    )

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

    # ---------------------------------------------------------
    # 6. Keep extraction collection available for the next
    #    deterministic validation stage.
    # ---------------------------------------------------------
    #
    # We intentionally do not add another database field here.
    # The next stage will consume these DocumentExtraction objects.
    #
    _ = extractions