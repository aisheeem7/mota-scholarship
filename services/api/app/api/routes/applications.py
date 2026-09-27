from datetime import datetime, timezone
import logging
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
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
from app.schemas.validation import ValidationResult
from app.services.ocr.pipeline import process_application_documents
from app.services.validation.validation_service import get_rule_name
from app.services.workflow.workflow_service import (
    transition_application,
)


router = APIRouter()
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".jpg",
    ".jpeg",
    ".png",
}

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
        # Keep database/PostgREST details server-side for debugging.
        # The client receives only the stable public error contract.
        logger.exception(
            "Application creation failed for application_id=%s",
            application_id,
        )
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
# PROCESS APPLICATION
# ============================================================

@router.post(
    "/{application_id}/process",
    response_model=ApplicationResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def process_application(
    application_id: UUID,
    background_tasks: BackgroundTasks,
    supabase: Client = Depends(get_supabase),
):
    # --------------------------------------------------------
    # Verify application exists
    # --------------------------------------------------------

    try:
        application_result = (
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

    if not application_result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    application = application_result.data[0]

    # --------------------------------------------------------
    # Move application into PROCESSING through workflow service
    # --------------------------------------------------------

    current_status = ApplicationStatus(
        application["status"]
    )

    try:
        transition_application(
            application_id=application_id,
            from_status=current_status,
            to_status=ApplicationStatus.PROCESSING,
            reason="Document processing started",
            supabase=supabase,
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Application cannot be processed from its current status",
        )

    # --------------------------------------------------------
    # Update timestamp
    # --------------------------------------------------------

    now = datetime.now(timezone.utc)

    try:
        timestamp_result = (
            supabase.table("applications")
            .update(
                {
                    "updated_at": now.isoformat(),
                }
            )
            .eq("id", str(application_id))
            .execute()
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Application processing could not be started",
        )

    # --------------------------------------------------------
    # Build response reflecting PROCESSING state
    # --------------------------------------------------------

    if timestamp_result.data:
        response_application = timestamp_result.data[0]
    else:
        response_application = {
            **application,
            "status": ApplicationStatus.PROCESSING.value,
            "updated_at": now.isoformat(),
        }

    # --------------------------------------------------------
    # Start OCR pipeline in background
    # --------------------------------------------------------

    background_tasks.add_task(
        process_application_documents,
        application_id,
        supabase,
    )

    return response_application


# ============================================================
# RESUBMIT APPLICATION
# ============================================================

@router.post(
    "/{application_id}/resubmit",
    response_model=ApplicationResponse,
)
def resubmit_application(
    application_id: UUID,
    supabase: Client = Depends(get_supabase),
):
    # --------------------------------------------------------
    # Verify application exists
    # --------------------------------------------------------

    try:
        application_result = (
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

    if not application_result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    application = application_result.data[0]

    current_status = ApplicationStatus(
        application["status"]
    )

    # --------------------------------------------------------
    # DEFICIENT -> RESUBMITTED
    # --------------------------------------------------------

    try:
        transition_application(
            application_id=application_id,
            from_status=current_status,
            to_status=ApplicationStatus.RESUBMITTED,
            reason="Applicant resubmitted application",
            supabase=supabase,
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Application cannot be resubmitted from its current status",
        )

    # --------------------------------------------------------
    # Update timestamp
    # --------------------------------------------------------

    now = datetime.now(timezone.utc)

    try:
        timestamp_result = (
            supabase.table("applications")
            .update(
                {
                    "updated_at": now.isoformat(),
                }
            )
            .eq("id", str(application_id))
            .execute()
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Application resubmission could not be completed",
        )

    # --------------------------------------------------------
    # Build response reflecting RESUBMITTED state
    # --------------------------------------------------------

    if timestamp_result.data:
        response_application = timestamp_result.data[0]
    else:
        response_application = {
            **application,
            "status": ApplicationStatus.RESUBMITTED.value,
            "updated_at": now.isoformat(),
        }

    return response_application


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
# GET VALIDATIONS
# ============================================================

@router.get(
    "/{application_id}/validations",
    response_model=list[ValidationResult],
)
def get_validations(
    application_id: UUID,
    supabase: Client = Depends(get_supabase),
):
    try:
        result = (
            supabase.table("validations")
            .select(
                "rule_id, passed, extracted_value, "
                "expected_condition, reasoning, severity"
            )
            .eq("application_id", str(application_id))
            .execute()
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Validation lookup failed",
        )

    validation_rows = []

    for row in result.data or []:
        validation_rows.append(
            {
                **row,
                "rule_name": get_rule_name(
                    row["rule_id"]
                ),
            }
        )

    return validation_rows


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
                "application_id, status, transaction_id, "
                "amount, created_at"
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

    extension = Path(
        file.filename or ""
    ).suffix.lower()

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
        supabase.storage.from_(
            STORAGE_BUCKET
        ).upload(
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
        try:
            supabase.storage.from_(
                STORAGE_BUCKET
            ).remove(
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
            supabase.storage.from_(
                STORAGE_BUCKET
            ).remove(
                [storage_path]
            )
        except Exception:
            pass

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document upload failed",
        )

    # --------------------------------------------------------
    # Return document response
    # --------------------------------------------------------

    return DocumentResponse(
        id=document_id,
        application_id=application_id,
        document_type=document_type,
        ocr_status=OCRStatus.PROCESSING,
    )