from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.decision_proposal import DecisionProposalCreate, DecisionProposalOut
from app.schemas.decision_review import DecisionReview
from app.services.decision_service import create_decision_proposal
from app.services.decision_review_service import review_decision
from app.services.decision_sla_service import evaluate_decision_sla

router = APIRouter(prefix="/decisions", tags=["Decisions"])

@router.post("", response_model=DecisionProposalOut, status_code=status.HTTP_201_CREATED)
def create_decision(payload: DecisionProposalCreate, db: Session = Depends(get_db)):
    return create_decision_proposal(db, payload)

@router.post("/{proposal_id}/review", response_model=DecisionProposalOut)
def review_decision_api(
    proposal_id: int,
    payload: DecisionReview,
    db: Session = Depends(get_db)
):
    return review_decision(db, proposal_id, payload)

@router.post("/sla/evaluate")
def evaluate_sla_endpoint(db: Session = Depends(get_db)):
    count = evaluate_decision_sla(db)
    return {"escalated": count}
