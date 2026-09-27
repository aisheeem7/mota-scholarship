from app.schemas.matching import (
    DocumentMatchResult,
    MatchStatus,
)
from app.schemas.risk import RiskBand
from app.services.risk.risk_service import calculate_risk


def make_match(
    field_name,
    match_status=MatchStatus.EXACT_MATCH,
):
    return DocumentMatchResult(
        left_document_id="doc-1",
        right_document_id="doc-2",
        field_name=field_name,
        similarity=(
            1.0
            if match_status != MatchStatus.CONFLICT
            else 0.0
        ),
        match_status=match_status,
        reasoning="Test match result",
    )


def test_valid_case_has_zero_risk():
    result = calculate_risk()

    assert result.score == 0
    assert result.band == RiskBand.LOW
    assert result.name_mismatch is False
    assert result.duplicate is False
    assert result.income_inconsistency is False
    assert result.missing_document is False
    assert result.unreadable_document is False


def test_name_mismatch_adds_30_points():
    result = calculate_risk(
        match_results=[
            make_match(
                "STUDENT_NAME",
                MatchStatus.CONFLICT,
            )
        ]
    )

    assert result.score == 30
    assert result.band == RiskBand.MEDIUM
    assert result.name_mismatch is True


def test_duplicate_adds_30_points():
    result = calculate_risk(
        duplicate=True,
    )

    assert result.score == 30
    assert result.band == RiskBand.MEDIUM
    assert result.duplicate is True


def test_income_inconsistency_adds_25_points():
    result = calculate_risk(
        match_results=[
            make_match(
                "ANNUAL_INCOME",
                MatchStatus.CONFLICT,
            )
        ]
    )

    assert result.score == 25
    assert result.band == RiskBand.MEDIUM
    assert result.income_inconsistency is True


def test_missing_document_adds_20_points():
    result = calculate_risk(
        missing_document=True,
    )

    assert result.score == 20
    assert result.band == RiskBand.LOW
    assert result.missing_document is True


def test_unreadable_document_adds_20_points():
    result = calculate_risk(
        unreadable_document=True,
    )

    assert result.score == 20
    assert result.band == RiskBand.LOW
    assert result.unreadable_document is True


def test_multiple_factors_reach_high_band():
    result = calculate_risk(
        match_results=[
            make_match(
                "STUDENT_NAME",
                MatchStatus.CONFLICT,
            ),
            make_match(
                "ANNUAL_INCOME",
                MatchStatus.CONFLICT,
            ),
        ]
    )

    assert result.score == 55
    assert result.band == RiskBand.HIGH
    assert result.name_mismatch is True
    assert result.income_inconsistency is True


def test_score_is_capped_at_100():
    result = calculate_risk(
        match_results=[
            make_match(
                "STUDENT_NAME",
                MatchStatus.CONFLICT,
            ),
            make_match(
                "ANNUAL_INCOME",
                MatchStatus.CONFLICT,
            ),
        ],
        duplicate=True,
        missing_document=True,
        unreadable_document=True,
    )

    assert result.score == 100
    assert result.band == RiskBand.HIGH