from app.schemas.application import ApplicationStatus
from app.services.workflow.workflow_service import (
    is_transition_allowed,
    transition_application,
)


class FakeQuery:
    def __init__(self, database, table_name):
        self.database = database
        self.table_name = table_name
        self.insert_data = None
        self.update_data = None
        self.filters = {}

    def insert(self, data):
        self.insert_data = data
        return self

    def update(self, data):
        self.update_data = data
        return self

    def eq(self, field, value):
        self.filters[field] = value
        return self

    def execute(self):
        table = self.database.setdefault(
            self.table_name,
            [],
        )

        if self.insert_data is not None:
            row = dict(self.insert_data)
            table.append(row)
            return type(
                "Result",
                (),
                {"data": [row]},
            )()

        if self.update_data is not None:
            rows = table

            for field, value in self.filters.items():
                rows = [
                    row
                    for row in rows
                    if str(row.get(field))
                    == str(value)
                ]

            for row in rows:
                row.update(self.update_data)

            return type(
                "Result",
                (),
                {"data": rows},
            )()

        return type(
            "Result",
            (),
            {"data": table},
        )()


class FakeSupabase:
    def __init__(self):
        self.database = {
            "applications": [],
            "workflow_events": [],
        }

    def table(self, table_name):
        return FakeQuery(
            self.database,
            table_name,
        )


def test_submitted_to_processing_is_allowed():
    assert is_transition_allowed(
        ApplicationStatus.SUBMITTED,
        ApplicationStatus.PROCESSING,
    ) is True


def test_processing_to_flagged_for_review_is_allowed():
    assert is_transition_allowed(
        ApplicationStatus.PROCESSING,
        ApplicationStatus.FLAGGED_FOR_REVIEW,
    ) is True


def test_processing_to_deficient_is_allowed():
    assert is_transition_allowed(
        ApplicationStatus.PROCESSING,
        ApplicationStatus.DEFICIENT,
    ) is True


def test_deficient_to_resubmitted_is_allowed():
    assert is_transition_allowed(
        ApplicationStatus.DEFICIENT,
        ApplicationStatus.RESUBMITTED,
    ) is True


def test_resubmitted_to_processing_is_allowed():
    assert is_transition_allowed(
        ApplicationStatus.RESUBMITTED,
        ApplicationStatus.PROCESSING,
    ) is True


def test_flagged_to_admin_review_is_allowed():
    assert is_transition_allowed(
        ApplicationStatus.FLAGGED_FOR_REVIEW,
        ApplicationStatus.ADMIN_REVIEW,
    ) is True


def test_admin_review_to_approved_is_allowed():
    assert is_transition_allowed(
        ApplicationStatus.ADMIN_REVIEW,
        ApplicationStatus.APPROVED,
    ) is True


def test_invalid_transition_is_rejected():
    assert is_transition_allowed(
        ApplicationStatus.SUBMITTED,
        ApplicationStatus.APPROVED,
    ) is False


def test_transition_persists_workflow_event_and_status():
    supabase = FakeSupabase()

    application_id = (
        "11111111-1111-1111-1111-111111111111"
    )

    supabase.database["applications"].append(
        {
            "id": application_id,
            "status": ApplicationStatus.SUBMITTED.value,
        }
    )

    transition_application(
        application_id=application_id,
        from_status=ApplicationStatus.SUBMITTED,
        to_status=ApplicationStatus.PROCESSING,
        reason="Document processing started",
        supabase=supabase,
    )

    events = supabase.database["workflow_events"]
    applications = supabase.database["applications"]

    assert len(events) == 1

    assert events[0]["application_id"] == application_id
    assert events[0]["from_status"] == "SUBMITTED"
    assert events[0]["to_status"] == "PROCESSING"
    assert events[0]["reason"] == (
        "Document processing started"
    )

    assert applications[0]["status"] == "PROCESSING"


def test_invalid_transition_raises_value_error():
    supabase = FakeSupabase()

    application_id = (
        "22222222-2222-2222-2222-222222222222"
    )

    supabase.database["applications"].append(
        {
            "id": application_id,
            "status": ApplicationStatus.SUBMITTED.value,
        }
    )

    try:
        transition_application(
            application_id=application_id,
            from_status=ApplicationStatus.SUBMITTED,
            to_status=ApplicationStatus.APPROVED,
            reason="Invalid test transition",
            supabase=supabase,
        )
    except ValueError as exc:
        assert "Invalid workflow transition" in str(exc)
    else:
        raise AssertionError(
            "Expected ValueError for invalid transition"
        )