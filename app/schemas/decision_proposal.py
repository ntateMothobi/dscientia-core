from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DecisionProposalCreate(BaseModel):
    entity_type: str
    entity_id: int
    risk_score: float
    decision_level: str
    recommendation: str
    rationale: Optional[str] = None

class DecisionProposalOut(DecisionProposalCreate):
    id: int
    status: str
    created_at: datetime
    decided_at: Optional[datetime]

    class Config:
        from_attributes = True
