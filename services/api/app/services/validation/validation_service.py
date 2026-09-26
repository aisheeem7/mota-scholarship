import json
from pathlib import Path

from app.schemas.extraction import DocumentExtraction
from app.schemas.validation import (
    ValidationResult,
    ValidationSeverity,
)


CONFIG_PATH = (
    Path(__file__).resolve().parents[5]
    / "config"
    / "schemes.json"
)


RULE_NAMES = {
    "CATEGORY": "Category Eligibility",
    "ACADEMIC_LEVEL": "Academic Level Eligibility",
    "INCOME": "Income Eligibility",
    "REQUIRED_DOCUMENTS": "Required Documents",
    "INSTITUTION": "Institution Requirement",
    "COURSE_ACADEMIC": "Course / Academic Requirement",
    "SLOT_AVAILABILITY": "Slot Availability",
}


def load_scheme_config() -> dict:
    """
    Load the canonical scheme configuration.
    """

    with CONFIG_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def get_scheme_config(scheme_id: str) -> dict:
    """
    Return the configuration for one scheme.
    """

    config = load_scheme_config()

    for scheme in config.get("schemes", []):
        if scheme.get("id") == scheme_id:
            return scheme

    raise ValueError(
        f"Unknown scheme_id: {scheme_id}"
    )


def get_rule_name(rule_id: str) -> str:
    """
    Convert a configured rule ID into a readable API rule name.
    """

    return RULE_NAMES.get(
        rule_id,
        rule_id.replace("_", " ").title(),
    )


def _result(
    *,
    rule_id: str,
    passed: bool | None,
    extracted_value: str | None,
    expected_condition: str | None,
    reasoning: str | None,
    severity: ValidationSeverity | None,
) -> ValidationResult:
    return ValidationResult(
        rule_id=rule_id,
        rule_name=get_rule_name(rule_id),
        passed=passed,
        extracted_value=extracted_value,
        expected_condition=expected_condition,
        reasoning=reasoning,
        severity=severity,
    )


