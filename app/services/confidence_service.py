from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.services.data_quality_service import analyze_data_quality
from app.services.trust_service import calculate_data_freshness
from app.services.lead_service import get_all_leads
from app.ingestion.registry import registry

def calculate_system_confidence(db: Session) -> Dict[str, Any]:
    """
    Calculates the overall system confidence score based on data quality,
    freshness, and ingestion status.
    """
    leads = get_all_leads(db)
    
    # 1. Get Data Completeness
    quality_report = analyze_data_quality(leads)
    completeness_score = quality_report.get("avg_completeness", 0)
    
    # 2. Get Data Freshness
    freshness_report = calculate_data_freshness(leads)
    freshness_score = freshness_report.get("freshness_score", 0)
    
    # 3. Get Ingestion Status
    ingestion_summary = registry.last_summary or {}
    total_records = ingestion_summary.get("total_processed", 0)
    failed_records = ingestion_summary.get("total_failed", 0)
    ingestion_success_rate = ((total_records - failed_records) / total_records) * 100 if total_records > 0 else 100

    # --- Scoring Logic ---
    # Weighted average: Completeness (40%), Freshness (40%), Ingestion (20%)
    final_score = (completeness_score * 0.4) + (freshness_score * 0.4) + (ingestion_success_rate * 0.2)
    final_score = round(final_score, 2)

    # --- Signal Generation ---
    signals = []
    if freshness_score >= 80:
        signals.append("✅ Data is up-to-date.")
    elif freshness_score >= 60:
        signals.append("⚠️ Data is a few days old.")
    else:
        signals.append("🔥 Data is stale. Consider running ingestion.")

    if completeness_score >= 90:
        signals.append("✅ Lead data is highly complete.")
    elif completeness_score >= 70:
        signals.append("⚠️ Some optional lead fields are missing.")
    else:
        signals.append("🔥 Critical lead data is missing, reducing insight quality.")

    if ingestion_success_rate < 100:
        signals.append(f"🔥 {failed_records} records failed during the last ingestion.")

    # --- Confidence Level ---
    if final_score >= 85:
        level = "High"
    elif final_score >= 60:
        level = "Medium"
    else:
        level = "Low"
        
    return {
        "confidence_level": level,
        "confidence_score": final_score,
        "signals": signals,
        "metrics": {
            "completeness_score": completeness_score,
            "freshness_score": freshness_score,
            "ingestion_success_rate": round(ingestion_success_rate, 2)
        }
    }
