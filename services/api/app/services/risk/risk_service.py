from app.schemas.matching import (
    DocumentMatchResult,
    MatchStatus,
)
from app.schemas.risk import (
    RiskAssessment,
    RiskBand,
)


NAME_MISMATCH_POINTS = 30
DUPLICATE_POINTS = 30
INCOME_INCONSISTENCY_POINTS = 25
MISSING_DOCUMENT_POINTS = 20
UNREADABLE_DOCUMENT_POINTS = 20


def calculate_risk(
    *,
    match_results: list[DocumentMatchResult] | None = None,
    duplicate: bool = False,
    missing_document: bool = False,
    unreadable_document: bool = False,
) -> RiskAssessment:
    """
    Calculate the prototype risk score.

    Risk factors:
    - Name/document mismatch: +30
    - Suspicious duplicate: +30
    - Income inconsistency: +25
    - Missing document: +20
    - Unreadable document: +20
    - Valid document: +0

    Scores are capped at 100.
    """

    match_results = match_results or []

    name_mismatch = any(
        result.match_status == MatchStatus.CONFLICT
        and result.field_name == "STUDENT_NAME"
        for result in match_results
    )

    income_inconsistency = any(
        result.match_status == MatchStatus.CONFLICT
        and result.field_name == "ANNUAL_INCOME"
        for result in match_results
    )

    score = 0

    if name_mismatch:
        score += NAME_MISMATCH_POINTS

    if duplicate:
        score += DUPLICATE_POINTS

    if income_inconsistency:
        score += INCOME_INCONSISTENCY_POINTS

    if missing_document:
        score += MISSING_DOCUMENT_POINTS

    if unreadable_document:
        score += UNREADABLE_DOCUMENT_POINTS

    score = min(score, 100)

    if score <= 20:
        band = RiskBand.LOW
    elif score <= 50:
        band = RiskBand.MEDIUM
    else:
        band = RiskBand.HIGH

    return RiskAssessment(
        score=score,
        band=band,
        name_mismatch=name_mismatch,
        duplicate=duplicate,
        income_inconsistency=income_inconsistency,
        missing_document=missing_document,
        unreadable_document=unreadable_document,
    )