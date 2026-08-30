from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from secure_candidate_app.database import get_database_session
from secure_candidate_app.models import User
from secure_candidate_app.schemas import UserRegister, UserResponse, TokenResponse
from secure_candidate_app.security import hash_password, create_access_token, verify_password, get_current_user


app = FastAPI()


@app.post(
    "/auth/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    user_data: UserRegister,
    db_session: Session = Depends(get_database_session),
):
    existing_user = db_session.scalar(
        select(User).where(User.email == user_data.email)
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    user_record = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password),
    )
    db_session.add(user_record)
    db_session.commit()
    db_session.refresh(user_record)
    return user_record


@app.post(
    "/auth/login",
    response_model=TokenResponse,
)
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db_session: Session = Depends(get_database_session),
):
    user_record = db_session.scalar(
        select(User).where(
            User.email == form_data.username
        )
    )

    if not user_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(
        form_data.password,
        user_record.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        str(user_record.email)
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )


@app.get(
    "/auth/me",
    response_model=UserResponse,
)
def get_authenticated_user(
    current_user: User = Depends(get_current_user),
):
    return current_user