from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.config.postgres_config import SessionLocal
from app.routers.users.models import Users
from app.auth.jwt_handler import jwt_handler
from typing import Optional

security = HTTPBearer()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Users:
    """
    Get the current authenticated user from JWT token.
    This function is used as a dependency for protected endpoints.
    """
    try:
        # Verify the token and get username
        username = jwt_handler.verify_token(credentials.credentials)
        
        # Get user from database
        user = db.query(Users).filter(Users.username == username).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[Users]:
    """
    Get the current authenticated user if token is provided, otherwise return None.
    This allows for optional authentication on some endpoints.
    """
    if not credentials:
        return None
    
    try:
        username = jwt_handler.verify_token(credentials.credentials)
        user = db.query(Users).filter(Users.username == username).first()
        return user
    except Exception:
        return None