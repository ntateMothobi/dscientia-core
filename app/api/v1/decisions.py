from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.decision_proposal import DecisionProposalCreate, DecisionProposalOut
from app.services.decision_service import create_decision_proposal
from app.core.database import get_db

router = APIRouter(prefix="/decisions", tags=["Decisions"])

@router.post("", response_model=DecisionProposalOut)
def create_decision(payload: DecisionProposalCreate, db: Session = Depends(get_db)):
    return create_decision_proposal(db, payload)
