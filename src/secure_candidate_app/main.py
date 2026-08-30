from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from secure_candidate_app.database import get_database_session
from secure_candidate_app.models import User
from secure_candidate_app.schemas import UserRegister, UserResponse
from secure_candidate_app.security import hash_password


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