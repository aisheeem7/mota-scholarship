"""Regression tests for safe API handling of Supabase application insert failures."""

from uuid import UUID

from fastapi.testclient import TestClient

from app.core.supabase_client import get_supabase
from app.main import app


class FailingInsertQuery:
    def insert(self, data):
        return self

    def execute(self):
        raise RuntimeError(
            "simulated PostgREST insert failure: permission denied"
        )


class FailingSupabase:
    def table(self, table_name):
        assert table_name == "applications"
        return FailingInsertQuery()


def test_create_application_hides_database_error_and_logs_it(caplog):
    fake_supabase = FailingSupabase()

    def override_get_supabase():
        return fake_supabase

    app.dependency_overrides[get_supabase] = override_get_supabase

    try:
        client = TestClient(app)

        with caplog.at_level("ERROR"):
            response = client.post(
                "/api/v1/applications",
                json={
                    "student_id": str(
                        UUID("00000000-0000-0000-0000-000000000001")
                    ),
                    "scheme_id": "PRE_MATRIC",
                },
            )

        assert response.status_code == 500
        assert response.json() == {
            "detail": "Application creation failed"
        }

        assert "simulated PostgREST insert failure" in caplog.text
        assert "Application creation failed for application_id=" in (
            caplog.text
        )

        # Internal exception details must not cross the API boundary.
        assert "permission denied" not in response.text

    finally:
        app.dependency_overrides.pop(
            get_supabase,
            None,
        )
