from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
import time

from app.models.lead import Lead
from app.models.followup import Followup

_system_start_time = time.time()

def get_system_health(db: Session, last_ingestion_summary: Optional[Dict]) -> Dict[str, Any]:
    """
    Determines the overall system health based on DB status and ingestion results.
    """
    uptime_seconds = int(time.time() - _system_start_time)
    
    try:
        db.query(Lead).first()
    except Exception:
        return {
            "status": "unhealthy",
            "reason": "Database connection failed.",
            "uptime_seconds": uptime_seconds,
            "api_version": "0.3.0",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    if last_ingestion_summary:
        last_run_dt = datetime.fromisoformat(last_ingestion_summary.get("run_at", ""))
        if (datetime.now(timezone.utc) - last_run_dt) > timedelta(days=1):
            return {
                "status": "degraded",
                "reason": "Data is stale (no successful ingestion in over 24 hours).",
                "uptime_seconds": uptime_seconds,
                "api_version": "0.3.0",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        for source, results in last_ingestion_summary.get("sources", {}).items():
            if results.get("status") == "failure":
                return {
                    "status": "degraded",
                    "reason": f"Source '{source}' failed during the last ingestion.",
                    "uptime_seconds": uptime_seconds,
                    "api_version": "0.3.0",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }

    return {
        "status": "healthy",
        "reason": "All systems operational.",
        "uptime_seconds": uptime_seconds,
        "api_version": "0.3.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

def get_system_metrics(db: Session, last_ingestion_summary: Optional[Dict]) -> Dict[str, Any]:
    """
    Gathers key operational metrics.
    """
    leads_count = db.query(Lead).count()
    followups_count = db.query(Followup).count()
    
    failed_ingestions = 0
    if last_ingestion_summary:
        for results in last_ingestion_summary.get("sources", {}).values():
            if results.get("status") == "failure":
                failed_ingestions += 1

    return {
        "leads_count": leads_count,
        "followups_count": followups_count,
        "last_ingestion_at": last_ingestion_summary.get("run_at") if last_ingestion_summary else None,
        "failed_ingestions_last_24h": failed_ingestions,
        "avg_ingestion_duration_sec": 5 # Mocked value
    }

def get_ingestion_status(last_ingestion_summary: Optional[Dict]) -> Dict[str, Any]:
    """
    Returns the summary of the last ingestion run.
    """
    if not last_ingestion_summary:
        return {
            "last_run": None,
            "overall_status": "not_run_yet",
            "sources": {}
        }
    
    statuses = [results.get("status") for results in last_ingestion_summary.get("sources", {}).values()]
    if "failure" in statuses:
        overall = "failed"
    elif any(s == "partial" for s in statuses):
        overall = "partial"
    else:
        overall = "success"

    return {
        "last_run": last_ingestion_summary.get("run_at"),
        "overall_status": overall,
        "sources": last_ingestion_summary.get("sources", {})
    }
