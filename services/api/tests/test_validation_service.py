from app.schemas.extraction import DocumentExtraction
from app.services.validation.validation_service import (
    validate_extraction,
)


def make_extraction(
    *,
    category="ST",
    annual_income=180000,
    academic_level="X",
    institution="Demo Institution",
    course=None,
):
    return DocumentExtraction(
        student_name="Demo Student",
        category=category,
        annual_income=annual_income,
        academic_level=academic_level,
        institution=institution,
        course=course,
        confidence=1.0,
    )


def get_result(results, rule_id):
    return next(
        result
        for result in results
        if result.rule_id == rule_id
    )


def test_pre_matric_valid_extraction():
    results = validate_extraction(
        make_extraction(),
        "PRE_MATRIC",
    )

    category = get_result(results, "CATEGORY")
    income = get_result(results, "INCOME")
    academic = get_result(results, "ACADEMIC_LEVEL")
    documents = get_result(
        results,
        "REQUIRED_DOCUMENTS",
    )

    assert category.passed is True
    assert category.rule_name == "Category Eligibility"

    assert income.passed is True

    assert academic.passed is True

    assert documents.passed is None


def test_pre_matric_high_income_fails():
    results = validate_extraction(
        make_extraction(
            annual_income=320000,
        ),
        "PRE_MATRIC",
    )

    income = get_result(results, "INCOME")

    assert income.passed is False
    assert income.extracted_value == "320000.0"


def test_category_mismatch_fails():
    results = validate_extraction(
        make_extraction(
            category="OBC",
        ),
        "PRE_MATRIC",
    )

    category = get_result(results, "CATEGORY")

    assert category.passed is False
    assert category.extracted_value == "OBC"


def test_missing_income_is_not_evaluable():
    results = validate_extraction(
        make_extraction(
            annual_income=None,
        ),
        "PRE_MATRIC",
    )

    income = get_result(results, "INCOME")

    assert income.passed is None


def test_missing_category_is_not_evaluable():
    results = validate_extraction(
        make_extraction(
            category=None,
        ),
        "PRE_MATRIC",
    )

    category = get_result(results, "CATEGORY")

    assert category.passed is None


def test_pre_matric_class_nine_passes():
    results = validate_extraction(
        make_extraction(
            academic_level="IX",
        ),
        "PRE_MATRIC",
    )

    academic = get_result(
        results,
        "ACADEMIC_LEVEL",
    )

    assert academic.passed is True