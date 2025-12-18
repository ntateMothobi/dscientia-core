from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.decision_proposal import DecisionProposal

SLA_HOURS = 24

def evaluate_decision_sla(db: Session):
    now = datetime.utcnow()
    deadline = now - timedelta(hours=SLA_HOURS)

    proposals = db.query(DecisionProposal).filter(
        DecisionProposal.status == "PENDING",
        DecisionProposal.created_at <= deadline,
        DecisionProposal.escalated == False
    ).all()

    for p in proposals:
        p.status = "ESCALATED"
        p.escalated = True

    db.commit()
    return len(proposals)
