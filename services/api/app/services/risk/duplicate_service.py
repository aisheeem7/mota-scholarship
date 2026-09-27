from uuid import UUID

from supabase import Client

from app.schemas.application import ApplicationStatus


ACTIVE_DUPLICATE_STATUSES = {
    ApplicationStatus.SUBMITTED.value,
    ApplicationStatus.PROCESSING.value,
    ApplicationStatus.DEFICIENT.value,
    ApplicationStatus.RESUBMITTED.value,
    ApplicationStatus.FLAGGED_FOR_REVIEW.value,
    ApplicationStatus.ADMIN_REVIEW.value,
    ApplicationStatus.APPROVED.value,
}


def has_duplicate_application(
    *,
    student_id: str,
    scheme_id: str,
    application_id: UUID,
    supabase: Client,
) -> bool:
    """
    Detect another active application for the same student and scheme.

    The current application is excluded from the duplicate check.
    Rejected applications are not treated as duplicates.
    """

    result = (
        supabase.table("applications")
        .select("id, status")
        .eq("student_id", str(student_id))
        .eq("scheme_id", scheme_id)
        .execute()
    )

    rows = result.data or []

    current_application_id = str(application_id)

    return any(
        str(row.get("id")) != current_application_id
        and row.get("status") in ACTIVE_DUPLICATE_STATUSES
        for row in rows
    )