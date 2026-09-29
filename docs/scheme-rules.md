# Scheme rules — field reference

Explains every field in [`config/schemes.json`](../config/schemes.json). Policy facts here are traced to
the Team Handbook, Ch.4 "Target Schemes" and Ch.5 "Policy as Configuration". UI wording lives separately
in [`config/translations/*.json`](../config/translations/en.json) — this file is stable IDs and eligibility facts only.

## Stable IDs

Five schemes. Use these exact strings everywhere `scheme_id` is read or written
(`applications.scheme_id` in the DB, `ApplicationCreate.scheme_id` in the API, frontend scheme selector):

| id | name |
|---|---|
| `PRE_MATRIC` | Pre-Matric Scholarship |
| `POST_MATRIC` | Post-Matric Scholarship |
| `TOP_CLASS` | National Scholarship Scheme — Top Class |
| `NATIONAL_FELLOWSHIP` | National Fellowship Scheme |
| `NATIONAL_OVERSEAS` | National Overseas Scholarship (NOS) |

`applications.scheme_id` is enforced at the DB layer by a CHECK constraint referencing exactly this list
(`supabase/migrations/20260922000002_scheme_id_and_embedding.sql`) — this file is still the source of
truth for what each ID *means*, but the DB now rejects anything outside these five.

## Field meanings

- **sponsorship** — `CENTRALLY_SPONSORED` (state-administered, central funding) vs `NATIONAL`
  (centrally administered). Informational only; not currently used by the rules engine.
- **target_level** — academic stage or institution class the scheme applies to.
- **category** — applicant category the scheme is restricted to. All five schemes are ST-only per the
  handbook's project scope (Ministry of Tribal Affairs).
- **income** — `{ limit, operator }` in INR/year, or `null` if the scheme has no income test
  (`NATIONAL_FELLOWSHIP`). `operator` is always `LESS_THAN_OR_EQUAL` today; kept explicit rather than
  hard-coded `<=` so a future scheme with a different comparison doesn't need a code change.
- **benefit_components** — what the scheme pays out. Some schemes pay a single `SCHOLARSHIP` amount;
  `POST_MATRIC` pays two components (`MAINTENANCE_ALLOWANCE` + `INSTITUTIONAL_FEE`); the amounts
  themselves aren't in the handbook yet — TODO once official rulebook is supplied.
- **stipend** — fellowship-specific monthly amounts, keyed by academic stage.
- **slot_limit** — annual cap on approvals, where the scheme is quota-based rather than open-ended.
- **tracked_fields** — extra fields the rules engine must validate for that scheme beyond the common set.
- **validations_required** — which validation categories the rules engine runs for this scheme; maps to
  `validations.rule_id` rows the engine writes per application.

## Cross-cutting validations (not per-scheme)

Name/identity matching across a student's documents is **not** part of any scheme's `validations_required`
list, and that's intentional, not an omission. Per the handbook (Ch.10, Cross-Document Matching), the
system flags `NAME_MISMATCH` → routes to `FLAGGED_FOR_REVIEW` uniformly, regardless of scheme — it's a
cross-document embedding comparison, not a scheme-specific rule. Don't add `NAME_MATCH`/`IDENTITY_MATCH`
to any scheme's `validations_required`; it lives in the matching pipeline instead.

## Prototype decisions (frozen in Issue #6, 2026-09-25)

These are **PROTOTYPE CONFIGURATION**, not official MoTA policy. No source in the handbook defines them.

- **Document types.** `documents.document_type` accepts `INCOME_CERTIFICATE`, `CASTE_CERTIFICATE`,
  `ACADEMIC_RECORD` and `IDENTITY_DOCUMENT` (enforced in the DB, migration
  `20260925000002_document_type_check.sql`). The values come from the handbook's Ch.32 demo story. There is
  **no per-scheme required-document mapping**: the handbook (Ch.1–36) never says which documents each scheme
  needs, so `REQUIRED_DOCUMENTS` in `validations_required` stays a category name only.
- **NOS PVTG.** PVTG is treated as a sub-tag of `ST`. `students.category` is not extended, and the 17 ST /
  3 PVTG slot split lives only in `NATIONAL_OVERSEAS.slot_limit`.
- **DBT mock.** A demo DBT transfer is recorded in a separate `dbt_mock_transactions` table, not as an
  application status. UI copy must always label it as a demo (handbook Ch.13).

## Open TODOs (do not guess — confirm against official scheme material)

- `TOP_CLASS.target_level`: exact roster of the 265 premier institutes (field is `null` until resolved —
  don't put placeholder text in the data value itself).
- Exact INR amounts for `POST_MATRIC` benefit components (maintenance allowance / fee slabs).
- Official per-scheme required documents, if an official source is ever supplied. Until then the prototype
  decision above applies.
