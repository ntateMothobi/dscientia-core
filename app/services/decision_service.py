from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.decision_proposal import DecisionProposal
from app.schemas.decision_proposal import DecisionProposalCreate
from app.schemas.override import DecisionOverride

def create_decision_proposal(db: Session, payload: DecisionProposalCreate) -> DecisionProposal:
    """
    Persists a new decision proposal to the database.
    """
    db_proposal = DecisionProposal(
        entity_type=payload.entity_type,
        entity_id=payload.entity_id,
        risk_score=payload.risk_score,
        decision_level=payload.decision_level,
        original_recommendation=payload.recommendation,
        final_decision=payload.recommendation, # Initially, final decision is the same
        rationale=payload.rationale,
        status="PENDING"
    )
    db.add(db_proposal)
    db.commit()
    db.refresh(db_proposal)
    return db_proposal

def override_decision(db: Session, proposal_id: int, new_decision: str, override_data: DecisionOverride) -> DecisionProposal:
    """
    Overrides an existing decision proposal.
    """
    proposal = db.query(DecisionProposal).filter(DecisionProposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Decision proposal not found")

    if proposal.status != "PENDING":
        raise HTTPException(status_code=400, detail="Decision has already been acted upon and cannot be overridden.")

    proposal.final_decision = new_decision
    proposal.overridden = True
    proposal.override_details = override_data.model_dump()
    proposal.status = "OVERRIDDEN"

    db.commit()
    db.refresh(proposal)
    return proposal
