from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client

from app.core.supabase_client import get_supabase
from app.schemas.admin_review import (
    AdminReviewDecision,
    AdminReviewRequest,
)
from app.schemas.application import (
    ApplicationResponse,
    ApplicationStatus,
)
from app.services.workflow.workflow_service import (
    transition_application,
)


router = APIRouter()


@router.post(
    "/applications/{application_id}/review",
    response_model=ApplicationResponse,
    status_code=status.HTTP_200_OK,
)
def review_application(
    application_id: UUID,
    payload: AdminReviewRequest,
    supabase: Client = Depends(get_supabase),
):
    # --------------------------------------------------------
    # Verify application exists
    # --------------------------------------------------------

    try:
        application_result = (
            supabase.table("applications")
            .select(
                "id, student_id, scheme_id, status, "
                "risk_score, created_at, updated_at"
            )
            .eq("id", str(application_id))
            .limit(1)
            .execute()
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Application lookup failed",
        )

    if not application_result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    application = application_result.data[0]

    current_status = ApplicationStatus(
        application["status"]
    )

    # --------------------------------------------------------
    # Only flagged applications enter admin review
    # --------------------------------------------------------

    try:
        transition_application(
            application_id=application_id,
            from_status=current_status,
            to_status=ApplicationStatus.ADMIN_REVIEW,
            reason="Application requires administrative review.",
            supabase=supabase,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    # --------------------------------------------------------
    # Map admin decision to final application status
    # --------------------------------------------------------

    decision_to_status = {
        AdminReviewDecision.APPROVE: ApplicationStatus.APPROVED,
        AdminReviewDecision.REJECT: ApplicationStatus.REJECTED,
        AdminReviewDecision.REQUEST_RESUBMISSION: (
            ApplicationStatus.DEFICIENT
        ),
    }

    target_status = decision_to_status[payload.decision]

    # --------------------------------------------------------
    # ADMIN_REVIEW -> final decision
    # --------------------------------------------------------

    try:
        transition_application(
            application_id=application_id,
            from_status=ApplicationStatus.ADMIN_REVIEW,
            to_status=target_status,
            reason=payload.reason,
            supabase=supabase,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    # --------------------------------------------------------
    # Update timestamp
    # --------------------------------------------------------

    now = datetime.now(timezone.utc)

    try:
        timestamp_result = (
            supabase.table("applications")
            .update(
                {
                    "updated_at": now.isoformat(),
                }
            )
            .eq("id", str(application_id))
            .execute()
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Application review could not be completed",
        )

    # --------------------------------------------------------
    # Return final application
    # --------------------------------------------------------

    if timestamp_result.data:
        return timestamp_result.data[0]

    return {
        **application,
        "status": target_status.value,
        "updated_at": now.isoformat(),
    }