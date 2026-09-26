from enum import Enum

from pydantic import BaseModel


class ValidationSeverity(str, Enum):
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ValidationResult(BaseModel):
    rule_id: str
    passed: bool | None
    extracted_value: str | None = None
    expected_condition: str | None = None
    reasoning: str | None = None
    severity: ValidationSeverity | None = None