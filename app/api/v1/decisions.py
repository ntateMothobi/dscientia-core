from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List
import json

from app.core.database import get_db
from app.schemas.decision_proposal import DecisionProposalCreate, DecisionProposalOut
from app.schemas.decision_review import DecisionReview
from app.schemas.override import DecisionOverride
from app.services.decision_service import create_decision_proposal, override_decision
from app.services.decision_review_service import review_decision
from app.services.audit_log_service import create_audit_log_entry
from app.schemas.audit_log import AuditLogCreate
from app.core.security import get_current_user, UserRole, require_roles, UserContext

router = APIRouter(prefix="/decisions", tags=["Decisions"])

@router.post("", response_model=DecisionProposalOut, status_code=status.HTTP_201_CREATED)
def submit_decision_proposal(payload: DecisionProposalCreate, db: Session = Depends(get_db)):
    return create_decision_proposal(db, payload)

@router.post("/{proposal_id}/review", response_model=DecisionProposalOut)
def review_decision_api(
    proposal_id: int,
    payload: DecisionReview,
    db: Session = Depends(get_db)
):
    return review_decision(db, proposal_id, payload)

@router.post("/{proposal_id}/override", response_model=DecisionProposalOut, dependencies=[Depends(require_roles([UserRole.FOUNDER, UserRole.OPS_CRM]))])
def override_decision_api(
    proposal_id: int,
    new_decision: str,
    override_reason: str,
    db: Session = Depends(get_db),
    user: UserContext = Depends(get_current_user)
):
    override_data = DecisionOverride(
        by=user.user_id,
        role=user.role.value,
        reason=override_reason
    )
    
    overridden_proposal = override_decision(db, proposal_id, new_decision, override_data)

    # Audit the override event
    log_details = json.dumps({
        "proposal_id": proposal_id,
        "original_decision": overridden_proposal.original_recommendation,
        "new_decision": new_decision,
        "reason": override_reason,
        "overridden_by": user.user_id
    })
    log_entry = AuditLogCreate(
        event_type="decision_override",
        decision="OVERRIDDEN",
        details=log_details,
        persona=user.role.value
    )
    create_audit_log_entry(db, log_entry)

    return overridden_proposal
