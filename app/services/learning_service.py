from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any, List
from datetime import datetime

from app.models.decision_feedback import DecisionFeedback, DecisionFeedbackType
from app.models.learning_review import LearningReview, ReviewStatus
from app.schemas.learning_review import LearningReviewCreate, LearningReviewUpdate
from app.core.security import UserRole

def aggregate_learning_insights(db: Session) -> Dict[str, Any]:
    """
    Aggregates insights from DecisionFeedback table.
    """
    total_decisions = db.query(func.count(DecisionFeedback.id)).scalar()
    
    # Approval Rate by Persona
    personas = db.query(DecisionFeedback.persona).distinct().all()
    approval_rate_by_persona = {}
    for p in personas:
        persona_name = p[0]
        p_total = db.query(func.count(DecisionFeedback.id)).filter(
            DecisionFeedback.persona == persona_name
        ).scalar()
        p_approved = db.query(func.count(DecisionFeedback.id)).filter(
            DecisionFeedback.persona == persona_name,
            DecisionFeedback.decision == DecisionFeedbackType.APPROVED.value
        ).scalar()
        if p_total > 0:
            approval_rate_by_persona[persona_name] = round((p_approved / p_total) * 100, 2)

    # Override Frequency
    overrides = db.query(func.count(DecisionFeedback.id)).filter(
        DecisionFeedback.decision == DecisionFeedbackType.OVERRIDDEN.value
    ).scalar()
    override_frequency = 0.0
    if total_decisions > 0:
        override_frequency = round((overrides / total_decisions) * 100, 2)

    # Confidence vs Rejection (Simplified Proxy)
    # In a real system, we'd join with Recommendation table. 
    # Here we just count rejections as a proxy for low confidence alignment.
    rejections = db.query(func.count(DecisionFeedback.id)).filter(
        DecisionFeedback.decision == DecisionFeedbackType.REJECTED.value
    ).scalar()
    rejection_rate = 0.0
    if total_decisions > 0:
        rejection_rate = round((rejections / total_decisions) * 100, 2)

    return {
        "total_decisions": total_decisions,
        "approval_rate_by_persona": approval_rate_by_persona,
        "override_frequency": override_frequency,
        "rejection_rate": rejection_rate,
        "rule_sensitivity_index": "N/A (Requires Rule Engine Metadata)" 
    }

def create_learning_review_proposal(db: Session) -> LearningReview:
    """
    Creates a new LearningReview entry based on current insights.
    Ideally run periodically, but here triggered on demand for demo.
    """
    insights = aggregate_learning_insights(db)
    
    # Check if there is already a pending review with similar metrics to avoid spam
    # For simplicity, we just create a new one if no pending exists
    existing = db.query(LearningReview).filter(LearningReview.status == ReviewStatus.PENDING.value).first()
    if existing:
        return existing

    review = LearningReview(
        insight_type="Weekly Aggregation",
        summary=f"Review of {insights['total_decisions']} decisions. Rejection Rate: {insights['rejection_rate']}%",
        metrics=insights,
        status=ReviewStatus.PENDING.value
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review

def get_pending_reviews(db: Session) -> List[LearningReview]:
    return db.query(LearningReview).filter(LearningReview.status == ReviewStatus.PENDING.value).all()

def process_learning_review(
    db: Session, 
    review_id: int, 
    status: ReviewStatus, 
    reviewer: str, 
    notes: str
) -> LearningReview:
    review = db.query(LearningReview).filter(LearningReview.id == review_id).first()
    if not review:
        return None
    
    review.status = status.value
    review.reviewer = reviewer
    review.reviewed_at = datetime.utcnow()
    review.notes = notes
    
    db.commit()
    db.refresh(review)
    return review
