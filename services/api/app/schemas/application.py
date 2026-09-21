from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ApplicationStatus(str, Enum):
    SUBMITTED = "SUBMITTED"
    PROCESSING = "PROCESSING"
    APPROVED = "APPROVED"
    DEFICIENT = "DEFICIENT"
    RESUBMITTED = "RESUBMITTED"
    FLAGGED_FOR_REVIEW = "FLAGGED_FOR_REVIEW"


class ApplicationCreate(BaseModel):
    student_name: str = Field(min_length=2, max_length=120)
    scheme_id: str


class ApplicationResponse(BaseModel):
    id: str
    student_name: str
    scheme_id: str
    status: ApplicationStatus
    created_at: datetime


class DocumentProcessingStatus(str, Enum):
    SUBMITTED = "SUBMITTED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class DocumentResponse(BaseModel):
    id: str
    application_id: str
    document_type: str
    processing_status: DocumentProcessingStatus
