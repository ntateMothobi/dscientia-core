from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Followup(Base):
    """
    SQLAlchemy model for follow-up records.
    """
    __tablename__ = "followups"

    id = Column(Integer, primary_key=True, index=True)
    
    lead_id = Column(
        Integer, 
        ForeignKey("leads.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    
    note = Column(String, nullable=False)
    
    status = Column(String, nullable=False, default="pending", index=True)
    
    next_contact_date = Column(Date, nullable=True)
    
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now()
    )

    # Relationship to Lead
    lead = relationship("Lead", back_populates="followups")
