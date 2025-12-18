from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

def default_uuid():
    return str(uuid.uuid4())

class AuditLog(Base):
    """
    SQLAlchemy model for audit logs.
    Stores a simplified record of system events and decisions.
    """
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, unique=True, index=True, default=default_uuid)
    
    event_type = Column(String, nullable=False, index=True)
    decision = Column(String, nullable=True)
    details = Column(Text, nullable=True) # Use Text for potentially longer content
    persona = Column(String, nullable=True, index=True)
    
    # Renamed from timestamp to created_at for consistency with other models
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Kept for future Web3 anchoring
    event_hash = Column(String, nullable=True)
