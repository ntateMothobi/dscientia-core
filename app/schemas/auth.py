from pydantic import BaseModel
from app.core.security import UserRole

class UserTokenPayload(BaseModel):
    """
    Schema for the data encoded within the JWT.
    """
    sub: str  # Standard JWT subject claim, used for user_id
    role: UserRole
    exp: int

class LoginRequest(BaseModel):
    """
    Schema for the login request body.
    """
    persona: str

class TokenResponse(BaseModel):
    """
    Schema for the response when a token is issued.
    """
    access_token: str
    token_type: str = "bearer"
