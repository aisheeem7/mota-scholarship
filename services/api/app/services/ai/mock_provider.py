import re

from app.schemas.extraction import DocumentExtraction
from app.services.ai.extraction_provider import (
    ExtractionError,
    ExtractionProvider,
)


class MockExtractionProvider(ExtractionProvider):
    """
    Deterministic extraction provider for the current demo.

    Extracts structured values from OCR text without requiring an
    external LLM. This preserves the same DocumentExtraction contract
    used by the GPT-4o provider.
    """

    def extract(
        self,
        text: str,
        document_type: str,
    ) -> DocumentExtraction:
        if not text.strip():
            raise ExtractionError("OCR text is empty")

        normalized_text = self._normalize_ocr_text(text)

        student_name = self._extract_field(
            normalized_text,
            [
                "Applicant",
                "Student",
                "Student Name",
                "Name",
            ],
        )

        category = self._extract_field(
            normalized_text,
            [
                "Category",
            ],
        )

        income_text = self._extract_field(
            normalized_text,
            [
                "Annual Family Income",
                "Annual Income",
                "Family Income",
            ],
        )

        annual_income = self._parse_income(income_text)

        academic_level = self._extract_field(
            normalized_text,
            [
                "Academic Level",
                "Class",
                "Standard",
            ],
        )

        institution = self._extract_field(
            normalized_text,
            [
                "Institution",
                "College",
                "University",
            ],
        )

        course = self._extract_field(
            normalized_text,
            [
                "Course",
                "Program",
            ],
        )

        document_number = self._extract_field(
            normalized_text,
            [
                "Certificate No",
                "Certificate Number",
                "Document No",
                "Document Number",
                "ID No",
                "ID Number",
            ],
        )

        missing_fields = []

        if not student_name:
            missing_fields.append("student name")

        if not category:
            missing_fields.append("category")

        if annual_income is None:
            missing_fields.append("annual income")

        # Keep these defaults because not every synthetic document
        # contains every field.
        academic_level = academic_level or "X"
        institution = institution or "Demo Institution"
        document_number = (
            document_number or f"DEMO-{document_type}"
        )

        reasoning = (
            "Deterministic demo extraction performed from OCR text. "
            f"Document type: {document_type}."
        )

        if missing_fields:
            reasoning += (
                " The following fields were not found in the OCR text: "
                + ", ".join(missing_fields)
                + "."
            )

        evidence = [
            "OCR-derived deterministic extraction",
            f"Document type: {document_type}",
        ]

        if student_name:
            evidence.append(
                f"Student name extracted: {student_name}"
            )

        if category:
            evidence.append(
                f"Category extracted: {category}"
            )

        if annual_income is not None:
            evidence.append(
                f"Annual income extracted: "
                f"₹{annual_income:,.0f}"
            )

        return DocumentExtraction(
            student_name=student_name,
            category=category,
            annual_income=annual_income,
            academic_level=academic_level,
            institution=institution,
            course=course,
            document_number=document_number,
            confidence=1.0 if not missing_fields else 0.8,
            reasoning=reasoning,
            evidence=evidence,
        )

    @staticmethod
    def _normalize_ocr_text(text: str) -> str:
        """
        Convert LlamaCloud Markdown/HTML table output into
        predictable line-oriented text.

        Example:

            <td>Category</td>
            <td>ST</td>

        becomes:

            Category
            ST
        """

        normalized = text

        # Convert common table cell boundaries to newlines.
        normalized = re.sub(
            r"</td\s*>",
            "\n",
            normalized,
            flags=re.IGNORECASE,
        )

        normalized = re.sub(
            r"</tr\s*>",
            "\n",
            normalized,
            flags=re.IGNORECASE,
        )

        # Remove remaining HTML tags.
        normalized = re.sub(
            r"<[^>]+>",
            "",
            normalized,
        )

        # Decode common HTML entities.
        normalized = (
            normalized
            .replace("&nbsp;", " ")
            .replace("&amp;", "&")
            .replace("&lt;", "<")
            .replace("&gt;", ">")
        )

        # Normalize whitespace while preserving line structure.
        lines = []

        for line in normalized.splitlines():
            cleaned = re.sub(
                r"\s+",
                " ",
                line,
            ).strip()

            if cleaned:
                lines.append(cleaned)

        return "\n".join(lines)

    @staticmethod
    def _extract_field(
        text: str,
        labels: list[str],
    ) -> str | None:
        """
        Extract the value following a known field label.

        Supports both:

            Category
            ST

        and:

            Category: ST
        """

        lines = text.splitlines()

        for index, line in enumerate(lines):
            normalized_line = line.strip().rstrip(":")

            for label in labels:
                if normalized_line.lower() == label.lower():
                    if index + 1 < len(lines):
                        value = lines[index + 1].strip()

                        if value:
                            return value

                pattern = (
                    rf"^{re.escape(label)}\s*:\s*(.+)$"
                )

                match = re.match(
                    pattern,
                    line,
                    flags=re.IGNORECASE,
                )

                if match:
                    value = match.group(1).strip()

                    if value:
                        return value

        return None

    @staticmethod
    def _parse_income(
        value: str | None,
    ) -> float | None:
        if not value:
            return None

        cleaned = (
            value
            .replace(",", "")
            .replace("₹", "")
            .replace("â‚¹", "")
            .strip()
        )

        match = re.search(
            r"(\d+(?:\.\d+)?)",
            cleaned,
        )

        if not match:
            return None

        try:
            return float(match.group(1))
        except ValueError:
            return None