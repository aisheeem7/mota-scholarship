from abc import ABC, abstractmethod

from app.schemas.extraction import DocumentExtraction


class ExtractionError(Exception):
    """Raised when document extraction fails."""


class ExtractionProvider(ABC):
    """
    Common interface for all extraction providers.

    Both mock and GPT-4o providers return the same
    DocumentExtraction Pydantic model.
    """

    @abstractmethod
    def extract(
        self,
        text: str,
        document_type: str,
    ) -> DocumentExtraction:
        raise NotImplementedError