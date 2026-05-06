from fastapi import APIRouter, Depends, HTTPException, status
from app.auth.dependencies import get_current_user
from app.routers.users.models import Users

router = APIRouter(prefix="/auth")


@router.get("/validate", status_code=status.HTTP_200_OK)
def validate_token(current_user: Users = Depends(get_current_user)):
    return {
        "valid": True,
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email
        }
    }