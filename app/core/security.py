from enum import Enum
from typing import List, Optional
from fastapi import Request, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from jose import JWTError, jwt
from datetime import datetime

from app.core.config import JWT_SECRET_KEY, JWT_ALGORITHM

# --- DEV AUTH BYPASS – REMOVE BEFORE PRODUCTION ---
DEV_MODE_BYPASS_AUTH = True
# --- END DEV AUTH BYPASS ---

class UserRole(str, Enum):
    FOUNDER = "founder"
    SALES_MANAGER = "sales_manager"
    OPS_CRM = "ops_crm"

class UserContext(BaseModel):
    user_id: str
    role: UserRole
    source: str

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

def get_current_user(request: Request, token: Optional[str] = Depends(oauth2_scheme)) -> Optional[UserContext]:
    """
    Parses a JWT or provides a mock user in dev mode.
    """
    # --- DEV AUTH BYPASS – REMOVE BEFORE PRODUCTION ---
    if DEV_MODE_BYPASS_AUTH:
        # In dev mode, we can default to a specific role for testing.
        # This allows the UI to work without a real login flow.
        return UserContext(user_id="dev_user", role=UserRole.FOUNDER, source="dev_bypass")
    # --- END DEV AUTH BYPASS ---

    if not token:
        return None
        
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        if datetime.utcnow() > datetime.fromtimestamp(payload.get("exp", 0)):
            return None
        return UserContext(
            user_id=payload.get("sub"),
            role=UserRole(payload.get("role")),
            source='jwt'
        )
    except (JWTError, ValueError):
        return None

def get_current_user_role(request: Request, user_context: Optional[UserContext] = Depends(get_current_user)) -> UserRole:
    """
    Determines the user's role from JWT, dev bypass, or header.
    """
    if user_context:
        return user_context.role

    # Fallback to header if no JWT or dev bypass
    role_str = request.headers.get("X-User-Role")
    if role_str:
        try:
            return UserRole(role_str)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role in X-User-Role header")
    
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

def require_roles(allowed_roles: List[UserRole]):
    def guard(role: UserRole = Depends(get_current_user_role)):
        if role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. User with role '{role.value}' does not have permission."
            )
    return guard
