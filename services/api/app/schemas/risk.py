from enum import Enum

from pydantic import BaseModel, Field


class RiskBand(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class RiskAssessment(BaseModel):
    score: int = Field(
        ge=0,
        le=100,
    )
    band: RiskBand

    name_mismatch: bool = False
    duplicate: bool = False
    income_inconsistency: bool = False
    missing_document: bool = False
    unreadable_document: bool = False