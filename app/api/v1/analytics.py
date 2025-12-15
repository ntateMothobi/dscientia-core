from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.analytics import DashboardAnalytics
from app.services import analytics_service

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)

@router.get(
    "/dashboard",
    response_model=DashboardAnalytics,
    summary="Get dashboard analytics"
)
def get_dashboard_metrics(db: Session = Depends(get_db)):
    """
    Retrieve aggregated business metrics for the main dashboard.
    Includes total counts and status breakdowns for leads and follow-ups.
    """
    return analytics_service.get_dashboard_analytics(db)
