from pydantic import BaseModel, Field
from typing import Dict

class LeadAnalytics(BaseModel):
    """
    Analytics data for Leads.
    Provides a high-level overview of lead volume and pipeline status.
    """
    total_leads: int = Field(..., description="Total number of leads in the system")
    by_status: Dict[str, int] = Field(..., description="Breakdown of leads by their current status (e.g., new, contacted)")

class FollowupAnalytics(BaseModel):
    """
    Analytics data for Follow-ups.
    Tracks agent activity and interaction outcomes.
    """
    total_followups: int = Field(..., description="Total number of follow-up interactions recorded")
    by_status: Dict[str, int] = Field(..., description="Breakdown of follow-ups by their status (e.g., pending, closed)")

class DashboardAnalytics(BaseModel):
    """
    Main Dashboard Analytics Schema.
    Aggregates all key metrics into a single response for the frontend dashboard.
    """
    leads: LeadAnalytics
    followups: FollowupAnalytics
