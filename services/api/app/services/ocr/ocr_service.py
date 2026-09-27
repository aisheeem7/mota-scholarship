from pathlib import Path
from tempfile import NamedTemporaryFile

from llama_cloud import LlamaCloud

from app.core.config import settings


class OCRProcessingError(Exception):
    pass


def run_ocr(
    file_bytes: bytes,
    filename: str,
) -> str:
    if not settings.llama_cloud_api_key:
        raise OCRProcessingError(
            "LLAMA_CLOUD_API_KEY is not configured"
        )

    suffix = Path(filename).suffix.lower() or ".pdf"

    try:
        client = LlamaCloud(
            api_key=settings.llama_cloud_api_key
        )

        with NamedTemporaryFile(
            suffix=suffix,
            delete=False,
        ) as temp_file:
            temp_file.write(file_bytes)
            temp_path = temp_file.name

        try:
            uploaded_file = client.files.create(
                file=temp_path,
                purpose="parse",
            )

            result = client.parsing.parse(
                file_id=uploaded_file.id,
                tier="agentic",
                version="latest",
                expand=["markdown"],
            )

            pages = getattr(
                getattr(result, "markdown", None),
                "pages",
                [],
            )

            text_parts = []

            for page in pages:
                page_text = getattr(page, "markdown", None)

                if page_text:
                    text_parts.append(page_text)

            text = "\n\n".join(text_parts).strip()

            if not text:
                raise OCRProcessingError(
                    "OCR returned no readable text"
                )

            return text

        finally:
            Path(temp_path).unlink(
                missing_ok=True
            )

    except OCRProcessingError:
        raise

    except Exception as exc:
        raise OCRProcessingError(
            "OCR processing failed"
        ) from exc