from fastapi.testclient import TestClient

from app.core.supabase_client import get_supabase
from app.main import app
from app.services.ocr import pipeline as ocr_pipeline
from uuid import UUID

# ============================================================
# FAKE SUPABASE
# ============================================================

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
        self.pending_insert = data
        return self
    def update(self, data):
        self.pending_update = data
        return self

    def execute(self):
        table = self.database.setdefault(self.table_name, [])
        if self.pending_update is not None:
            rows = table

            for field, value in self.filters.items():
                rows = [
                    row
                    for row in rows
                    if str(row.get(field)) == str(value)
                ]

            for row in rows:
                row.update(self.pending_update)

            return FakeResult(rows)

        if self.pending_insert is not None:
            row = dict(self.pending_insert)
            table.append(row)
            return FakeResult([row])

        rows = table

        for field, value in self.filters.items():
            rows = [
                row
                for row in rows
                if str(row.get(field)) == str(value)
            ]

        return FakeResult(rows)


class FakeStorageBucket:
    def __init__(self, storage):
        self.storage = storage

    def upload(self, path, file_bytes, options):
        self.storage[path] = {
            "bytes": file_bytes,
            "content_type": options.get("content-type"),
        }

    def remove(self, paths):
        for path in paths:
            self.storage.pop(path, None)
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
            "students": [],
            "applications": [],
            "documents": [],
            "dbt_mock_transactions": [],
            "validations": [],
        }

        self.storage_data = {}
        self.storage = FakeStorage(self.storage_data)

    def table(self, table_name):
        return FakeQuery(self.database, table_name)


# ============================================================
# TEST SETUP
# ============================================================

fake_supabase = FakeSupabase()


def override_get_supabase():
    return fake_supabase


app.dependency_overrides[get_supabase] = override_get_supabase

client = TestClient(app)


def setup_function():
    fake_supabase.database = {
        "students": [],
        "applications": [],
        "documents": [],
        "dbt_mock_transactions": [],
        "validations": [],
    }

    fake_supabase.storage_data.clear()


# ============================================================
# EXISTING APPLICATION TESTS
# ============================================================

def test_health():
    response = client.get("/health")

    assert response.status_code == 200


def test_create_application():
    student_id = "00000000-0000-0000-0000-000000000001"

    fake_supabase.database["students"].append({
        "id": student_id,
    })

    payload = {
        "student_id": student_id,
        "scheme_id": "PRE_MATRIC",
    }

    response = client.post(
        "/api/v1/applications",
        json=payload,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["student_id"] == student_id
    assert data["scheme_id"] == "PRE_MATRIC"
    assert data["status"] == "SUBMITTED"


def test_get_application():
    student_id = "00000000-0000-0000-0000-000000000002"

    fake_supabase.database["students"].append({
        "id": student_id,
    })

    payload = {
        "student_id": student_id,
        "scheme_id": "POST_MATRIC",
    }

    create_response = client.post(
        "/api/v1/applications",
        json=payload,
    )

    assert create_response.status_code == 201

    application_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/applications/{application_id}"
    )

    assert response.status_code == 200
    assert response.json()["id"] == application_id


def test_get_unknown_application():
    application_id = "00000000-0000-0000-0000-000000000099"

    response = client.get(
        f"/api/v1/applications/{application_id}"
    )

    assert response.status_code == 404


def test_invalid_student_id():
    payload = {
        "student_id": "not-a-uuid",
        "scheme_id": "PRE_MATRIC",
    }

    response = client.post(
        "/api/v1/applications",
        json=payload,
    )

    assert response.status_code == 422


def test_invalid_scheme_id():
    payload = {
        "student_id": "00000000-0000-0000-0000-000000000001",
        "scheme_id": "INVALID_SCHEME",
    }

    response = client.post(
        "/api/v1/applications",
        json=payload,
    )

    assert response.status_code == 422


# ============================================================
# DBT TESTS
# ============================================================

