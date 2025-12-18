from sqlalchemy.orm import Session
from app.models.decision_proposal import DecisionProposal
from app.schemas.decision_proposal import DecisionProposalCreate

def create_decision_proposal(db: Session, payload: DecisionProposalCreate):
    proposal = DecisionProposal(
        entity_type=payload.entity_type,
        entity_id=payload.entity_id,
        risk_score=payload.risk_score,
        decision_level=payload.decision_level,
        recommendation=payload.recommendation,
        rationale=payload.rationale,
        status="PENDING"
    )
    db.add(proposal)
    db.commit()
    db.refresh(proposal)
    return proposal
