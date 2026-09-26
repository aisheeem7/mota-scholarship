from enum import Enum

from pydantic import BaseModel, Field


class AdminReviewDecision(str, Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    REQUEST_RESUBMISSION = "REQUEST_RESUBMISSION"


class AdminReviewRequest(BaseModel):
    decision: AdminReviewDecision
    reason: str = Field(min_length=1)