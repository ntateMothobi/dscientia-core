from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, JSON
from sqlalchemy.sql import func
from app.core.database import Base

class DecisionProposal(Base):
    __tablename__ = "decision_proposals"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String, nullable=False)
    entity_id = Column(Integer, nullable=False)

    risk_score = Column(Float, nullable=False)
    decision_level = Column(String, nullable=False)

    # Store the original system recommendation
    original_recommendation = Column('recommendation', String, nullable=False)
    # Store the final decision, which may be the original or an override
    final_decision = Column(String, nullable=False)
    
    rationale = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="PENDING")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    decided_at = Column(DateTime(timezone=True), nullable=True)
    
    reviewed_by = Column(String, nullable=True)
    review_note = Column(Text, nullable=True)

    escalated = Column(Boolean, default=False)
    sla_deadline = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # New fields for override
    overridden = Column(Boolean, default=False)
    override_details = Column(JSON, nullable=True)
