from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class Message(BaseModel):
    message: str = Field(..., description="Human readable message.")


# ---- Auth ----
class SignupRequest(BaseModel):
    email: EmailStr = Field(..., description="User email address.")
    password: str = Field(..., min_length=8, description="User password (min 8 chars).")


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="User email address.")
    password: str = Field(..., description="User password.")


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="Short-lived JWT access token.")
    refresh_token: str = Field(..., description="Longer-lived JWT refresh token.")
    token_type: str = Field("bearer", description="Token type.")


class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., description="Refresh JWT token.")


# ---- Notes ----
class NoteBase(BaseModel):
    title: str = Field(..., max_length=200, description="Note title.")
    content: str = Field(..., description="Note content.")


class NoteCreate(NoteBase):
    pass


class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200, description="Updated note title.")
    content: Optional[str] = Field(None, description="Updated note content.")


class NoteOut(NoteBase):
    id: int = Field(..., description="Note ID.")
    created_at: datetime = Field(..., description="Creation timestamp.")
    updated_at: datetime = Field(..., description="Last update timestamp.")

    class Config:
        from_attributes = True
