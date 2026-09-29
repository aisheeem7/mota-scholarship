"""Deterministic acceptance tests for the complete processing pipeline.

The extraction layer is intentionally mocked here. OCR, storage, validation,
matching, risk, and workflow behavior are still exercised through the real
pipeline implementation.
"""

from uuid import NAMESPACE_URL, UUID, uuid5

import pytest

from app.schemas.application import ApplicationStatus, OCRStatus
from app.schemas.extraction import DocumentExtraction
from app.services.ocr import pipeline as ocr_pipeline
from app.services.validation.validation_service import (
    get_required_documents,
    validate_extraction,
)
from tests.fixtures.acceptance_cases import (
    ACCEPTANCE_CASES,
)


class FakeResult:
    def __init__(self, data):
        self.data = data


class FakeQuery:
    def __init__(self, database, table_name):
        self.database = database
        self.table_name = table_name
        self.filters = {}
        self.pending_insert = None
        self.pending_update = None

    def select(self, *fields):
        return self

    def eq(self, field, value):
        self.filters[field] = value
        return self

    def limit(self, value):
        return self

    def insert(self, data):
        # supabase-py accepts a single row or a list of rows.
        if isinstance(data, list):
            self.pending_insert = [dict(row) for row in data]
        else:
            self.pending_insert = [dict(data)]
        return self

    def update(self, data):
        self.pending_update = dict(data)
        return self

    def execute(self):
        table = self.database.setdefault(
            self.table_name,
            [],
        )

        rows = table

        for field, value in self.filters.items():
            rows = [
                row
                for row in rows
                if str(row.get(field)) == str(value)
            ]

        if self.pending_update is not None:
            for row in rows:
                row.update(self.pending_update)
            return FakeResult(rows)

        if self.pending_insert is not None:
            table.extend(self.pending_insert)
            return FakeResult(self.pending_insert)

        return FakeResult(rows)


class FakeStorageBucket:
    def __init__(self, storage):
        self.storage = storage

    def download(self, path):
        return self.storage[path]["bytes"]


class FakeStorage:
    def __init__(self, storage):
        self.storage = storage

    def from_(self, bucket_name):
        return FakeStorageBucket(self.storage)


class FakeSupabase:
    def __init__(self):
        self.database = {
            "applications": [],
            "documents": [],
            "validations": [],
            "student_document_matches": [],
            "workflow_events": [],
        }
        self.storage_data = {}
        self.storage = FakeStorage(self.storage_data)

    def table(self, table_name):
        return FakeQuery(
            self.database,
            table_name,
        )


def _application_id(case_id: str) -> UUID:
    return uuid5(
        NAMESPACE_URL,
        f"mota-scholarship/acceptance/{case_id}/application",
    )


def _document_id(
    case_id: str,
    document_type: str,
) -> UUID:
    return uuid5(
        NAMESPACE_URL,
        f"mota-scholarship/acceptance/{case_id}/document/{document_type}",
    )


def _seed_case(
    fake_supabase: FakeSupabase,
    case,
):
    application_id = _application_id(case.case_id)
    student_id = uuid5(
        NAMESPACE_URL,
        f"mota-scholarship/acceptance/{case.case_id}/student",
    )

    fake_supabase.database["applications"].append(
        {
            "id": str(application_id),
            "student_id": str(student_id),
            "scheme_id": case.scheme_id,
            "status": ApplicationStatus.SUBMITTED.value,
            "risk_score": None,
        }
    )

    for document_type in case.present_document_types:
        document_id = _document_id(
            case.case_id,
            document_type,
        )

        storage_path = (
            f"applications/{application_id}/"
            f"{document_id}-{document_type}.pdf"
        )

        fake_supabase.database["documents"].append(
            {
                "id": str(document_id),
                "application_id": str(application_id),
                "document_type": document_type,
                "storage_path": storage_path,
                "ocr_status": OCRStatus.PROCESSING.value,
            }
        )

        fake_supabase.storage_data[storage_path] = {
            "bytes": b"%PDF-1.4 deterministic acceptance fixture",
        }

    return application_id


@pytest.mark.parametrize(
    "case",
    ACCEPTANCE_CASES,
    ids=lambda case: case.case_id,
)
def test_acceptance_case_uses_exact_document_extraction_schema(case):
    """Every fixture is a DocumentExtraction instance, not loose dict data."""

    expected_fields = set(
        DocumentExtraction.model_fields
    )

    for extraction in case.extractions_by_type.values():
        assert isinstance(
            extraction,
            DocumentExtraction,
        )
        assert set(extraction.model_dump().keys()) == expected_fields
        assert extraction.evidence
        assert extraction.evidence[0] == "MOCKED_FIXTURE"
        assert "MOCKED EXTRACTION OUTPUT" in (
            extraction.reasoning or ""
        )


