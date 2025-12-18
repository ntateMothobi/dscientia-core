from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.core.database import get_db
from app.schemas.lead import LeadAnalytics
from app.schemas.audit_log import AuditLogCreate
from app.services.lead_service import get_leads_with_analytics, get_all_leads
from app.services.persona_insight_service import generate_all_persona_insights
from app.services.trust_service import calculate_data_freshness
from app.services.data_quality_service import analyze_data_quality
from app.services.insight_quality_service import calculate_insight_quality
from app.services.confidence_service import calculate_system_confidence
from app.services.audit_log_service import create_audit_log_entry
from app.core.security import get_current_user_role, UserRole

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)

@router.get("/confidence", response_model=Dict[str, Any])
def get_system_confidence(
    db: Session = Depends(get_db),
    role: UserRole = Depends(get_current_user_role)
):
    """
    Calculates and returns the system's overall confidence score.
    This score reflects the trustworthiness of the data and insights.
    """
    confidence_data = calculate_system_confidence(db)
    
    # Audit the confidence calculation event
    log_details = (
        f"Score: {confidence_data['confidence_score']}. "
        f"Metrics: {confidence_data['metrics']}"
    )
    
    log_entry = AuditLogCreate(
        event_type="confidence_evaluated",
        decision=confidence_data['confidence_level'],
        details=log_details,
        persona=role.value if role else "anonymous"
    )
    create_audit_log_entry(db, log_entry)
    
    return confidence_data

@router.get("/risk_profile", response_model=List[LeadAnalytics])
def get_lead_risk_profile(db: Session = Depends(get_db)):
    # ... (existing code)
    pass

@router.get("/data_freshness", response_model=Dict[str, Any])
def get_data_freshness(db: Session = Depends(get_db)):
    # ... (existing code)
    pass

@router.get("/data_quality", response_model=Dict[str, Any])
def get_data_quality(db: Session = Depends(get_db)):
    # ... (existing code)
    pass

@router.get("/insight_quality", response_model=Dict[str, Any])
def get_insight_quality(db: Session = Depends(get_db)):
    """
    Calculates and returns the quality score for the generated insights.
    """
    leads = get_all_leads(db)
    quality_report = calculate_insight_quality(leads)
    return quality_report

@router.get("/persona_insights", response_model=str)
def get_persona_insights(persona: str, db: Session = Depends(get_db)):
    """
    Generates and returns a persona-specific insight string.
    """
    leads = get_all_leads(db)
    analytics_data = get_leads_with_analytics(db)
    insights = generate_all_persona_insights(db, analytics_data, leads)
    persona_map = {
        "founder": "Founder",
        "sales": "Sales Manager",
        "ops": "Operations Manager"
    }
    insight_key = persona_map.get(persona.lower())
    if not insight_key or insight_key not in insights:
        raise HTTPException(status_code=404, detail=f"Persona '{persona}' not found.")
    return insights[insight_key]
