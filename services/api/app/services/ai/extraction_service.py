from app.core.config import settings
from app.schemas.extraction import DocumentExtraction
from app.services.ai.extraction_provider import (
    ExtractionError,
    ExtractionProvider,
)
from app.services.ai.gpt4o_provider import GPT4oExtractionProvider
from app.services.ai.mock_provider import MockExtractionProvider


class ExtractionService:
    """
    Provider-independent extraction service.

    Downstream code interacts only with this service.
    """

    def __init__(self, provider: ExtractionProvider):
        self.provider = provider

    def extract_document(
        self,
        text: str,
        document_type: str,
    ) -> DocumentExtraction:

        if not text.strip():
            raise ExtractionError(
                "OCR text is empty"
            )

        return self.provider.extract(
            text=text,
            document_type=document_type,
        )


def get_extraction_service() -> ExtractionService:
    """
    Select the configured provider.
    """

    provider_name = settings.extraction_provider.lower()

    if provider_name == "gpt4o":
        provider = GPT4oExtractionProvider()

    elif provider_name == "mock":
        provider = MockExtractionProvider()

    else:
        raise ValueError(
            f"Unsupported extraction provider: {provider_name}"
        )

    return ExtractionService(provider)


def extract_document(
    text: str,
    document_type: str,
) -> DocumentExtraction:
    """
    Backward-compatible convenience function.
    """

    service = get_extraction_service()

    return service.extract_document(
        text=text,
        document_type=document_type,
    )