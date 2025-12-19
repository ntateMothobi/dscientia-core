from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class ReviewStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class LearningReview(Base):
    __tablename__ = "learning_reviews"

    id = Column(Integer, primary_key=True, index=True)
    insight_type = Column(String, nullable=False)
    summary = Column(String, nullable=False)
    metrics = Column(JSON, nullable=False)
    status = Column(String, default=ReviewStatus.PENDING.value)
    reviewer = Column(String, nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
