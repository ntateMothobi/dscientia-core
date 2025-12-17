from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.core.database import get_db
from app.services import system_health_service

router = APIRouter(
    prefix="/health",
    tags=["System Health"]
)

@router.get("/", response_model=Dict[str, Any])
def get_system_health(db: Session = Depends(get_db)):
    """
    Provides a comprehensive health check of the entire system, including
    database connectivity, cache status, and ingestion service readiness.
    """
    return system_health_service.get_full_system_health(db)
