from uuid import UUID

from supabase import Client

from app.schemas.application import ApplicationStatus, OCRStatus
from app.services.ocr.ocr_service import OCRProcessingError, run_ocr


STORAGE_BUCKET = "application-documents"


def process_application_documents(
    application_id: UUID,
    supabase: Client,
) -> None:
    """
    Process all documents belonging to an application.

    Flow:
    1. Get documents from Supabase.
    2. Download each document from private storage.
    3. Run OCR.
    4. Save OCR result/status.
    5. Update application status.
    """

    # ---------------------------------------------------------
    # 1. Fetch documents for the application
    # ---------------------------------------------------------
    documents_result = (
        supabase.table("documents")
        .select("id, storage_path, ocr_status")
        .eq("application_id", str(application_id))
        .execute()
    )

    documents = documents_result.data or []

    # ---------------------------------------------------------
    # 2. No documents -> application is deficient
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

    # ---------------------------------------------------------
    # 3. Process every document
    # ---------------------------------------------------------
    for document in documents:
        document_id = document["id"]
        storage_path = document["storage_path"]

        try:
            # -------------------------------------------------
            # 3a. Download document from private Supabase storage
            # -------------------------------------------------
            file_bytes = (
                supabase.storage
                .from_(STORAGE_BUCKET)
                .download(storage_path)
            )

            # -------------------------------------------------
            # 3b. Get filename from storage path
            # -------------------------------------------------
            filename = storage_path.rsplit("/", 1)[-1]

            # -------------------------------------------------
            # 3c. Run OCR
            # -------------------------------------------------
            text = run_ocr(
                file_bytes=file_bytes,
                filename=filename,
            )

            # -------------------------------------------------
            # 3d. Save successful OCR result
            # -------------------------------------------------
            (
                supabase.table("documents")
                .update(
                    {
                        "ocr_status": OCRStatus.READABLE.value,
                        "ocr_text": text,
                    }
                )
                .eq("id", document_id)
                .execute()
            )

        except OCRProcessingError:
            # OCR failed for this document
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

        except Exception:
            # Any unexpected processing/storage error
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
    # 4. Update final application status
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