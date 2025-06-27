from typing import Optional

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    id: Optional[str] = None
    username: str
    password: str
    email: str

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    username: str
    password: str
    email: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: str
    username: str
    email: str

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
