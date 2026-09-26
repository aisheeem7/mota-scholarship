from app.schemas.application import ApplicationStatus


ALLOWED_TRANSITIONS = {
    ApplicationStatus.SUBMITTED: {
        ApplicationStatus.PROCESSING,
    },
    ApplicationStatus.PROCESSING: {
        ApplicationStatus.APPROVED,
        ApplicationStatus.DEFICIENT,
        ApplicationStatus.FLAGGED_FOR_REVIEW,
    },
    ApplicationStatus.DEFICIENT: {
        ApplicationStatus.RESUBMITTED,
    },
    ApplicationStatus.RESUBMITTED: {
        ApplicationStatus.PROCESSING,
    },
    ApplicationStatus.FLAGGED_FOR_REVIEW: {
        ApplicationStatus.ADMIN_REVIEW,
    },
    ApplicationStatus.ADMIN_REVIEW: {
        ApplicationStatus.APPROVED,
        ApplicationStatus.REJECTED,
        ApplicationStatus.DEFICIENT,
    },
}


def is_transition_allowed(
    from_status: ApplicationStatus,
    to_status: ApplicationStatus,
) -> bool:
    """
    Check whether a workflow transition is allowed.
    """

    return to_status in ALLOWED_TRANSITIONS.get(
        from_status,
        set(),
    )


def transition_application(
    *,
    application_id,
    from_status: ApplicationStatus,
    to_status: ApplicationStatus,
    reason: str | None,
    supabase,
) -> None:
    """
    Persist a workflow transition and update the application.

    The transition is recorded in workflow_events before the
    application status is updated.
    """

    if not is_transition_allowed(
        from_status,
        to_status,
    ):
        raise ValueError(
            f"Invalid workflow transition: "
            f"{from_status.value} -> {to_status.value}"
        )

    supabase.table("workflow_events").insert(
        {
            "application_id": str(application_id),
            "from_status": from_status.value,
            "to_status": to_status.value,
            "reason": reason,
        }
    ).execute()

    supabase.table("applications").update(
        {
            "status": to_status.value,
        }
    ).eq(
        "id",
        str(application_id),
    ).execute()