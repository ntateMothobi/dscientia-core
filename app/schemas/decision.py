from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Dict, Any
from enum import Enum
import uuid

class RecommendationPriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class SuggestedOwner(str, Enum):
    EXECUTIVE = "Executive"
    SALES = "Sales"
    MARKETING = "Marketing"
    OPS = "Ops"

class DecisionRecommendation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    recommendation: str
    priority: RecommendationPriority
    confidence: int
    rationale: str
    impacted_metrics: List[str]
    governance_flags: List[str]
    suggested_owner: SuggestedOwner
    explanation: Optional[Dict[str, Any]] = None
    explainability_summary: Optional[str] = None

    class Config:
        from_attributes = True
