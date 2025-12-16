from sqlalchemy.orm import Session
from typing import List

from app.models.lead import Lead
from app.schemas.lead import LeadCreate

def create_lead(db: Session, lead_in: LeadCreate) -> Lead:
    """Create a new lead record."""
    db_lead = Lead(**lead_in.model_dump())
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead

def get_all_leads(db: Session) -> List[Lead]:
    """Get all lead records."""
    return db.query(Lead).all()
