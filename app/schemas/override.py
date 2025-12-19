from pydantic import BaseModel, Field
from datetime import datetime

class DecisionOverride(BaseModel):
    by: str  # User ID
    role: str
    reason: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