def test_required_document_mapping_is_frozen_for_all_schemes():
    expected = {
        "PRE_MATRIC": (
            "INCOME_CERTIFICATE",
            "CASTE_CERTIFICATE",
            "ACADEMIC_RECORD",
            "IDENTITY_DOCUMENT",
        ),
        "POST_MATRIC": (
            "INCOME_CERTIFICATE",
            "CASTE_CERTIFICATE",
            "ACADEMIC_RECORD",
            "IDENTITY_DOCUMENT",
        ),
        "TOP_CLASS": (
            "INCOME_CERTIFICATE",
            "CASTE_CERTIFICATE",
            "ACADEMIC_RECORD",
            "IDENTITY_DOCUMENT",
        ),
        "NATIONAL_FELLOWSHIP": (
            "CASTE_CERTIFICATE",
            "ACADEMIC_RECORD",
            "IDENTITY_DOCUMENT",
        ),
        "NATIONAL_OVERSEAS": (
            "INCOME_CERTIFICATE",
            "CASTE_CERTIFICATE",
            "ACADEMIC_RECORD",
            "IDENTITY_DOCUMENT",
        ),
    }

    for scheme_id, required_documents in expected.items():
        assert tuple(
            get_required_documents(scheme_id)
        ) == required_documents


@pytest.mark.parametrize(
    "case",
    ACCEPTANCE_CASES,
    ids=lambda case: case.case_id,
)
def test_acceptance_case_required_document_presence_is_deterministic(case):
    result = ocr_pipeline.validate_required_documents(
        scheme_id=case.scheme_id,
        uploaded_document_types=list(
            case.present_document_types
        ),
    )

    assert result.rule_id == "REQUIRED_DOCUMENTS"

    if case.case_id == "E_MISSING_DOCUMENT":
        assert result.passed is False
        assert "CASTE_CERTIFICATE" in result.reasoning
    else:
        assert result.passed is True


def test_high_income_fixture_fails_the_income_rule():
    case = next(
        item
        for item in ACCEPTANCE_CASES
        if item.case_id == "B_HIGH_INCOME"
    )

    extraction = case.extractions_by_type["INCOME_CERTIFICATE"]

    results = validate_extraction(
        extraction=extraction,
        scheme_id=case.scheme_id,
    )

    by_rule = {
        result.rule_id: result
        for result in results
    }

    assert by_rule["CATEGORY"].passed is True
    assert by_rule["ACADEMIC_LEVEL"].passed is True
    assert by_rule["INCOME"].passed is False


@pytest.mark.parametrize(
    "case",
    ACCEPTANCE_CASES,
    ids=lambda case: case.case_id,
)
def test_complete_pipeline_acceptance_case(
    monkeypatch,
    case,
):
    """Run stored files -> OCR -> mocked extraction -> rules -> matching -> risk -> workflow."""

    fake_supabase = FakeSupabase()
    application_id = _seed_case(
        fake_supabase,
        case,
    )

    class FixtureExtractionService:
        def extract_document(self, text, document_type):
            return case.extractions_by_type[document_type]

    def fake_ocr(file_bytes, filename):
        if (
            case.unreadable_document_type is not None
            and f"-{case.unreadable_document_type}.pdf" in filename
        ):
            raise ocr_pipeline.OCRProcessingError(
                "Deterministic unreadable fixture"
            )

        return (
            "MOCKED OCR OUTPUT\n"
            f"Fixture case: {case.case_id}\n"
            f"Filename: {filename}"
        )

    monkeypatch.setattr(
        ocr_pipeline,
        "run_ocr",
        fake_ocr,
    )
    monkeypatch.setattr(
        ocr_pipeline,
        "get_extraction_service",
        lambda: FixtureExtractionService(),
    )

    ocr_pipeline.process_application_documents(
        application_id,
        fake_supabase,
    )

    application = fake_supabase.database["applications"][0]

    assert application["status"] == case.expected_status.value
    assert application["risk_score"] == case.expected_risk_score

    events = fake_supabase.database["workflow_events"]

    assert len(events) == 2
    assert events[0]["from_status"] == "SUBMITTED"
    assert events[0]["to_status"] == "PROCESSING"
    assert events[1]["from_status"] == "PROCESSING"
    assert events[1]["to_status"] == case.expected_status.value

    if case.case_id == "C_NAME_MISMATCH":
        matches = fake_supabase.database[
            "student_document_matches"
        ]
        assert any(
            result["field_name"] == "STUDENT_NAME"
            and result["match_status"] == "CONFLICT"
            for result in matches
        )

    elif case.case_id == "D_UNREADABLE":
        documents = fake_supabase.database["documents"]

        unreadable = [
            document
            for document in documents
            if document["document_type"] == "INCOME_CERTIFICATE"
        ][0]

        assert unreadable["ocr_status"] == "UNREADABLE"

    elif case.case_id == "E_MISSING_DOCUMENT":
        validations = fake_supabase.database["validations"]

        required_results = [
            result
            for result in validations
            if result["rule_id"] == "REQUIRED_DOCUMENTS"
        ]

        assert required_results
        assert required_results[0]["passed"] is False

    else:
        documents = fake_supabase.database["documents"]

        assert all(
            document["ocr_status"] == "READABLE"
            for document in documents
        )
