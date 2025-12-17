from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.services.audit_log_service import log_persona_insight_generation
from app.core.cache import simple_cache
from app.services.insight_quality_service import calculate_insight_quality

@simple_cache(ttl=300)
def generate_all_persona_insights(db: Session, analytics_data: List[Dict[str, Any]], leads: List[Any]) -> Dict[str, str]:
    """
    Generates a dictionary of formatted insight strings for all personas and logs the events.
    This function is cached.
    """
    if not analytics_data:
        return {
            "Founder": "No lead data available to generate insights.",
            "Sales Manager": "No lead data available to generate insights.",
            "Operations Manager": "No lead data available to generate insights."
        }

    insights = {
        "Founder": _generate_founder_insights(analytics_data),
        "Sales Manager": _generate_sales_manager_insights(analytics_data),
        "Operations Manager": _generate_operations_manager_insights(analytics_data),
    }

    # Calculate insight quality
    quality_report = calculate_insight_quality(leads)

    # Audit logging with quality score
    for persona, insight_text in insights.items():
        log_persona_insight_generation(
            db=db,
            persona=persona,
            inputs={"lead_count": len(analytics_data)},
            decision={"insight": insight_text},
            confidence=quality_report.get("score")
        )

    return insights

def _generate_founder_insights(data: List[Dict[str, Any]]) -> str:
    # ... (existing code)
    pass

def _generate_sales_manager_insights(data: List[Dict[str, Any]]) -> str:
    # ... (existing code)
    pass

def _generate_operations_manager_insights(data: List[Dict[str, Any]]) -> str:
    # ... (existing code)
    pass
