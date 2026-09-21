from pydantic import BaseModel


class ValidationResult(BaseModel):
    passed: bool
    rule_id: str
    rule_name: str
    extracted_value: str | None = None
    expected_condition: str
    reasoning: str
    severity: str
