from itertools import combinations
import re

from app.schemas.extraction import DocumentExtraction
from app.schemas.matching import (
    DocumentMatchResult,
    MatchStatus,
)


MATCHABLE_FIELDS = (
    "student_name",
    "category",
    "annual_income",
)


def _normalize_text(value: str) -> str:
    """
    Normalize text for deterministic comparison.

    Case, spaces, and punctuation are ignored.
    """

    return re.sub(
        r"[^a-z0-9]+",
        "",
        value.strip().lower(),
    )


def _compare_text(
    left_value: str,
    right_value: str,
) -> tuple[MatchStatus, str, float]:
    """
    Compare two text values.
    """

    left_normalized = _normalize_text(left_value)
    right_normalized = _normalize_text(right_value)

    if left_normalized == right_normalized:
        if (
            left_value.strip().lower()
            == right_value.strip().lower()
        ):
            return (
                MatchStatus.EXACT_MATCH,
                "Values match exactly.",
                1.0,
            )

        return (
            MatchStatus.HARMLESS_VARIANT,
            "Values differ only by case, spacing, or punctuation.",
            1.0,
        )

    return (
        MatchStatus.CONFLICT,
        "Values are inconsistent across the two documents.",
        0.0,
    )


def _compare_income(
    left_value: float,
    right_value: float,
) -> tuple[MatchStatus, str, float]:
    """
    Compare two extracted annual income values.
    """

    if float(left_value) == float(right_value):
        return (
            MatchStatus.EXACT_MATCH,
            "Annual income matches across the two documents.",
            1.0,
        )

    return (
        MatchStatus.CONFLICT,
        "Annual income differs across the two documents.",
        0.0,
    )


def _compare_field(
    field_name: str,
    left_value,
    right_value,
) -> tuple[MatchStatus, str, float]:
    """
    Compare one supported field.
    """

    if field_name in {
        "student_name",
        "category",
    }:
        return _compare_text(
            str(left_value),
            str(right_value),
        )

    if field_name == "annual_income":
        return _compare_income(
            float(left_value),
            float(right_value),
        )

    raise ValueError(
        f"Unsupported matching field: {field_name}"
    )


def match_documents(
    documents: list[dict],
) -> list[DocumentMatchResult]:
    """
    Cross-match extracted information between documents.

    Expected input:

    [
        {
            "document_id": "...",
            "document_type": "...",
            "extraction": DocumentExtraction(...),
        },
        ...
    ]

    Currently matched fields:
    - student_name
    - category
    - annual_income

    Missing fields are skipped rather than treated as conflicts.
    """

    results: list[DocumentMatchResult] = []

    for left_document, right_document in combinations(
        documents,
        2,
    ):
        left_extraction: DocumentExtraction = (
            left_document["extraction"]
        )

        right_extraction: DocumentExtraction = (
            right_document["extraction"]
        )

        for field_name in MATCHABLE_FIELDS:
            left_value = getattr(
                left_extraction,
                field_name,
                None,
            )

            right_value = getattr(
                right_extraction,
                field_name,
                None,
            )

            # Missing evidence is not automatically a mismatch.
            if left_value is None or right_value is None:
                continue

            (
                match_status,
                reasoning,
                similarity,
            ) = _compare_field(
                field_name,
                left_value,
                right_value,
            )

            results.append(
                DocumentMatchResult(
                    left_document_id=str(
                        left_document["document_id"]
                    ),
                    right_document_id=str(
                        right_document["document_id"]
                    ),
                    field_name=field_name.upper(),
                    similarity=similarity,
                    match_status=match_status,
                    reasoning=reasoning,
                )
            )

    return results


def has_conflict(
    results: list[DocumentMatchResult],
) -> bool:
    """
    Return True when at least one comparison is CONFLICT.
    """

    return any(
        result.match_status == MatchStatus.CONFLICT
        for result in results
    )