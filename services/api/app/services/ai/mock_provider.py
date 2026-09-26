from app.schemas.extraction import DocumentExtraction
from app.services.ai.extraction_provider import (
    ExtractionError,
    ExtractionProvider,
)


class MockExtractionProvider(ExtractionProvider):
    """
    Deterministic extraction provider for the current demo.

    It returns the same DocumentExtraction schema as GPT-4o.
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

        return DocumentExtraction(
            student_name="Demo Student",
            category="ST",
            annual_income=180000,
            academic_level="X",
            institution="Demo Institution",
            course=None,
            document_number="DEMO-001",
            confidence=1.0,
            reasoning=(
                "Deterministic mock extraction used for the demo "
                "because the real GPT-4o API is currently unavailable."
            ),
            evidence=[
                "Mock extraction fixture",
                f"Document type: {document_type}",
            ],
        )