def test_dbt_transaction_not_found():
    application_id = "00000000-0000-0000-0000-000000000010"

    response = client.get(
        f"/api/v1/applications/{application_id}/dbt-transaction"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "DBT transaction not found"


def test_dbt_transaction_success():
    application_id = "00000000-0000-0000-0000-000000000011"

    fake_supabase.database["dbt_mock_transactions"].append({
        "application_id": application_id,
        "status": "SUCCESS",
        "transaction_id": "TXN-001",
        "amount": 2500,
        "created_at": "2026-09-25T00:00:00Z",
    })

    response = client.get(
        f"/api/v1/applications/{application_id}/dbt-transaction"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["application_id"] == application_id
    assert data["status"] == "SUCCESS"
    assert data["transaction_id"] == "TXN-001"
    assert data["amount"] == 2500


# ============================================================
# DOCUMENT UPLOAD TESTS
# ============================================================

def test_upload_document_success():
    application_id = "00000000-0000-0000-0000-000000000020"

    fake_supabase.database["applications"].append({
        "id": application_id,
    })

    response = client.post(
        f"/api/v1/applications/{application_id}/documents",
        data={
            "document_type": "INCOME_CERTIFICATE",
        },
        files={
            "file": (
                "income.pdf",
                b"%PDF-1.4 test document",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 202

    data = response.json()

    assert data["application_id"] == application_id
    assert data["document_type"] == "INCOME_CERTIFICATE"
    assert data["ocr_status"] == "PROCESSING"

    assert len(fake_supabase.database["documents"]) == 1
    assert len(fake_supabase.storage_data) == 1


def test_upload_document_invalid_extension():
    application_id = "00000000-0000-0000-0000-000000000021"

    fake_supabase.database["applications"].append({
        "id": application_id,
    })

    response = client.post(
        f"/api/v1/applications/{application_id}/documents",
        data={
            "document_type": "INCOME_CERTIFICATE",
        },
        files={
            "file": (
                "test.txt",
                b"test",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Unsupported file type"


def test_upload_document_invalid_content_type():
    application_id = "00000000-0000-0000-0000-000000000022"

    fake_supabase.database["applications"].append({
        "id": application_id,
    })

    response = client.post(
        f"/api/v1/applications/{application_id}/documents",
        data={
            "document_type": "CASTE_CERTIFICATE",
        },
        files={
            "file": (
                "certificate.pdf",
                b"fake content",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Unsupported content type"


# ============================================================
# VALIDATION TESTS
# ============================================================

def test_validations_list_found():
    application_id = "00000000-0000-0000-0000-000000000030"

    fake_supabase.database["validations"].append({
        "application_id": application_id,
        "rule_id": "RULE_001",
        "passed": True,
        "extracted_value": "120000",
        "expected_condition": "Income evidence provided",
        "reasoning": "Income certificate was readable",
        "severity": "NONE",
    })

    response = client.get(
        f"/api/v1/applications/{application_id}/validations"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["rule_id"] == "RULE_001"
    assert data[0]["passed"] is True
    assert data[0]["extracted_value"] == "120000"
    assert data[0]["expected_condition"] == "Income evidence provided"
    assert data[0]["reasoning"] == "Income certificate was readable"
    assert data[0]["severity"] == "NONE"


def test_validations_empty_list():
    application_id = "00000000-0000-0000-0000-000000000031"

    response = client.get(
        f"/api/v1/applications/{application_id}/validations"
    )

    assert response.status_code == 200
    assert response.json() == []


def test_validation_passed_true():
    application_id = "00000000-0000-0000-0000-000000000032"

    fake_supabase.database["validations"].append({
        "application_id": application_id,
        "rule_id": "RULE_PASS",
        "passed": True,
        "extracted_value": "VALID",
        "expected_condition": "Value must be valid",
        "reasoning": "Condition satisfied",
        "severity": "NONE",
    })

    response = client.get(
        f"/api/v1/applications/{application_id}/validations"
    )

    assert response.status_code == 200
    assert response.json()[0]["passed"] is True


def test_validation_passed_false():
    application_id = "00000000-0000-0000-0000-000000000033"

    fake_supabase.database["validations"].append({
        "application_id": application_id,
        "rule_id": "RULE_FAIL",
        "passed": False,
        "extracted_value": "INVALID",
        "expected_condition": "Value must be valid",
        "reasoning": "Condition not satisfied",
        "severity": "HIGH",
    })

    response = client.get(
        f"/api/v1/applications/{application_id}/validations"
    )

    assert response.status_code == 200
    assert response.json()[0]["passed"] is False


def test_validation_passed_null():
    application_id = "00000000-0000-0000-0000-000000000034"

    fake_supabase.database["validations"].append({
        "application_id": application_id,
        "rule_id": "RULE_UNKNOWN",
        "passed": None,
        "extracted_value": None,
        "expected_condition": None,
        "reasoning": None,
        "severity": None,
    })

    response = client.get(
        f"/api/v1/applications/{application_id}/validations"
    )

    assert response.status_code == 200

    data = response.json()

    assert data[0]["rule_id"] == "RULE_UNKNOWN"
    assert data[0]["passed"] is None
    assert data[0]["extracted_value"] is None
    assert data[0]["expected_condition"] is None
    assert data[0]["reasoning"] is None
    assert data[0]["severity"] is None
# ============================================================
# PROCESS TESTS
# ============================================================

def test_process_application_success():
    application_id = "00000000-0000-0000-0000-000000000040"

    fake_supabase.database["applications"].append({
        "id": application_id,
        "student_id": "00000000-0000-0000-0000-000000000001",
        "scheme_id": "PRE_MATRIC",
        "status": "SUBMITTED",
        "risk_score": None,
        "created_at": "2026-09-25T00:00:00Z",
        "updated_at": "2026-09-25T00:00:00Z",
    })

    response = client.post(
        f"/api/v1/applications/{application_id}/process"
    )

    assert response.status_code == 202

    data = response.json()

    assert data["id"] == application_id
    assert data["status"] == "PROCESSING"


def test_process_application_not_found():
    application_id = "00000000-0000-0000-0000-000000000041"

    response = client.post(
        f"/api/v1/applications/{application_id}/process"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Application not found"
def test_ocr_pipeline_readable(monkeypatch):
    application_id = "11111111-1111-1111-1111-111111111111"
    document_id = "22222222-2222-2222-2222-222222222222"

    fake_supabase.database["applications"].append(
        {
            "id": application_id,
            "student_id": "33333333-3333-3333-3333-333333333333",
            "scheme_id": "PRE_MATRIC",
            "status": "SUBMITTED",
            "risk_score": None,
            "created_at": "2026-01-01T00:00:00+00:00",
            "updated_at": "2026-01-01T00:00:00+00:00",
        }
    )

    storage_path = (
        f"applications/{application_id}/"
        f"{document_id}-INCOME_CERTIFICATE.pdf"
    )

    fake_supabase.database["documents"].append(
        {
            "id": document_id,
            "application_id": application_id,
            "document_type": "INCOME_CERTIFICATE",
            "storage_path": storage_path,
            "ocr_status": "PROCESSING",
        }
    )

    fake_supabase.storage_data[storage_path] = {
        "bytes": b"fake pdf content",
    }

    monkeypatch.setattr(
        ocr_pipeline,
        "run_ocr",
        lambda file_bytes, filename: "Annual family income: Rs. 200000",
    )

    ocr_pipeline.process_application_documents(
        UUID(application_id),
        fake_supabase,
    )

    document = fake_supabase.database["documents"][0]
    application = fake_supabase.database["applications"][0]

    assert document["ocr_status"] == "READABLE"
    assert application["status"] == "PROCESSING"


def test_ocr_pipeline_unreadable(monkeypatch):
    application_id = "44444444-4444-4444-4444-444444444444"
    document_id = "55555555-5555-5555-5555-555555555555"

    fake_supabase.database["applications"].append(
        {
            "id": application_id,
            "student_id": "66666666-6666-6666-6666-666666666666",
            "scheme_id": "PRE_MATRIC",
            "status": "SUBMITTED",
            "risk_score": None,
            "created_at": "2026-01-01T00:00:00+00:00",
            "updated_at": "2026-01-01T00:00:00+00:00",
        }
    )

    storage_path = (
        f"applications/{application_id}/"
        f"{document_id}-INCOME_CERTIFICATE.pdf"
    )

    fake_supabase.database["documents"].append(
        {
            "id": document_id,
            "application_id": application_id,
            "document_type": "INCOME_CERTIFICATE",
            "storage_path": storage_path,
            "ocr_status": "PROCESSING",
        }
    )

    fake_supabase.storage_data[storage_path] = {
        "bytes": b"fake pdf content",
    }

    def fake_ocr(file_bytes, filename):
        raise ocr_pipeline.OCRProcessingError(
            "OCR failed"
        )

    monkeypatch.setattr(
        ocr_pipeline,
        "run_ocr",
        fake_ocr,
    )

    ocr_pipeline.process_application_documents(
        UUID(application_id),
        fake_supabase,
    )

    document = fake_supabase.database["documents"][0]
    application = fake_supabase.database["applications"][0]

    assert document["ocr_status"] == "UNREADABLE"
    assert application["status"] == "DEFICIENT"