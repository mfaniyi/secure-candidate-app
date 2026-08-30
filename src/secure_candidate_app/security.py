from datetime import datetime, timedelta, timezone
import os

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session
from secure_candidate_app.database import get_database_session
from secure_candidate_app.models import User

load_dotenv()


JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not JWT_SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY is not configured")


ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 30


password_hasher = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
)


def hash_password(plain_password: str) -> str:
    """Hash a plaintext password using Argon2."""
    return password_hasher.hash(plain_password)


def verify_password(
    plain_password: str,
    password_hash: str,
) -> bool:
    """Verify a plaintext password against its stored hash."""
    return password_hasher.verify(
        plain_password,
        password_hash,
    )


def create_access_token(
    subject: str,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed JWT access token."""
    if expires_delta is None:
        expires_delta = timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    expiration_time = (
        datetime.now(timezone.utc)
        + expires_delta
    )
    token_payload = {
        "sub": subject,
        "exp": expiration_time,
    }
    return jwt.encode(
        token_payload,
        JWT_SECRET_KEY,
        algorithm=ALGORITHM,
    )


def get_current_user_email(
    access_token: str = Depends(oauth2_scheme),
) -> str:
    """Extract and validate the user email from a JWT."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={
            "WWW-Authenticate": "Bearer",
        },
    )
    try:
        token_payload = jwt.decode(
            access_token,
            JWT_SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        user_email = token_payload.get("sub")
        if not user_email:
            raise credentials_exception
        return user_email
    except InvalidTokenError:
        raise credentials_exception


def get_current_user(
    user_email: str = Depends(get_current_user_email),
    db_session: Session = Depends(get_database_session),
) -> User:
    """Return the authenticated user from the database."""

    current_user = db_session.scalar(
        select(User).where(User.email == user_email)
    )
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )
    return current_user