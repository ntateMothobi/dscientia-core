from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import json
import logging

from app.core.database import get_db
from app.schemas.decision import DecisionRecommendation
from app.services.decision_engine import generate_recommendations, filter_recommendations_by_persona
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
    try:
        confidence_data = get_system_confidence(db)
        analytics_metrics = get_key_metrics(db)
        
        all_recommendations = generate_recommendations(
            analytics_metrics=analytics_metrics,
            confidence_score=confidence_data.score,
            persona=role
        )
        
        filtered_recommendations = filter_recommendations_by_persona(all_recommendations, role)
        
        for rec in filtered_recommendations:
            log_details = json.dumps({
                "title": rec.title,
                "priority": rec.priority.value,
                "confidence": rec.confidence,
                "explanation_summary": rec.explainability_summary
            })
            log_entry = AuditLogCreate(
                event_type="decision_generated",
                decision=rec.recommendation[:255],
                details=log_details,
                persona=role.value
            )
            create_audit_log_entry(db, log_entry)
        
        return filtered_recommendations

    except Exception as e:
        logging.error(f"Failed to generate recommendations: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while generating recommendations."
        )
