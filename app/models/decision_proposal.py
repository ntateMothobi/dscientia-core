from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class DecisionProposal(Base):
    __tablename__ = "decision_proposals"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String, nullable=False)
    entity_id = Column(Integer, nullable=False)

    risk_score = Column(Float, nullable=False)
    decision_level = Column(String, nullable=False)

    recommendation = Column(String, nullable=False)
    rationale = Column(Text, nullable=True)

    status = Column(String, nullable=False, default="PENDING")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    decided_at = Column(DateTime(timezone=True), nullable=True)
