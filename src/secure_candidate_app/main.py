import logging
import time
import uuid

from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from secure_candidate_app.database import get_database_session
from secure_candidate_app.models import User, Vacancy, Applicant
from secure_candidate_app.schemas import UserRegister, UserResponse, TokenResponse, VacancyCreate, VacancyResponse, ApplicantCreate, ApplicantResponse
from secure_candidate_app.security import hash_password, create_access_token, verify_password, get_current_user, require_admin
from secure_candidate_app.logging_config import configure_logging
from secure_candidate_app.error_handlers import internal_error_handler
from secure_candidate_app.rate_limit import is_rate_limited, record_failed_login, reset_login_attempts

app = FastAPI()

app.add_exception_handler(
    Exception,
    internal_error_handler,
)


configure_logging()

logger = logging.getLogger("secure_candidate_app")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    start_time = time.perf_counter()

    response = await call_next(request)

    latency_ms = round(
        (time.perf_counter() - start_time) * 1000,
        2,
    )

    logger.info(
        "request completed",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "latency_ms": latency_ms,
        },
    )

    response.headers["X-Request-ID"] = request_id

    return response


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
        role="user"
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
    if is_rate_limited(form_data.username):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later.",
            headers={"Retry-After": "60"},
        )

    user_record = db_session.scalar(
        select(User).where(
            User.email == form_data.username
        )
    )

    if not user_record:
        record_failed_login(form_data.username)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(
        form_data.password,
        user_record.password_hash,
    ):
        record_failed_login(form_data.username)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    reset_login_attempts(form_data.username)

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

@app.post(
    "/vacancies",
    response_model=VacancyResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_vacancy(
    vacancy_data: VacancyCreate,
    db_session: Session = Depends(get_database_session),
    current_user: User = Depends(require_admin),
):
    vacancy_record = Vacancy(
        title=vacancy_data.title,
        description=vacancy_data.description,
    )

    db_session.add(vacancy_record)
    db_session.commit()
    db_session.refresh(vacancy_record)

    return vacancy_record


@app.post(
    "/applicants",
    response_model=ApplicantResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_applicant(
    applicant_data: ApplicantCreate,
    db_session: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user),
):
    vacancy_record = db_session.get(
        Vacancy,
        applicant_data.vacancy_id,
    )

    if not vacancy_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vacancy not found",
        )

    applicant_record = Applicant(
        name=applicant_data.name,
        email=applicant_data.email,
        vacancy_id=applicant_data.vacancy_id,
    )

    db_session.add(applicant_record)
    db_session.commit()
    db_session.refresh(applicant_record)

    return applicant_record


@app.get("/admin/test")
def admin_test(
    current_user: User = Depends(require_admin),
):
    return {
        "message": "Welcome, admin",
        "email": current_user.email,
    }