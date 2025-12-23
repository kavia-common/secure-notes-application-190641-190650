from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.auth import create_access_token, create_refresh_token, verify_refresh_token
from src.db import get_db
from src.models import User
from src.schemas import (
    LoginRequest,
    Message,
    RefreshRequest,
    SignupRequest,
    TokenResponse,
)
from src.security import hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/signup",
    response_model=Message,
    status_code=status.HTTP_201_CREATED,
    summary="Create a user account",
    description="Creates a new user account with email + password.",
)
# PUBLIC_INTERFACE
def signup(payload: SignupRequest, db: Session = Depends(get_db)) -> Message:
    """Create a new user (unique email)."""
    existing = db.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(email=payload.email, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    return Message(message="User created")


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login and receive JWT tokens",
    description="Validates credentials and returns access + refresh tokens.",
)
# PUBLIC_INTERFACE
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Login with email/password."""
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        token_type="bearer",
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="Exchanges a valid refresh token for a new access token (and a new refresh token).",
)
# PUBLIC_INTERFACE
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Refresh JWT tokens using a refresh token."""
    user_id = verify_refresh_token(payload.refresh_token)
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        token_type="bearer",
    )
