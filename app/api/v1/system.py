from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.core.database import get_db
from app.services import system_health_service
from app.ingestion.registry import registry # Import the registry to get the summary

router = APIRouter(
    prefix="/system",
    tags=["System Health"]
)

@router.get("/health")
def get_health(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Provides a high-level status of the system, including API, database,
    and data freshness.
    """
    last_summary = registry.last_summary
    return system_health_service.get_system_health(db, last_summary)

@router.get("/metrics")
def get_metrics(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Returns key operational metrics about the data platform.
    """
    last_summary = registry.last_summary
    return system_health_service.get_system_metrics(db, last_summary)

@router.get("/ingestion_status")
def get_ingestion_status() -> Dict[str, Any]:
    """
    Provides a detailed summary of the last ingestion run across all sources.
    """
    last_summary = registry.last_summary
    return system_health_service.get_ingestion_status(last_summary)
