"""Browser-facing API E2E harness for the MoTA backend.

This script performs API requests only for application creation, document
upload, processing, polling, and validation reads. It never writes directly
to Supabase. The Supabase client is used read-only to resolve the three seeded
demo student IDs by name.

The active extraction provider is intentionally the deterministic mock
provider. Mock fixture markers are embedded in generated PDF text so the real
LlamaCloud OCR stage feeds deterministic, explicitly mocked extraction output.
"""

from __future__ import annotations

import argparse
import io
import os
import time
from dataclasses import dataclass

import httpx
from dotenv import load_dotenv
from supabase import create_client


FINAL_STATUSES = {
    "APPROVED",
    "DEFICIENT",
    "FLAGGED_FOR_REVIEW",
    "REJECTED",
}

EXPECTED_CASES = {
    "A_VALID": ("APPROVED", 0),
    "B_HIGH_INCOME": ("DEFICIENT", 0),
    "C_NAME_MISMATCH": ("FLAGGED_FOR_REVIEW", 30),
    "D_UNREADABLE": ("DEFICIENT", 20),
    "E_MISSING_DOCUMENT": ("DEFICIENT", 20),
}


@dataclass(frozen=True)
class CaseDefinition:
    case_id: str
    scheme_id: str
    student_name: str
    document_types: tuple[str, ...]
    markers: tuple[str, ...]
    unreadable_document_type: str | None


def _pdf_escape(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
        .replace("(", "\\(")
        .replace(")", "\\)")
    )


def make_text_pdf(lines: list[str]) -> bytes:
    """Create a tiny valid text PDF without external PDF dependencies."""

    commands = [
        "BT",
        "/F1 12 Tf",
        "50 750 Td",
    ]

    for index, line in enumerate(lines):
        if index:
            commands.append("0 -20 Td")
        commands.append(f"({_pdf_escape(line)}) Tj")

    commands.append("ET")
    stream = "\n".join(commands).encode("latin-1", "replace")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>"
        ),
        (
            b"<< /Length "
            + str(len(stream)).encode()
            + b" >>\nstream\n"
            + stream
            + b"\nendstream"
        ),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]

    for object_number, object_body in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(
            f"{object_number} 0 obj\n".encode()
        )
        pdf.extend(object_body)
        pdf.extend(b"\nendobj\n")

    xref_offset = len(pdf)
    pdf.extend(
        f"xref\n0 {len(objects) + 1}\n".encode()
    )
    pdf.extend(b"0000000000 65535 f \n")

    for offset in offsets[1:]:
        pdf.extend(
            f"{offset:010d} 00000 n \n".encode()
        )

    pdf.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n"
        ).encode()
    )

    return bytes(pdf)


def make_case_document(
    *,
    case_id: str,
    document_type: str,
    markers: tuple[str, ...],
    unreadable: bool,
) -> bytes:
    if unreadable:
        return b"This is an intentionally corrupted PDF fixture."

    lines = [
        "MO TA SCHOLARSHIP E2E TEST DOCUMENT",
        "Student Name: Demo Student",
        "Category: ST",
        "Annual Family Income: Rs. 1,80,000",
        "Academic Level: X",
        "Institution: Demo Institution",
        f"Document Type: {document_type}",
        f"Case: {case_id}",
        "Certificate Number: E2E-TEST-001",
        *markers,
    ]

    return make_text_pdf(lines)


def resolve_seeded_students() -> dict[str, str]:
    supabase_url = os.environ["SUPABASE_URL"]
    service_key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

    client = create_client(
        supabase_url,
        service_key,
    )

    rows = (
        client.table("students")
        .select("id, name")
        .in_(
            "name",
            [
                "Test Student One",
                "Test Student Two",
                "Test Student Three",
            ],
        )
        .execute()
        .data
        or []
    )

    found = {row["name"]: row["id"] for row in rows}

    missing = {
        name
        for name in (
            "Test Student One",
            "Test Student Two",
            "Test Student Three",
        )
        if name not in found
    }

    if missing:
        raise RuntimeError(
            "Seeded students missing from Supabase: "
            + ", ".join(sorted(missing))
        )

    return found


def api_base_url() -> str:
    return os.getenv(
        "MOTA_API_URL",
        "http://127.0.0.1:8001",
    ).rstrip("/")


