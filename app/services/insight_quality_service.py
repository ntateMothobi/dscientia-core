from typing import List, Dict, Any
from datetime import datetime, timezone
from app.models.lead import Lead
from app.services.data_quality_service import calculate_lead_completeness

# --- Scoring Weights ---
WEIGHTS = {
    "volume": 0.30,
    "completeness": 0.30,
    "time_coverage": 0.20,
    "source_diversity": 0.20
}

# --- Thresholds for Full Score ---
THRESHOLDS = {
    "volume": 20,
    "completeness": 85.0, # in percent
    "time_coverage": 14, # in days
    "source_diversity": 2
}

def calculate_insight_quality(leads: List[Lead]) -> Dict[str, Any]:
    """
    Calculates a confidence score for the generated analytics insights.
    """
    if not leads:
        return {
            "score": 0,
            "confidence_level": "Low",
            "drivers": [],
            "limitations": ["No lead data available to generate insights."]
        }

    # --- Factor Calculations ---
    
    # 1. Volume
    volume = len(leads)
    volume_score = min(volume / THRESHOLDS["volume"], 1.0)

    # 2. Completeness
    completeness_scores = [calculate_lead_completeness(lead) for lead in leads]
    avg_completeness = (sum(completeness_scores) / volume) * 100
    completeness_score = min(avg_completeness / THRESHOLDS["completeness"], 1.0)

    # 3. Time Coverage
    now = datetime.now(timezone.utc)
    lead_ages = [(now - lead.created_at.replace(tzinfo=timezone.utc)).days for lead in leads if lead.created_at]
    time_coverage = max(lead_ages) if lead_ages else 0
    time_coverage_score = min(time_coverage / THRESHOLDS["time_coverage"], 1.0)

    # 4. Source Diversity
    sources = {lead.source for lead in leads if lead.source}
    source_diversity = len(sources)
    source_diversity_score = min(source_diversity / THRESHOLDS["source_diversity"], 1.0)

    # --- Final Score ---
    final_score = (
        (volume_score * WEIGHTS["volume"]) +
        (completeness_score * WEIGHTS["completeness"]) +
        (time_coverage_score * WEIGHTS["time_coverage"]) +
        (source_diversity_score * WEIGHTS["source_diversity"])
    ) * 100
    
    final_score = int(final_score)

    # --- Confidence Level & Explanations ---
    drivers = []
    limitations = []

    if volume_score == 1.0:
        drivers.append(f"Sufficient lead volume ({volume} leads)")
    else:
        limitations.append(f"Low lead volume ({volume} of {THRESHOLDS['volume']} recommended)")

    if completeness_score == 1.0:
        drivers.append(f"High data completeness ({avg_completeness:.0f}%)")
    else:
        limitations.append(f"Incomplete data ({avg_completeness:.0f}% vs {THRESHOLDS['completeness']}% target)")

    if time_coverage_score == 1.0:
        drivers.append(f"Sufficient time coverage ({time_coverage} days)")
    else:
        limitations.append(f"Short time window ({time_coverage} of {THRESHOLDS['time_coverage']} days observed)")

    if source_diversity_score == 1.0:
        drivers.append(f"Diverse data sources ({source_diversity} sources)")
    else:
        limitations.append(f"Limited source diversity ({source_diversity} of {THRESHOLDS['source_diversity']} recommended)")

    if final_score >= 75:
        confidence_level = "High"
    elif final_score >= 50:
        confidence_level = "Medium"
    else:
        confidence_level = "Low"

    return {
        "score": final_score,
        "confidence_level": confidence_level,
        "drivers": drivers,
        "limitations": limitations
    }
