"""seed initial users vacancies and applicants

Revision ID: 87322cc05a77
Revises: a9d61b0722af
Create Date: 2026-09-04 13:01:18.334787

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column


revision: str = "87322cc05a77"
down_revision: Union[str, Sequence[str], None] = "a9d61b0722af"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Seed initial application data."""

    users = table(
        "users",
        column("id", sa.Integer),
        column("email", sa.String),
        column("password_hash", sa.String),
        column("role", sa.String),
    )

    vacancies = table(
        "vacancies",
        column("id", sa.Integer),
        column("title", sa.String),
        column("description", sa.Text),
    )

    applicants = table(
        "applicants",
        column("id", sa.Integer),
        column("name", sa.String),
        column("email", sa.String),
        column("years_of_experience", sa.Integer),
        column("vacancy_id", sa.Integer),
    )

    # Seed users
    op.bulk_insert(
        users,
        [
            {
                "id": 1,
                "email": "admin@example.com",
                "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$tcoAu+6ZH1dJY8N6f27cwg$tUv6svKOUF56DgYf9CW6w/AKisPxfuqxla22U8spY74",
                "role": "admin",
            },
            {
                "id": 2,
                "email": "recruiter@example.com",
                "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$UB0okWzZO8kFZHO4ue0NYg$HvuW7UmIYuiwYtDJ6MXDdKpfvSspKRDhI4MOBuIwAfM",
                "role": "user",
            },
            {
                "id": 3,
                "email": "candidate@example.com",
                "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$bppPBhezQtPjtrWYRk/3Sg$HSKAhUjHnmb63rGwYyLP9/8cgi8YiffL5j1tJbBGLp0",
                "role": "user",
            },
        ],
    )

    # Seed vacancies
    op.bulk_insert(
        vacancies,
        [
            {
                "id": 1,
                "title": "Python Developer",
                "description": "Develop and maintain Python applications.",
            },
            {
                "id": 2,
                "title": "Data Analyst",
                "description": "Analyze business data and create actionable insights.",
            },
            {
                "id": 3,
                "title": "AI/ML Engineer",
                "description": "Build and maintain machine learning solutions.",
            },
            {
                "id": 4,
                "title": "Backend Developer",
                "description": "Design and develop backend APIs and services.",
            },
            {
                "id": 5,
                "title": "BI Analyst",
                "description": "Develop dashboards and business intelligence solutions.",
            },
        ],
    )

    # Seed applicants
    op.bulk_insert(
        applicants,
        [
            {
                "id": 1,
                "name": "John Smith",
                "email": "john.smith@example.com",
                "years_of_experience": 3,
                "vacancy_id": 1,
            },
            {
                "id": 2,
                "name": "Jane Doe",
                "email": "jane.doe@example.com",
                "years_of_experience": 5,
                "vacancy_id": 2,
            },
            {
                "id": 3,
                "name": "Michael Brown",
                "email": "michael.brown@example.com",
                "years_of_experience": 4,
                "vacancy_id": 3,
            },
            {
                "id": 4,
                "name": "Sarah Wilson",
                "email": "sarah.wilson@example.com",
                "years_of_experience": 6,
                "vacancy_id": 4,
            },
            {
                "id": 5,
                "name": "David Johnson",
                "email": "david.johnson@example.com",
                "years_of_experience": 2,
                "vacancy_id": 5,
            },
            {
                "id": 6,
                "name": "Emily Davis",
                "email": "emily.davis@example.com",
                "years_of_experience": 4,
                "vacancy_id": 1,
            },
            {
                "id": 7,
                "name": "Daniel Miller",
                "email": "daniel.miller@example.com",
                "years_of_experience": 7,
                "vacancy_id": 3,
            },
            {
                "id": 8,
                "name": "Olivia Taylor",
                "email": "olivia.taylor@example.com",
                "years_of_experience": 3,
                "vacancy_id": 2,
            },
            {
                "id": 9,
                "name": "James Anderson",
                "email": "james.anderson@example.com",
                "years_of_experience": 5,
                "vacancy_id": 4,
            },
            {
                "id": 10,
                "name": "Sophia Thomas",
                "email": "sophia.thomas@example.com",
                "years_of_experience": 8,
                "vacancy_id": 5,
            },
        ],
    )

    # Synchronize PostgreSQL sequences with the highest existing IDs.
    # This ensures future automatically generated IDs continue
    # after the seeded records.
    op.execute(
        """
        SELECT setval(
            pg_get_serial_sequence('users', 'id'),
            COALESCE((SELECT MAX(id) FROM users), 1)
        )
        """
    )

    op.execute(
        """
        SELECT setval(
            pg_get_serial_sequence('vacancies', 'id'),
            COALESCE((SELECT MAX(id) FROM vacancies), 1)
        )
        """
    )

    op.execute(
        """
        SELECT setval(
            pg_get_serial_sequence('applicants', 'id'),
            COALESCE((SELECT MAX(id) FROM applicants), 1)
        )
        """
    )


def downgrade() -> None:
    """Remove seeded application data."""

    op.execute(
        "DELETE FROM applicants WHERE id BETWEEN 1 AND 10"
    )

    op.execute(
        "DELETE FROM vacancies WHERE id BETWEEN 1 AND 5"
    )

    op.execute(
        """
        DELETE FROM users
        WHERE id BETWEEN 1 AND 3
        """
    )