def wait_for_final_status(
    client: httpx.Client,
    application_id: str,
    timeout_seconds: int,
) -> dict:
    deadline = time.time() + timeout_seconds
    last_response = None

    while time.time() < deadline:
        response = client.get(
            f"/api/v1/applications/{application_id}"
        )
        response.raise_for_status()
        last_response = response.json()

        if last_response["status"] in FINAL_STATUSES:
            return last_response

        time.sleep(2)

    raise TimeoutError(
        "Application did not reach a final status within "
        f"{timeout_seconds}s. Last response: {last_response}"
    )


def verify_api_contract(client: httpx.Client) -> None:
    response = client.get("/openapi.json")
    response.raise_for_status()

    paths = response.json().get("paths", {})

    required_paths = {
        "/api/v1/applications": "POST",
        "/api/v1/applications/{application_id}/documents": "POST",
        "/api/v1/applications/{application_id}/process": "POST",
        "/api/v1/applications/{application_id}": "GET",
        "/api/v1/applications/{application_id}/validations": "GET",
        "/api/v1/admin/applications/{application_id}/review": "POST",
    }

    missing = [
        f"{method} {path}"
        for path, method in required_paths.items()
        if method.lower() not in {
            key.lower()
            for key in paths.get(path, {})
        }
    ]

    if missing:
        raise AssertionError(
            "Required API contract routes missing from OpenAPI: "
            + ", ".join(missing)
        )

    print("API contract: PASS")
    for path, method in required_paths.items():
        print(f"  {method} {path}")


def create_application(
    client: httpx.Client,
    student_id: str,
    scheme_id: str,
) -> dict:
    response = client.post(
        "/api/v1/applications",
        json={
            "student_id": student_id,
            "scheme_id": scheme_id,
        },
    )

    if response.status_code != 201:
        raise AssertionError(
            "POST /applications failed: "
            f"{response.status_code} {response.text}"
        )

    return response.json()


def upload_document(
    client: httpx.Client,
    application_id: str,
    document_type: str,
    pdf_bytes: bytes,
) -> dict:
    response = client.post(
        f"/api/v1/applications/{application_id}/documents",
        data={
            "document_type": document_type,
        },
        files={
            "file": (
                f"{document_type}.pdf",
                io.BytesIO(pdf_bytes),
                "application/pdf",
            )
        },
    )

    if response.status_code != 202:
        raise AssertionError(
            "POST /documents failed: "
            f"{response.status_code} {response.text}"
        )

    return response.json()