def validate_extraction(
    extraction: DocumentExtraction,
    scheme_id: str,
) -> list[ValidationResult]:
    """
    Validate structured extraction against deterministic
    scheme configuration.

    AI extraction supplies values.
    This service evaluates those values against rules.
    """

    scheme = get_scheme_config(scheme_id)

    results: list[ValidationResult] = []

    required_rules = scheme.get(
        "validations_required",
        [],
    )

    # ---------------------------------------------------------
    # CATEGORY
    # ---------------------------------------------------------

    if "CATEGORY" in required_rules:
        expected_category = scheme.get("category")
        actual_category = extraction.category

        if actual_category is None:
            results.append(
                _result(
                    rule_id="CATEGORY",
                    passed=None,
                    extracted_value=None,
                    expected_condition=(
                        f"Category must be {expected_category}"
                    ),
                    reasoning=(
                        "Category could not be evaluated because "
                        "the extracted category is missing."
                    ),
                    severity=ValidationSeverity.MEDIUM,
                )
            )
        else:
            passed = (
                actual_category.strip().upper()
                == str(expected_category).strip().upper()
            )

            results.append(
                _result(
                    rule_id="CATEGORY",
                    passed=passed,
                    extracted_value=actual_category,
                    expected_condition=(
                        f"Category must be {expected_category}"
                    ),
                    reasoning=(
                        "Extracted category matches the configured "
                        "scheme category."
                        if passed
                        else
                        "Extracted category does not match the "
                        "configured scheme category."
                    ),
                    severity=(
                        ValidationSeverity.NONE
                        if passed
                        else ValidationSeverity.HIGH
                    ),
                )
            )

    # ---------------------------------------------------------
    # INCOME
    # ---------------------------------------------------------

    if "INCOME" in required_rules:
        income_config = scheme.get("income")

        if income_config is None:
            results.append(
                _result(
                    rule_id="INCOME",
                    passed=None,
                    extracted_value=(
                        str(extraction.annual_income)
                        if extraction.annual_income is not None
                        else None
                    ),
                    expected_condition=(
                        "No income threshold configured"
                    ),
                    reasoning=(
                        "This scheme does not define an income "
                        "threshold in the canonical configuration."
                    ),
                    severity=None,
                )
            )

        elif extraction.annual_income is None:
            results.append(
                _result(
                    rule_id="INCOME",
                    passed=None,
                    extracted_value=None,
                    expected_condition=(
                        f"Annual income must be <= "
                        f"{income_config['limit']}"
                    ),
                    reasoning=(
                        "Income could not be evaluated because "
                        "the extracted annual income is missing."
                    ),
                    severity=ValidationSeverity.MEDIUM,
                )
            )

        else:
            limit = income_config["limit"]
            operator = income_config["operator"]

            if operator == "LESS_THAN_OR_EQUAL":
                passed = extraction.annual_income <= limit
                expected_condition = (
                    f"Annual income must be <= {limit}"
                )
            else:
                raise ValueError(
                    f"Unsupported income operator: {operator}"
                )

            results.append(
                _result(
                    rule_id="INCOME",
                    passed=passed,
                    extracted_value=str(
                        extraction.annual_income
                    ),
                    expected_condition=expected_condition,
                    reasoning=(
                        "Extracted annual income satisfies the "
                        "configured income condition."
                        if passed
                        else
                        "Extracted annual income exceeds the "
                        "configured income condition."
                    ),
                    severity=(
                        ValidationSeverity.NONE
                        if passed
                        else ValidationSeverity.HIGH
                    ),
                )
            )

    # ---------------------------------------------------------
    # ACADEMIC LEVEL
    # ---------------------------------------------------------

    if "ACADEMIC_LEVEL" in required_rules:
        configured_level = scheme.get("target_level")
        actual_level = extraction.academic_level

        if actual_level is None:
            results.append(
                _result(
                    rule_id="ACADEMIC_LEVEL",
                    passed=None,
                    extracted_value=None,
                    expected_condition=(
                        f"Academic level must satisfy "
                        f"{configured_level}"
                    ),
                    reasoning=(
                        "Academic level could not be evaluated "
                        "because it was not extracted."
                    ),
                    severity=ValidationSeverity.MEDIUM,
                )
            )

        elif configured_level is None:
            results.append(
                _result(
                    rule_id="ACADEMIC_LEVEL",
                    passed=None,
                    extracted_value=actual_level,
                    expected_condition=(
                        "No academic-level restriction configured"
                    ),
                    reasoning=(
                        "The scheme configuration does not define "
                        "a target academic level."
                    ),
                    severity=None,
                )
            )

        else:
            actual_normalized = actual_level.strip().upper()
            configured_normalized = (
                str(configured_level).strip().upper()
            )

            # The canonical Pre-Matric configuration represents
            # Classes IX-X as a range rather than a single value.
            if configured_normalized == "IX-X":
                passed = actual_normalized in {
                    "IX",
                    "X",
                }
            else:
                # Do not invent additional equivalence mappings.
                # For other schemes, compare against the configured
                # target-level text.
                passed = (
                    actual_normalized
                    == configured_normalized
                )

            results.append(
                _result(
                    rule_id="ACADEMIC_LEVEL",
                    passed=passed,
                    extracted_value=actual_level,
                    expected_condition=(
                        f"Academic level must satisfy "
                        f"{configured_level}"
                    ),
                    reasoning=(
                        "Extracted academic level satisfies "
                        "the configured target level."
                        if passed
                        else
                        "The extracted academic level does not "
                        "satisfy the configured target-level value."
                    ),
                    severity=(
                        ValidationSeverity.NONE
                        if passed
                        else ValidationSeverity.HIGH
                    ),
                )
            )

    # ---------------------------------------------------------
    # REQUIRED DOCUMENTS
    # ---------------------------------------------------------

    if "REQUIRED_DOCUMENTS" in required_rules:
        results.append(
            _result(
                rule_id="REQUIRED_DOCUMENTS",
                passed=None,
                extracted_value=None,
                expected_condition=(
                    "Required document evidence must be available"
                ),
                reasoning=(
                    "The current canonical configuration identifies "
                    "REQUIRED_DOCUMENTS as a validation category, "
                    "but does not define an exact per-scheme "
                    "document mapping. This rule is therefore "
                    "not evaluable at this stage."
                ),
                severity=None,
            )
        )

    # ---------------------------------------------------------
    # INSTITUTION
    # ---------------------------------------------------------

    if "INSTITUTION" in required_rules:
        if extraction.institution is None:
            results.append(
                _result(
                    rule_id="INSTITUTION",
                    passed=None,
                    extracted_value=None,
                    expected_condition=(
                        "Institution evidence must be available"
                    ),
                    reasoning=(
                        "Institution was not extracted."
                    ),
                    severity=ValidationSeverity.MEDIUM,
                )
            )
        else:
            results.append(
                _result(
                    rule_id="INSTITUTION",
                    passed=True,
                    extracted_value=extraction.institution,
                    expected_condition=(
                        "Institution evidence must be available"
                    ),
                    reasoning=(
                        "Institution information is present."
                    ),
                    severity=ValidationSeverity.NONE,
                )
            )

    # ---------------------------------------------------------
    # COURSE / ACADEMIC
    # ---------------------------------------------------------

    if "COURSE_ACADEMIC" in required_rules:
        if (
            extraction.course is None
            and extraction.academic_level is None
        ):
            results.append(
                _result(
                    rule_id="COURSE_ACADEMIC",
                    passed=None,
                    extracted_value=None,
                    expected_condition=(
                        "Course or academic evidence must be available"
                    ),
                    reasoning=(
                        "Neither course nor academic-level evidence "
                        "was extracted."
                    ),
                    severity=ValidationSeverity.MEDIUM,
                )
            )
        else:
            evidence_parts = []

            if extraction.course is not None:
                evidence_parts.append(
                    f"course={extraction.course}"
                )

            if extraction.academic_level is not None:
                evidence_parts.append(
                    f"academic_level={extraction.academic_level}"
                )

            results.append(
                _result(
                    rule_id="COURSE_ACADEMIC",
                    passed=True,
                    extracted_value=", ".join(
                        evidence_parts
                    ),
                    expected_condition=(
                        "Course or academic evidence must be available"
                    ),
                    reasoning=(
                        "Course or academic-level evidence is present."
                    ),
                    severity=ValidationSeverity.NONE,
                )
            )

    # ---------------------------------------------------------
    # SLOT AVAILABILITY
    # ---------------------------------------------------------

    if "SLOT_AVAILABILITY" in required_rules:
        results.append(
            _result(
                rule_id="SLOT_AVAILABILITY",
                passed=None,
                extracted_value=None,
                expected_condition=(
                    "Configured scholarship slots must be available"
                ),
                reasoning=(
                    "Slot availability is configurable in the scheme "
                    "file but is not connected to a live availability "
                    "counter in this validation service."
                ),
                severity=None,
            )
        )

    return results