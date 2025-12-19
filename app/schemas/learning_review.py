from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ReviewStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class LearningReviewCreate(BaseModel):
    insight_type: str
    summary: str
    metrics: Dict[str, Any]

class LearningReviewUpdate(BaseModel):
    status: ReviewStatus
    notes: Optional[str] = None

class LearningReviewRead(BaseModel):
    id: int
    insight_type: str
    summary: str
    metrics: Dict[str, Any]
    status: ReviewStatus
    reviewer: Optional[str]
    reviewed_at: Optional[datetime]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