def run_case(
    client: httpx.Client,
    case: CaseDefinition,
    student_id: str,
    timeout_seconds: int,
) -> dict:
    application = create_application(
        client,
        student_id,
        case.scheme_id,
    )
    application_id = application["id"]

    for document_type in case.document_types:
        unreadable = (
            document_type == case.unreadable_document_type
        )

        pdf_bytes = make_case_document(
            case_id=case.case_id,
            document_type=document_type,
            markers=case.markers,
            unreadable=unreadable,
        )

        if (
            case.case_id == "C_NAME_MISMATCH"
            and document_type == "IDENTITY_DOCUMENT"
        ):
            pdf_bytes = make_text_pdf(
                [
                    "MO TA SCHOLARSHIP E2E TEST DOCUMENT",
                    "Student Name: Other Student",
                    "Category: ST",
                    "Annual Family Income: Rs. 1,80,000",
                    "Academic Level: X",
                    "Institution: Demo Institution",
                    "Document Type: IDENTITY_DOCUMENT",
                    f"Case: {case.case_id}",
                    "E2E_CASE_C_NAME_MISMATCH",
                ]
            )

        upload_document(
            client,
            application_id,
            document_type,
            pdf_bytes,
        )

    process_response = client.post(
        f"/api/v1/applications/{application_id}/process"
    )

    if process_response.status_code != 202:
        raise AssertionError(
            "POST /process failed: "
            f"{process_response.status_code} "
            f"{process_response.text}"
        )

    processing_body = process_response.json()

    if processing_body["status"] != "PROCESSING":
        raise AssertionError(
            "Process response was expected to be PROCESSING, got "
            + str(processing_body["status"])
        )

    final_application = wait_for_final_status(
        client,
        application_id,
        timeout_seconds,
    )

    validations_response = client.get(
        f"/api/v1/applications/{application_id}/validations"
    )
    validations_response.raise_for_status()
    validations = validations_response.json()

    expected_status, expected_risk = EXPECTED_CASES[
        case.case_id
    ]

    result = {
        "case": case.case_id,
        "application_id": application_id,
        "scheme_id": case.scheme_id,
        "final_status": final_application["status"],
        "risk_score": final_application["risk_score"],
        "validations": validations,
        "expected_status": expected_status,
        "expected_risk_score": expected_risk,
        "passed": (
            final_application["status"] == expected_status
            and final_application["risk_score"] == expected_risk
        ),
    }

    return result


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--timeout",
        type=int,
        default=180,
        help="Per-case polling timeout in seconds.",
    )
    args = parser.parse_args()

    base_url = api_base_url()

    cases = (
        CaseDefinition(
            "A_VALID",
            "PRE_MATRIC",
            "Test Student Two",
            (
                "INCOME_CERTIFICATE",
                "CASTE_CERTIFICATE",
                "ACADEMIC_RECORD",
                "IDENTITY_DOCUMENT",
            ),
            (),
            None,
        ),
        CaseDefinition(
            "B_HIGH_INCOME",
            "PRE_MATRIC",
            "Test Student Three",
            (
                "INCOME_CERTIFICATE",
                "CASTE_CERTIFICATE",
                "ACADEMIC_RECORD",
                "IDENTITY_DOCUMENT",
            ),
            ("E2E_CASE_B_HIGH_INCOME",),
            None,
        ),
        CaseDefinition(
            "C_NAME_MISMATCH",
            "TOP_CLASS",
            "Test Student Two",
            (
                "INCOME_CERTIFICATE",
                "CASTE_CERTIFICATE",
                "ACADEMIC_RECORD",
                "IDENTITY_DOCUMENT",
            ),
            ("E2E_CASE_C_NAME_MISMATCH",),
            None,
        ),
        CaseDefinition(
            "D_UNREADABLE",
            "NATIONAL_FELLOWSHIP",
            "Test Student One",
            (
                "INCOME_CERTIFICATE",
                "CASTE_CERTIFICATE",
                "ACADEMIC_RECORD",
                "IDENTITY_DOCUMENT",
            ),
            (),
            "INCOME_CERTIFICATE",
        ),
        CaseDefinition(
            "E_MISSING_DOCUMENT",
            "NATIONAL_OVERSEAS",
            "Test Student Three",
            (
                "INCOME_CERTIFICATE",
                "ACADEMIC_RECORD",
                "IDENTITY_DOCUMENT",
            ),
            (),
            None,
        ),
    )

    seeded_students = resolve_seeded_students()

    with httpx.Client(
        base_url=base_url,
        timeout=60,
    ) as client:
        health = client.get("/health")
        health.raise_for_status()
        print(
            "Backend health: PASS",
            health.json(),
        )

        verify_api_contract(client)

        results = []

        for case in cases:
            print(
                f"\nRunning {case.case_id} "
                f"({case.scheme_id})..."
            )

            result = run_case(
                client,
                case,
                seeded_students[case.student_name],
                args.timeout,
            )

            results.append(result)

            print(
                "  application_id:",
                result["application_id"],
            )
            print(
                "  final_status:",
                result["final_status"],
            )
            print(
                "  risk_score:",
                result["risk_score"],
            )
            print(
                "  expected:",
                result["expected_status"],
                result["expected_risk_score"],
            )
            print(
                "  validations:",
                len(result["validations"]),
            )
            print(
                "  PASS:",
                result["passed"],
            )

        print("\n=== FIVE-CASE SUMMARY ===")
        for result in results:
            print(
                f"{result['case']}: "
                f"{result['application_id']} | "
                f"{result['final_status']} | "
                f"risk={result['risk_score']} | "
                f"PASS={result['passed']}"
            )

        failed = [
            result["case"]
            for result in results
            if not result["passed"]
        ]

        if failed:
            raise SystemExit(
                "Acceptance cases failed: "
                + ", ".join(failed)
            )

        print("\nALL FIVE API E2E CASES: PASS")


if __name__ == "__main__":
    main()
