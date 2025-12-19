from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import json

from app.core.database import get_db
from app.schemas.decision import DecisionRecommendation
from app.services.decision_engine import generate_recommendations, filter_recommendations_by_persona, explain_decision
from app.services.confidence_service import get_system_confidence
from app.services.analytics_service import get_key_metrics
from app.services.audit_log_service import create_audit_log_entry
from app.schemas.audit_log import AuditLogCreate
from app.core.security import get_current_user_role, UserRole

router = APIRouter(
    prefix="/decisions",
    tags=["Decisions"]
)

@router.get("/recommendations", response_model=List[DecisionRecommendation])
def get_decision_recommendations(
    db: Session = Depends(get_db),
    role: UserRole = Depends(get_current_user_role)
):
    """
    Generates and filters actionable recommendations based on the user's persona.
    """
    try:
        confidence_data = get_system_confidence(db)
        analytics_metrics = get_key_metrics(db)
        
        all_recommendations = generate_recommendations(
            analytics_metrics=analytics_metrics,
            confidence_score=confidence_data.score
        )
        
        for rec in all_recommendations:
            # This is a simplified example; in a real system, you'd pass the actual rule results
            # that led to THIS specific recommendation.
            from app.services.decision_engine import check_confidence_threshold, check_policy_violation, check_data_completeness
            rule_results = [
                check_confidence_threshold(confidence_data.score),
                check_policy_violation(analytics_metrics),
                check_data_completeness(analytics_metrics)
            ]
            rec.explanation = explain_decision(rec, rule_results)

        filtered_recommendations = filter_recommendations_by_persona(all_recommendations, role)
        
        for rec in filtered_recommendations:
            log_details = json.dumps({
                "title": rec.title,
                "priority": rec.priority.value,
                "confidence": rec.confidence,
                "explanation": rec.explanation
            })
            
            log_entry = AuditLogCreate(
                event_type="decision_generated",
                decision=rec.recommendation[:255],
                details=log_details,
                persona=role.value if role else "anonymous"
            )
            create_audit_log_entry(db, log_entry)
        
        return filtered_recommendations

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate recommendations: {str(e)}"
        )
