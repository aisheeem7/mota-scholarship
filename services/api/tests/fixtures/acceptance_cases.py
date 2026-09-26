"""Deterministic acceptance fixtures for the OCR/validation pipeline.

IMPORTANT:
    Every DocumentExtraction value in this module is MOCKED TEST OUTPUT.
    These fixtures do not represent live GPT-4o execution. They use the
    exact production DocumentExtraction schema so downstream validation,
    matching, risk, and workflow code can be exercised without an external
    AI dependency.
"""

from dataclasses import dataclass

from app.schemas.application import ApplicationStatus
from app.schemas.extraction import DocumentExtraction


DOCUMENT_TYPES = (
    "INCOME_CERTIFICATE",
    "CASTE_CERTIFICATE",
    "ACADEMIC_RECORD",
    "IDENTITY_DOCUMENT",
)

PRE_MATRIC_REQUIRED_DOCUMENTS = DOCUMENT_TYPES


@dataclass(frozen=True)
class AcceptanceCase:
    """One frozen end-to-end acceptance scenario."""

    case_id: str
    description: str
    scheme_id: str
    expected_status: ApplicationStatus
    expected_risk_score: int
    present_document_types: tuple[str, ...]
    unreadable_document_type: str | None
    extractions_by_type: dict[str, DocumentExtraction]


def _extraction(
    *,
    student_name: str = "Demo Student",
    annual_income: float = 180000,
    category: str = "ST",
    academic_level: str = "X",
    document_number: str,
) -> DocumentExtraction:
    """Build exact-schema mocked extraction output."""

    return DocumentExtraction(
        student_name=student_name,
        category=category,
        annual_income=annual_income,
        academic_level=academic_level,
        institution="Demo Institution",
        course=None,
        document_number=document_number,
        confidence=1.0,
        reasoning=(
            "MOCKED EXTRACTION OUTPUT for deterministic acceptance testing; "
            "not a live GPT-4o result."
        ),
        evidence=[
            "MOCKED_FIXTURE",
            f"document_number={document_number}",
        ],
    )


def _base_extractions(
    *,
    annual_income: float = 180000,
) -> dict[str, DocumentExtraction]:
    return {
        document_type: _extraction(
            annual_income=annual_income,
            document_number=f"MOCK-{document_type}-001",
        )
        for document_type in DOCUMENT_TYPES
    }


def build_acceptance_cases() -> tuple[AcceptanceCase, ...]:
    """Return all five deterministic acceptance scenarios."""

    # A: all four required documents, valid PRE-MATRIC evidence.
    case_a = AcceptanceCase(
        case_id="A_VALID",
        description=(
            "All required documents are present; mocked extraction is "
            "eligible and internally consistent."
        ),
        scheme_id="PRE_MATRIC",
        expected_status=ApplicationStatus.APPROVED,
        expected_risk_score=0,
        present_document_types=PRE_MATRIC_REQUIRED_DOCUMENTS,
        unreadable_document_type=None,
        extractions_by_type=_base_extractions(),
    )

    # B: all documents are present, but the deterministic income rule fails.
    case_b = AcceptanceCase(
        case_id="B_HIGH_INCOME",
        description=(
            "All required documents are present, but annual income exceeds "
            "the configured PRE-MATRIC threshold."
        ),
        scheme_id="PRE_MATRIC",
        expected_status=ApplicationStatus.DEFICIENT,
        expected_risk_score=0,
        present_document_types=PRE_MATRIC_REQUIRED_DOCUMENTS,
        unreadable_document_type=None,
        extractions_by_type=_base_extractions(
            annual_income=320000,
        ),
    )

    # C: one document has a conflicting student name.
    case_c_extractions = _base_extractions()
    case_c_extractions["IDENTITY_DOCUMENT"] = _extraction(
        student_name="Other Student",
        document_number="MOCK-IDENTITY_DOCUMENT-001",
    )

    case_c = AcceptanceCase(
        case_id="C_NAME_MISMATCH",
        description=(
            "All required documents pass deterministic eligibility rules, "
            "but cross-document student-name matching finds a conflict."
        ),
        scheme_id="PRE_MATRIC",
        expected_status=ApplicationStatus.FLAGGED_FOR_REVIEW,
        expected_risk_score=30,
        present_document_types=PRE_MATRIC_REQUIRED_DOCUMENTS,
        unreadable_document_type=None,
        extractions_by_type=case_c_extractions,
    )

    # D: OCR for one present document is deterministically marked unreadable.
    case_d = AcceptanceCase(
        case_id="D_UNREADABLE",
        description=(
            "All required documents are uploaded, but the income certificate "
            "cannot be read by the OCR stage."
        ),
        scheme_id="PRE_MATRIC",
        expected_status=ApplicationStatus.DEFICIENT,
        expected_risk_score=20,
        present_document_types=PRE_MATRIC_REQUIRED_DOCUMENTS,
        unreadable_document_type="INCOME_CERTIFICATE",
        extractions_by_type=_base_extractions(),
    )

    # E: one required document is not uploaded.
    case_e = AcceptanceCase(
        case_id="E_MISSING_DOCUMENT",
        description=(
            "The caste certificate is missing, so required-document "
            "validation fails before final approval."
        ),
        scheme_id="PRE_MATRIC",
        expected_status=ApplicationStatus.DEFICIENT,
        expected_risk_score=20,
        present_document_types=(
            "INCOME_CERTIFICATE",
            "ACADEMIC_RECORD",
            "IDENTITY_DOCUMENT",
        ),
        unreadable_document_type=None,
        extractions_by_type=_base_extractions(),
    )

    return (
        case_a,
        case_b,
        case_c,
        case_d,
        case_e,
    )


ACCEPTANCE_CASES = build_acceptance_cases()
