from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.lead import Lead, LeadCreate
from app.services import lead_service

router = APIRouter(
    prefix="/leads",
    tags=["Leads"]
)

@router.post(
    "/", 
    response_model=Lead, 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new lead"
)
def create_lead(lead: LeadCreate, db: Session = Depends(get_db)):
    """
    Create a new lead.
    """
    return lead_service.create_lead(db=db, lead_in=lead)

@router.get(
    "/", 
    response_model=List[Lead],
    summary="Get all leads"
)
def get_leads(db: Session = Depends(get_db)):
    """
    Retrieves a list of all leads.
    """
    return lead_service.get_all_leads(db=db)
