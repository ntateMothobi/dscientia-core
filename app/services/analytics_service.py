from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict

from app.models.lead import Lead
from app.models.followup import Followup
from app.schemas.analytics import LeadAnalytics, FollowupAnalytics, DashboardAnalytics

def get_lead_analytics(db: Session) -> LeadAnalytics:
    """
    Aggregates lead metrics: total count and breakdown by status.
    """
    total_leads = db.query(Lead).count()
    
    # Group by status and count
    status_counts = db.query(Lead.status, func.count(Lead.status))\
                      .group_by(Lead.status)\
                      .all()
    
    # Convert list of tuples [('new', 5), ('contacted', 3)] to dict
    by_status = {status: count for status, count in status_counts}
    
    return LeadAnalytics(
        total_leads=total_leads,
        by_status=by_status
    )

def get_followup_analytics(db: Session) -> FollowupAnalytics:
    """
    Aggregates follow-up metrics: total count and breakdown by status.
    """
    total_followups = db.query(Followup).count()
    
    # Group by status and count
    status_counts = db.query(Followup.status, func.count(Followup.status))\
                      .group_by(Followup.status)\
                      .all()
    
    # Convert list of tuples to dict
    by_status = {status: count for status, count in status_counts}
    
    return FollowupAnalytics(
        total_followups=total_followups,
        by_status=by_status
    )

def get_dashboard_analytics(db: Session) -> DashboardAnalytics:
    """
    Combines lead and follow-up analytics into a single dashboard view.
    """
    leads_data = get_lead_analytics(db)
    followups_data = get_followup_analytics(db)
    
    return DashboardAnalytics(
        leads=leads_data,
        followups=followups_data
    )
