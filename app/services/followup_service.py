from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List

from app.models.followup import Followup
from app.models.lead import Lead
from app.schemas.followup import FollowupCreate

def create_followup(db: Session, followup_in: FollowupCreate) -> Followup:
    """Create a new follow-up record for a lead."""
    
    # 1. Validate that the lead exists
    lead = db.query(Lead).filter(Lead.id == followup_in.lead_id).first()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lead with id {followup_in.lead_id} not found."
        )
        
    # 2. Create the Followup model instance
    db_followup = Followup(**followup_in.model_dump())
    
    # 3. Add to session, commit, and refresh
    db.add(db_followup)
    db.commit()
    db.refresh(db_followup)
    
    return db_followup

def get_followups_by_lead(db: Session, lead_id: int) -> List[Followup]:
    """Get all follow-ups for a specific lead, ordered by most recent."""
    
    # Validate that the lead exists
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lead with id {lead_id} not found."
        )

    return db.query(Followup)\
             .filter(Followup.lead_id == lead_id)\
             .order_by(Followup.created_at.desc())\
             .all()
