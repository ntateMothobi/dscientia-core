from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

class LeadBase(BaseModel):
    name: str = Field(..., description="Name of the potential client", json_schema_extra={"example": "Budi Santoso"})
    phone: str = Field(..., description="Primary contact number (WhatsApp)", json_schema_extra={"example": "+628123456789"})
    email: Optional[str] = Field(None, description="Email address (optional)", json_schema_extra={"example": "budi@example.com"})
    source: str = Field("manual", description="Where the lead came from", json_schema_extra={"example": "whatsapp"})
    budget: Optional[float] = Field(None, description="Estimated budget", json_schema_extra={"example": 1500000000})
    notes: Optional[str] = Field(None, description="Agent's notes", json_schema_extra={"example": "Looking for 3BR"})
    status: str = Field("new", description="Current status", json_schema_extra={"example": "new"})

class LeadCreate(LeadBase):
    pass

class Lead(LeadBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
