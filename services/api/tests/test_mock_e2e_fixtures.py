"""Tests for deterministic mock-extraction E2E fixture directives."""

import pytest

from app.schemas.extraction import DocumentExtraction
from app.services.ai.extraction_provider import ExtractionError
from app.services.ai.mock_provider import MockExtractionProvider


def test_mock_provider_baseline_is_explicitly_mocked():
    result = MockExtractionProvider().extract(
        text="ordinary deterministic demo OCR",
        document_type="INCOME_CERTIFICATE",
    )

    assert isinstance(result, DocumentExtraction)
    assert result.student_name == "Demo Student"
    assert result.category == "ST"
    assert result.annual_income == 180000
    assert result.evidence[0] == "MOCKED_FIXTURE"
    assert "not a live GPT-4o result" in (result.reasoning or "")


def test_mock_provider_high_income_fixture():
    result = MockExtractionProvider().extract(
        text="E2E_CASE_B_HIGH_INCOME",
        document_type="INCOME_CERTIFICATE",
    )

    assert result.annual_income == 320000


def test_mock_provider_name_mismatch_fixture_only_changes_identity():
    provider = MockExtractionProvider()

    income = provider.extract(
        text="E2E_CASE_C_NAME_MISMATCH",
        document_type="INCOME_CERTIFICATE",
    )
    identity = provider.extract(
        text="E2E_CASE_C_NAME_MISMATCH",
        document_type="IDENTITY_DOCUMENT",
    )

    assert income.student_name == "Demo Student"
    assert identity.student_name == "Other Student"


def test_mock_provider_missing_income_fixture():
    result = MockExtractionProvider().extract(
        text="E2E_MISSING_INCOME",
        document_type="INCOME_CERTIFICATE",
    )

    assert result.annual_income is None


def test_mock_provider_malformed_fixture_is_an_extraction_failure():
    with pytest.raises(
        ExtractionError,
        match="Deterministic malformed extraction fixture",
    ):
        MockExtractionProvider().extract(
            text="E2E_MALFORMED_EXTRACTION",
            document_type="INCOME_CERTIFICATE",
        )
