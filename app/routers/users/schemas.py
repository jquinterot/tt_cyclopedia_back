from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator
import re


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra='forbid')
    id: Optional[str] = Field(None, description="User ID")
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    password: str = Field(..., min_length=6, max_length=100, description="User password (hashed in DB)")
    email: str = Field(..., description="User email address")


class UserCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    username: str = Field(..., min_length=3, max_length=50, description="Desired username", examples=["johndoe"])
    password: str = Field(..., min_length=6, max_length=100, description="User password", examples=["securePass123"])
    email: EmailStr = Field(..., description="Valid email address", examples=["john@example.com"])

    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username must contain only letters, numbers, and underscores')
        return v


class UserLogin(BaseModel):
    model_config = ConfigDict(extra='forbid')
    username: str = Field(..., min_length=3, max_length=50, description="Username", examples=["johndoe"])
    password: str = Field(..., min_length=6, max_length=100, description="Password", examples=["securePass123"])

    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username must contain only letters, numbers, and underscores')
        return v


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra='forbid')
    id: str = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")


class Token(BaseModel):
    model_config = ConfigDict(extra='forbid')
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(..., description="Token type (usually 'bearer')")


class TokenData(BaseModel):
    model_config = ConfigDict(extra='forbid')
    username: Optional[str] = Field(None, description="Username extracted from token")


class LoginResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(..., description="Token type (usually 'bearer')")
    user: UserResponse = Field(..., description="Authenticated user details")
