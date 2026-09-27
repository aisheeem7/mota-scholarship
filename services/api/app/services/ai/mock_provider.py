from app.schemas.extraction import DocumentExtraction
from app.services.ai.extraction_provider import (
    ExtractionError,
    ExtractionProvider,
)


class MockExtractionProvider(ExtractionProvider):
    """
    Deterministic extraction provider for the current demo and E2E fixtures.

    Normal demo text returns the baseline synthetic applicant.
    Explicit E2E fixture markers alter only the mocked extraction result.

    All values produced by this provider are MOCKED OUTPUT, never live AI
    results.
    """

    def extract(
        self,
        text: str,
        document_type: str,
    ) -> DocumentExtraction:

        if not text.strip():
            raise ExtractionError(
                "OCR text is empty"
            )

        normalized_text = text.upper()

        if "E2E_MALFORMED_EXTRACTION" in normalized_text:
            raise ExtractionError(
                "Deterministic malformed extraction fixture"
            )

        student_name = "Demo Student"
        annual_income = 180000
        academic_level = "X"

        if "E2E_CASE_B_HIGH_INCOME" in normalized_text:
            annual_income = 320000

        if (
            "E2E_CASE_C_NAME_MISMATCH" in normalized_text
            and document_type == "IDENTITY_DOCUMENT"
        ):
            student_name = "Other Student"

        if "E2E_MISSING_INCOME" in normalized_text:
            annual_income = None

        document_number = f"DEMO-{document_type}-001"

        return DocumentExtraction(
            student_name=student_name,
            category="ST",
            annual_income=annual_income,
            academic_level=academic_level,
            institution="Demo Institution",
            course=None,
            document_number=document_number,
            confidence=1.0,
            reasoning=(
                "MOCKED EXTRACTION OUTPUT for the current demo/E2E path; "
                "not a live GPT-4o result."
            ),
            evidence=[
                "MOCKED_FIXTURE",
                f"Document type: {document_type}",
            ],
        )
