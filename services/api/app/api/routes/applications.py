from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status

from app.schemas.application import (
    ApplicationCreate,
    ApplicationResponse,
    ApplicationStatus,
)

router = APIRouter()

applications: dict[str, ApplicationResponse] = {}


@router.post(
    "",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_application(payload: ApplicationCreate):
    application_id = str(uuid4())

    application = ApplicationResponse(
        id=application_id,
        student_name=payload.student_name,
        scheme_id=payload.scheme_id,
        status=ApplicationStatus.SUBMITTED,
        created_at=datetime.now(timezone.utc),
    )

    applications[application_id] = application
    return application


@router.get(
    "/{application_id}",
    response_model=ApplicationResponse,
)
def get_application(application_id: str):
    application = applications.get(application_id)

    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    return application
