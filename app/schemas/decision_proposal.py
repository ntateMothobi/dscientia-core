from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class DecisionProposalBase(BaseModel):
    entity_type: str
    entity_id: int
    risk_score: float
    decision_level: str
    original_recommendation: str
    final_decision: str
    rationale: Optional[str] = None

class DecisionProposalCreate(BaseModel):
    entity_type: str
    entity_id: int
    risk_score: float
    decision_level: str
    recommendation: str # This will be used for both original and final on creation
    rationale: Optional[str] = None

class DecisionProposalOut(DecisionProposalBase):
    id: int
    status: str
    created_at: datetime
    decided_at: Optional[datetime]
    overridden: bool
    override_details: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True
