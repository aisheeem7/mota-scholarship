from app.schemas.extraction import DocumentExtraction
from app.schemas.matching import MatchStatus
from app.services.matching.matching_service import (
    has_conflict,
    match_documents,
)


def make_document(
    document_id,
    *,
    student_name="Rahul Das",
    category="ST",
    annual_income=180000,
):
    return {
        "document_id": document_id,
        "document_type": "INCOME_CERTIFICATE",
        "extraction": DocumentExtraction(
            student_name=student_name,
            category=category,
            annual_income=annual_income,
            academic_level="X",
            institution="Demo Institution",
            course=None,
            confidence=1.0,
        ),
    }


def get_result(
    results,
    field_name,
):
    return next(
        result
        for result in results
        if result.field_name == field_name
    )


def test_exact_name_match():
    results = match_documents(
        [
            make_document("doc-1"),
            make_document("doc-2"),
        ]
    )

    name_result = get_result(
        results,
        "STUDENT_NAME",
    )

    assert name_result.match_status == MatchStatus.EXACT_MATCH
    assert name_result.similarity == 1.0


def test_name_harmless_variant():
    results = match_documents(
        [
            make_document(
                "doc-1",
                student_name="Rahul Das",
            ),
            make_document(
                "doc-2",
                student_name="rahul-das",
            ),
        ]
    )

    name_result = get_result(
        results,
        "STUDENT_NAME",
    )

    assert (
        name_result.match_status
        == MatchStatus.HARMLESS_VARIANT
    )


def test_name_conflict():
    results = match_documents(
        [
            make_document(
                "doc-1",
                student_name="Rahul Das",
            ),
            make_document(
                "doc-2",
                student_name="Rahul Kumar",
            ),
        ]
    )

    name_result = get_result(
        results,
        "STUDENT_NAME",
    )

    assert name_result.match_status == MatchStatus.CONFLICT
    assert has_conflict(results) is True


def test_category_conflict():
    results = match_documents(
        [
            make_document(
                "doc-1",
                category="ST",
            ),
            make_document(
                "doc-2",
                category="OBC",
            ),
        ]
    )

    category_result = get_result(
        results,
        "CATEGORY",
    )

    assert (
        category_result.match_status
        == MatchStatus.CONFLICT
    )


def test_income_exact_match():
    results = match_documents(
        [
            make_document(
                "doc-1",
                annual_income=180000,
            ),
            make_document(
                "doc-2",
                annual_income=180000,
            ),
        ]
    )

    income_result = get_result(
        results,
        "ANNUAL_INCOME",
    )

    assert (
        income_result.match_status
        == MatchStatus.EXACT_MATCH
    )
    assert income_result.similarity == 1.0


def test_income_conflict():
    results = match_documents(
        [
            make_document(
                "doc-1",
                annual_income=180000,
            ),
            make_document(
                "doc-2",
                annual_income=320000,
            ),
        ]
    )

    income_result = get_result(
        results,
        "ANNUAL_INCOME",
    )

    assert (
        income_result.match_status
        == MatchStatus.CONFLICT
    )
    assert has_conflict(results) is True


def test_missing_field_is_skipped():
    document_1 = make_document(
        "doc-1",
    )

    document_2 = make_document(
        "doc-2",
    )

    document_2["extraction"].category = None

    results = match_documents(
        [
            document_1,
            document_2,
        ]
    )

    category_results = [
        result
        for result in results
        if result.field_name == "CATEGORY"
    ]

    assert category_results == []


def test_multiple_documents_produce_pairwise_results():
    results = match_documents(
        [
            make_document("doc-1"),
            make_document("doc-2"),
            make_document("doc-3"),
        ]
    )

    # 3 document pairs × 3 currently matchable fields
    assert len(results) == 9