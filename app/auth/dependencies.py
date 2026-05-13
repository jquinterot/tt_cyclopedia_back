from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.auth.jwt_handler import jwt_handler
from app.config.postgres_config import SessionLocal
from app.routers.users.models import Users

security = HTTPBearer(auto_error=False)


class AdminException(Exception):
    pass


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)
) -> Users:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Authentication required",
            headers={"X-Error-Code": "AUTH_001"},
        )
    try:
        username = jwt_handler.verify_token(credentials.credentials)
        user = db.query(Users).filter(Users.username == username).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer", "X-Error-Code": "AUTH_002"},
            )
        return user
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer", "X-Error-Code": "AUTH_002"},
        )


async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
) -> Users | None:
    if not credentials:
        return None
    try:
        username = jwt_handler.verify_token(credentials.credentials)
        user = db.query(Users).filter(Users.username == username).first()
        return user
    except Exception:
        return None


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)
) -> Users:
    user = await get_current_user(credentials, db)
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
            headers={"X-Error-Code": "AUTH_004"},
        )
    return user
