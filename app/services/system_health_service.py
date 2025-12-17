import time
from datetime import datetime, timezone
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError

from app.core.database import engine
from app.core import cache
from app.ingestion.registry import registry

# In-memory store for simple observability
_system_start_time = time.time()

def check_database_status(db: Session) -> str:
    """Checks if the database is connected and responsive."""
    try:
        # Perform a simple, fast query
        db.execute("SELECT 1")
        return "connected"
    except OperationalError:
        return "unreachable"
    except Exception:
        return "degraded"

def check_ingestion_services_status() -> Dict[str, str]:
    """Checks the status of all discovered ingestion sources."""
    available_sources = registry.get_available_sources()
    if not available_sources:
        return {"status": "degraded", "reason": "No ingestion sources discovered."}
    
    return {source: "ok" for source in available_sources}

def get_full_system_health(db: Session) -> Dict[str, Any]:
    """
    Aggregates health checks from all system components into a single report.
    """
    db_status = check_database_status(db)
    ingestion_status = check_ingestion_services_status()
    
    # Determine overall health
    overall_status = "healthy"
    if db_status != "connected":
        overall_status = "unhealthy"
    elif "degraded" in ingestion_status.values():
        overall_status = "degraded"

    # Get last ingestion timestamp from the registry
    last_ingestion_ts = None
    if registry.last_summary and "run_at" in registry.last_summary:
        last_ingestion_ts = registry.last_summary["run_at"]

    return {
        "status": overall_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": db_status,
        "cache": "active" if cache._cache else "inactive",
        "ingestion_services": ingestion_status,
        "last_ingestion": last_ingestion_ts
    }
