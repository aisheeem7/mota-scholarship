from pydantic import BaseModel, Field


class DocumentExtraction(BaseModel):
    """
    Structured information extracted from a scholarship document.
    """

    student_name: str | None = None

    category: str | None = None

    annual_income: float | None = Field(
        default=None,
        ge=0,
    )

    academic_level: str | None = None

    institution: str | None = None

    course: str | None = None

    document_number: str | None = None

    confidence: float = Field(
        ge=0,
        le=1,
    )

    reasoning: str | None = None

    evidence: list[str] = Field(
        default_factory=list,
    )