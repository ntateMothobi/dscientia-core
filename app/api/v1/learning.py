from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any, List
import json

from app.core.database import get_db
from app.core.security import get_current_user_role, UserRole, require_roles, UserContext, get_current_user
from app.models.decision_feedback import DecisionFeedback, DecisionFeedbackType
from app.schemas.decision_feedback import DecisionFeedbackCreate, DecisionFeedbackRead
from app.models.learning_review import LearningReview
from app.schemas.learning_review import LearningReviewRead, LearningReviewUpdate
from app.services.audit_log_service import create_audit_log_entry
from app.schemas.audit_log import AuditLogCreate
from app.services.learning_service import (
    aggregate_learning_insights, 
    create_learning_review_proposal, 
    get_pending_reviews, 
    process_learning_review,
    ReviewStatus
)

router = APIRouter(
    prefix="/learning",
    tags=["Learning"]
)

@router.post("/feedback", response_model=DecisionFeedbackRead, status_code=status.HTTP_201_CREATED)
def submit_decision_feedback(
    feedback: DecisionFeedbackCreate,
    db: Session = Depends(get_db),
    role: UserRole = Depends(get_current_user_role)
):
    """
    Records human feedback on a decision recommendation.
    """
    try:
        db_feedback = DecisionFeedback(
            recommendation_id=feedback.recommendation_id,
            recommendation_title=feedback.recommendation_title,
            persona=role.value if role else "anonymous",
            decision=feedback.decision.value,
            reason=feedback.reason
        )
        db.add(db_feedback)
        db.commit()
        db.refresh(db_feedback)

        # Audit Log
        log_details = json.dumps({
            "recommendation_id": feedback.recommendation_id,
            "decision": feedback.decision.value,
            "reason": feedback.reason
        })
        
        audit_entry = AuditLogCreate(
            event_type="decision_feedback",
            decision=feedback.decision.value,
            details=log_details,
            persona=role.value if role else "anonymous"
        )
        create_audit_log_entry(db, audit_entry)

        return db_feedback

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit feedback: {str(e)}"
        )

@router.get("/insights")
def get_learning_insights_api(
    db: Session = Depends(get_db),
    role: UserRole = Depends(get_current_user_role)
):
    """
    Returns READ-ONLY insights derived from human feedback.
    """
    try:
        return aggregate_learning_insights(db)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve insights: {str(e)}"
        )

@router.post("/review/generate", response_model=LearningReviewRead)
def generate_review_proposal(
    db: Session = Depends(get_db),
    role: UserRole = Depends(require_roles([UserRole.FOUNDER, UserRole.OPS_CRM]))
):
    """
    Manually triggers generation of a learning review proposal.
    """
    return create_learning_review_proposal(db)

@router.get("/reviews/pending", response_model=List[LearningReviewRead])
def get_pending_reviews_api(
    db: Session = Depends(get_db),
    role: UserRole = Depends(require_roles([UserRole.FOUNDER, UserRole.OPS_CRM]))
):
    return get_pending_reviews(db)

@router.post("/review/{review_id}/approve", response_model=LearningReviewRead)
def approve_learning_review(
    review_id: int,
    notes: str = None,
    db: Session = Depends(get_db),
    user: UserContext = Depends(get_current_user)
):
    if user.role not in [UserRole.FOUNDER, UserRole.OPS_CRM]:
        raise HTTPException(status_code=403, detail="Not authorized")

    review = process_learning_review(db, review_id, ReviewStatus.APPROVED, user.user_id, notes)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    # Audit Log
    log_details = json.dumps({
        "review_id": review_id,
        "action": "APPROVED",
        "notes": notes,
        "metrics_snapshot": review.metrics
    })
    audit_entry = AuditLogCreate(
        event_type="learning_review_approved",
        decision="APPROVED",
        details=log_details,
        persona=user.role.value
    )
    create_audit_log_entry(db, audit_entry)

    return review

@router.post("/review/{review_id}/reject", response_model=LearningReviewRead)
def reject_learning_review(
    review_id: int,
    notes: str = None,
    db: Session = Depends(get_db),
    user: UserContext = Depends(get_current_user)
):
    if user.role not in [UserRole.FOUNDER, UserRole.OPS_CRM]:
        raise HTTPException(status_code=403, detail="Not authorized")

    review = process_learning_review(db, review_id, ReviewStatus.REJECTED, user.user_id, notes)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    # Audit Log
    log_details = json.dumps({
        "review_id": review_id,
        "action": "REJECTED",
        "notes": notes
    })
    audit_entry = AuditLogCreate(
        event_type="learning_review_rejected",
        decision="REJECTED",
        details=log_details,
        persona=user.role.value
    )
    create_audit_log_entry(db, audit_entry)

    return review
