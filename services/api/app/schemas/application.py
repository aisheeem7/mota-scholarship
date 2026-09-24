from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class ApplicationStatus(str, Enum):
    SUBMITTED = "SUBMITTED"
    PROCESSING = "PROCESSING"
    APPROVED = "APPROVED"
    DEFICIENT = "DEFICIENT"
    RESUBMITTED = "RESUBMITTED"
    FLAGGED_FOR_REVIEW = "FLAGGED_FOR_REVIEW"
    ADMIN_REVIEW = "ADMIN_REVIEW"
    REJECTED = "REJECTED"


class SchemeId(str, Enum):
    PRE_MATRIC = "PRE_MATRIC"
    POST_MATRIC = "POST_MATRIC"
    TOP_CLASS = "TOP_CLASS"
    NATIONAL_FELLOWSHIP = "NATIONAL_FELLOWSHIP"
    NATIONAL_OVERSEAS = "NATIONAL_OVERSEAS"


class ApplicationCreate(BaseModel):
    student_id: UUID
    scheme_id: SchemeId


class ApplicationResponse(BaseModel):
    id: UUID
    student_id: UUID
    scheme_id: SchemeId
    status: ApplicationStatus
    risk_score: int | None = Field(default=None, ge=0, le=100)
    created_at: datetime
    updated_at: datetime


class OCRStatus(str, Enum):
    PROCESSING = "PROCESSING"
    READABLE = "READABLE"
    UNREADABLE = "UNREADABLE"
    PARTIALLY_READABLE = "PARTIALLY_READABLE"


class DocumentResponse(BaseModel):
    id: UUID
    application_id: UUID
    document_type: str
    ocr_status: OCRStatus