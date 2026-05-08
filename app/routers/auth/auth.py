from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.auth.dependencies import get_current_user
from app.routers.users.models import Users
from app.routers.users.schemas import UserResponse
from app.middleware.rate_limiter import read_rate_limit

router = APIRouter(prefix="/auth")


class TokenValidationResponse(BaseModel):
    valid: bool
    user: UserResponse


@router.get(
    "/validate",
    response_model=TokenValidationResponse,
    status_code=status.HTTP_200_OK,
)
def validate_token(
    current_user: Users = Depends(get_current_user),
    _: bool = Depends(read_rate_limit),
):
    return {
        "valid": True,
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
        },
    }
