from openai import OpenAI

from app.core.config import settings
from app.schemas.extraction import DocumentExtraction
from app.services.ai.extraction_provider import (
    ExtractionError,
    ExtractionProvider,
)


class GPT4oExtractionProvider(ExtractionProvider):
    """
    Production GPT-4o extraction provider.

    This remains available even while the current demo uses
    the mock provider.
    """

    def extract(
        self,
        text: str,
        document_type: str,
    ) -> DocumentExtraction:

        if not settings.openai_api_key:
            raise ExtractionError(
                "OPENAI_API_KEY is not configured"
            )

        if not text.strip():
            raise ExtractionError(
                "OCR text is empty"
            )

        try:
            client = OpenAI(
                api_key=settings.openai_api_key
            )

            completion = client.chat.completions.parse(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a document information extraction "
                            "system for a scholarship application. "
                            "Extract only information explicitly present "
                            "in the document. "
                            "Do not invent, guess, or infer missing values. "
                            "Use null when information is absent. "
                            "Eligibility decisions must not be made by you."
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Document type: {document_type}\n\n"
                            "Extract the relevant information from this "
                            "OCR text:\n\n"
                            f"{text}"
                        ),
                    },
                ],
                response_format=DocumentExtraction,
            )

            message = completion.choices[0].message

            if message.parsed is None:
                raise ExtractionError(
                    "GPT-4o returned no structured extraction"
                )

            return message.parsed

        except ExtractionError:
            raise

        except Exception as exc:
            raise ExtractionError(
                "Structured extraction failed"
            ) from exc