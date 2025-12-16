from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, date
from typing import Optional

class FollowupBase(BaseModel):
    lead_id: int = Field(..., description="ID of the lead this follow-up belongs to")
    note: str = Field(..., description="Details of the interaction", json_schema_extra={"example": "Customer asked for floor plan"})
    status: str = Field("pending", description="Status of this interaction", json_schema_extra={"example": "contacted"})
    next_contact_date: Optional[date] = Field(None, description="When to contact the lead next", json_schema_extra={"example": "2023-12-25"})

class FollowupCreate(FollowupBase):
    pass

class Followup(FollowupBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
