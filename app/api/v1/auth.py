from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, timedelta
from jose import jwt
from sqlalchemy.orm import Session

from app.schemas.auth import LoginRequest, TokenResponse
from app.core.config import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_ACCESS_TOKEN_EXPIRE_HOURS
from app.core.security import UserRole
from app.core.database import get_db
from app.services.audit_log_service import create_audit_log
from app.schemas.audit_log import AuditLogCreate

router = APIRouter(prefix="/auth", tags=["Authentication"])

def map_persona_to_role(persona: str) -> UserRole:
    """Maps a persona string to a UserRole enum."""
    mapping = {
        "Founder / Executive": UserRole.FOUNDER,
        "Sales Manager": UserRole.SALES_MANAGER,
        "Operations / CRM Manager": UserRole.OPS_CRM,
    }
    role = mapping.get(persona)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid persona specified: {persona}"
        )
    return role

@router.post("/login", response_model=TokenResponse)
def login_for_access_token(
    login_request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Fake login endpoint to issue a JWT based on a persona.
    In a real app, this would verify a username and password.
    """
    role = map_persona_to_role(login_request.persona)
    
    # In a real app, user_id would come from the database.
    # Here, we'll use a placeholder.
    user_id = f"user_for_{role.value}"

    expire_delta = timedelta(hours=JWT_ACCESS_TOKEN_EXPIRE_HOURS)
    expire_time = datetime.utcnow() + expire_delta
    
    to_encode = {
        "sub": user_id,
        "role": role.value,
        "exp": expire_time
    }
    
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    # Audit the login event
    create_audit_log(db, AuditLogCreate(
        event_type="user_login",
        details=f"User '{user_id}' logged in with role '{role.value}'.",
        persona=role.value
    ))
    
    return {"access_token": encoded_jwt, "token_type": "bearer"}
