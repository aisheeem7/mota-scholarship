from fastapi.testclient import TestClient

from app.core.supabase_client import get_supabase
from app.main import app


class FakeResult:
    def __init__(self, data):
        self.data = data


class FakeQuery:
    def __init__(self, database, table_name):
        self.database = database
        self.table_name = table_name
        self.filters = {}
        self.pending_insert = None

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

    def execute(self):
        table = self.database.setdefault(self.table_name, [])

        if self.pending_insert is not None:
            row = dict(self.pending_insert)
            table.append(row)
            return FakeResult([row])

        rows = table

        for field, value in self.filters.items():
            rows = [
                row for row in rows
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
        }
        self.storage_data = {}
        self.storage = FakeStorage(self.storage_data)

    def table(self, table_name):
        return FakeQuery(self.database, table_name)


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