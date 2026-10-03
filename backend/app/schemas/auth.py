from pydantic import BaseModel, EmailStr, Field
from typing import List

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    password_confirm: str

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    is_active: bool
    roles: List[str] = []
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshRequest(BaseModel):
    refresh_token: str
