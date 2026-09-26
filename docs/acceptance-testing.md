# Acceptance Testing

This repository uses a deterministic mocked-extraction path for the current
demo while keeping the live GPT-4o adapter available behind the same provider
interface.

## Processing path

The acceptance tests exercise this logical flow:

    stored application documents
             |
             v
        OCR stage
             |
             v
    DocumentExtraction (MOCKED)
             |
             v
    deterministic scheme rules
             |
             v
    cross-document matching
             |
             v
    prototype risk score
             |
             v
    workflow transition + event

The production OCR implementation remains LlamaCloud-based. The tests replace
only the OCR call and extraction service with deterministic fixtures so the
acceptance suite is repeatable and does not depend on external AI credits.

## Exact extraction schema

Every fixture is instantiated as the production
app.schemas.extraction.DocumentExtraction Pydantic model.

The fixture output explicitly contains:

- reasoning: "MOCKED EXTRACTION OUTPUT ..."
- evidence: "MOCKED_FIXTURE"

This is deliberate provenance labeling. These fixtures must never be described
as live GPT-4o output.

## Five acceptance cases

| Case | Input condition | Expected status | Risk |
|---|---|---:|---:|
| A | All four configured PRE-MATRIC documents; consistent eligible extraction | APPROVED | 0 |
| B | All four documents; annual income = 320000, above configured 250000 limit | DEFICIENT | 0 |
| C | All four documents; identity document has a different student name | FLAGGED_FOR_REVIEW | 30 |
| D | All four documents present; income certificate is unreadable at OCR stage | DEFICIENT | 20 |
| E | Caste certificate is missing | DEFICIENT | 20 |

## Live GPT-4o adapter

GPT4oExtractionProvider remains available through the same
ExtractionProvider interface. Switching providers is configuration-only:

    EXTRACTION_PROVIDER=mock

or, when live API access is available:

    EXTRACTION_PROVIDER=gpt4o

No acceptance claim in this document depends on a successful live GPT-4o API
request.

## Test command

Run from services/api:

    python -m pytest -q
