import pytest

from sqlalchemy import delete

from secure_candidate_app.database import SessionLocal
from secure_candidate_app.models import User, Vacancy, Applicant


@pytest.fixture(autouse=True)
def clean_database():
    database_session = SessionLocal()

    try:
        database_session.execute(delete(Applicant))
        database_session.execute(delete(Vacancy))
        database_session.execute(delete(User))
        database_session.commit()

        yield

    finally:
        database_session.rollback()
        database_session.close()