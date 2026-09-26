from pathlib import Path
from uuid import UUID, uuid4
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from supabase import Client

from app.core.supabase_client import get_supabase
from app.schemas.application import (
    ApplicationCreate,
    ApplicationResponse,
    ApplicationStatus,
    DocumentResponse,
    DocumentType,
    OCRStatus,
)
from app.schemas.dbt import DBTTransactionResponse

router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
}

STORAGE_BUCKET = "application-documents"


# ============================================================
# CREATE APPLICATION
# ============================================================

@router.post(
    "",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_application(
    payload: ApplicationCreate,
    supabase: Client = Depends(get_supabase),
):
    application_id = uuid4()
    now = datetime.now(timezone.utc)

    application_data = {
        "id": str(application_id),
        "student_id": str(payload.student_id),
        "scheme_id": payload.scheme_id.value,
        "status": ApplicationStatus.SUBMITTED.value,
        "risk_score": None,
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
    }

    try:
        result = (
            supabase.table("applications")
            .insert(application_data)
            .execute()
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Application creation failed",
        )

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Application creation failed",
        )

    return result.data[0]


# ============================================================
# GET APPLICATION
# ============================================================

@router.get(
    "/{application_id}",
    response_model=ApplicationResponse,
)
def get_application(
    application_id: UUID,
    supabase: Client = Depends(get_supabase),
):
    try:
        result = (
            supabase.table("applications")
            .select(
                "id, student_id, scheme_id, status, "
                "risk_score, created_at, updated_at"
            )
            .eq("id", str(application_id))
            .limit(1)
            .execute()
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Application lookup failed",
        )

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    return result.data[0]


# ============================================================
# GET DBT TRANSACTION
# ============================================================

@router.get(
    "/{application_id}/dbt-transaction",
    response_model=DBTTransactionResponse,
)
def get_dbt_transaction(
    application_id: UUID,
    supabase: Client = Depends(get_supabase),
):
    try:
        result = (
            supabase.table("dbt_mock_transactions")
            .select(
                "application_id, status, transaction_id, amount, created_at"
            )
            .eq("application_id", str(application_id))
            .limit(1)
            .execute()
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="DBT transaction lookup failed",
        )

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="DBT transaction not found",
        )

    return result.data[0]


# ============================================================
# UPLOAD DOCUMENT
# ============================================================

@router.post(
    "/{application_id}/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_document(
    application_id: UUID,
    document_type: DocumentType = Form(...),
    file: UploadFile = File(...),
    supabase: Client = Depends(get_supabase),
):
    # --------------------------------------------------------
    # Validate extension
    # --------------------------------------------------------

    extension = Path(file.filename or "").suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type",
        )

    # --------------------------------------------------------
    # Validate content type
    # --------------------------------------------------------

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported content type",
        )

    # --------------------------------------------------------
    # Verify application exists
    # --------------------------------------------------------

    try:
        application_result = (
            supabase.table("applications")
            .select("id")
            .eq("id", str(application_id))
            .limit(1)
            .execute()
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Application lookup failed",
        )

    if not application_result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    # --------------------------------------------------------
    # Generate document ID and storage path
    # --------------------------------------------------------

    document_id = uuid4()

    storage_path = (
        f"applications/{application_id}/"
        f"{document_id}-{document_type.value}{extension}"
    )

    # --------------------------------------------------------
    # Read file
    # --------------------------------------------------------

    file_bytes = await file.read()

    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty file",
        )

    # --------------------------------------------------------
    # Upload file + insert document metadata
    # --------------------------------------------------------

    try:
        supabase.storage.from_(STORAGE_BUCKET).upload(
            storage_path,
            file_bytes,
            {
                "content-type": file.content_type,
                "upsert": False,
            },
        )

        document_result = (
            supabase.table("documents")
            .insert(
                {
                    "id": str(document_id),
                    "application_id": str(application_id),
                    "document_type": document_type.value,
                    "storage_path": storage_path,
                    "ocr_status": OCRStatus.PROCESSING.value,
                }
            )
            .execute()
        )

    except Exception:
        # Clean up storage if database insertion fails
        try:
            supabase.storage.from_(STORAGE_BUCKET).remove(
                [storage_path]
            )
        except Exception:
            pass

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document upload failed",
        )

    if not document_result.data:
        try:
            supabase.storage.from_(STORAGE_BUCKET).remove(
                [storage_path]
            )
        except Exception:
            pass

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document upload failed",
        )

    # --------------------------------------------------------
    # Return frozen document response
    # --------------------------------------------------------

    return DocumentResponse(
        id=document_id,
        application_id=application_id,
        document_type=document_type,
        ocr_status=OCRStatus.PROCESSING,
    )