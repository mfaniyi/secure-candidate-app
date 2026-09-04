from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from secure_candidate_app.main import app
from sqlalchemy import text
from secure_candidate_app.database import engine


client = TestClient(app)


def test_register_user():
    response = client.post(
        "/auth/register",
        json={
            "email": "testuser@example.com",
            "password": "MyPassword123",
        },
    )

    assert response.status_code == 201
    assert response.json()["email"] == "testuser@example.com"
    assert "password" not in response.json()
    assert "password_hash" not in response.json()


def test_register_with_invalid_email():
    response = client.post(
        "/auth/register",
        json={
            "email": "not-a-valid-email",
            "password": "MyPassword123",
        },
    )

    assert response.status_code == 422


def test_login_user():
    client.post(
        "/auth/register",
        json={
            "email": "loginuser@example.com",
            "password": "MyPassword123",
        },
    )

    response = client.post(
        "/auth/login",
        data={
            "username": "loginuser@example.com",
            "password": "MyPassword123",
        },
    )

    assert response.status_code == 200

    response_data = response.json()

    assert "access_token" in response_data
    assert response_data["token_type"] == "bearer"


def test_login_with_wrong_password():
    client.post(
        "/auth/register",
        json={
            "email": "wrongpassword@example.com",
            "password": "MyPassword123",
        },
    )

    response = client.post(
        "/auth/login",
        data={
            "username": "wrongpassword@example.com",
            "password": "WrongPassword",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


def test_auth_me_requires_authentication():
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_auth_me_with_valid_token():
    client.post(
        "/auth/register",
        json={
            "email": "me@example.com",
            "password": "MyPassword123",
        },
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "me@example.com",
            "password": "MyPassword123",
        },
    )

    token = login_response.json()["access_token"]

    response = client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200
    assert response.json()["email"] == "me@example.com"


def test_invalid_token_is_rejected():
    response = client.get(
        "/auth/me",
        headers={
            "Authorization": "Bearer invalid.jwt.token",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


def test_create_vacancy_requires_authentication():
    response = client.post(
        "/vacancies",
        json={
            "title": "Data Analyst",
            "description": "Analyze business data",
        },
    )

    assert response.status_code == 401


def test_create_and_persist_vacancy():
    client.post(
        "/auth/register",
        json={
            "email": "vacancyuser@example.com",
            "password": "MyPassword123",
        },
    )

    with engine.begin() as connection:
        connection.execute(
            text(
                "UPDATE users SET role = 'admin' "
                "WHERE email = 'vacancyuser@example.com'"
            )
        )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "vacancyuser@example.com",
            "password": "MyPassword123",
        },
    )

    token = login_response.json()["access_token"]

    create_response = client.post(
        "/vacancies",
        json={
            "title": "Backend Developer",
            "description": "Build FastAPI applications",
        },
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert create_response.status_code == 201

    vacancy_data = create_response.json()

    assert vacancy_data["title"] == "Backend Developer"
    assert vacancy_data["description"] == "Build FastAPI applications"
    assert vacancy_data["id"] is not None


def test_create_applicant_for_vacancy():
    client.post(
        "/auth/register",
        json={
            "email": "applicantuser@example.com",
            "password": "MyPassword123",
        },
    )

    with engine.begin() as connection:
        connection.execute(
            text(
                "UPDATE users SET role = 'admin' "
                "WHERE email = 'applicantuser@example.com'"
            )
        )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "applicantuser@example.com",
            "password": "MyPassword123",
        },
    )

    token = login_response.json()["access_token"]

    vacancy_response = client.post(
        "/vacancies",
        json={
            "title": "Python Developer",
            "description": "Develop backend systems",
        },
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    vacancy_id = vacancy_response.json()["id"]

    applicant_response = client.post(
        "/applicants",
        json={
            "name": "Alice Johnson",
            "email": "alice.persistence@example.com",
            "years_of_experience": 3,
            "vacancy_id": vacancy_id,
        },
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert applicant_response.status_code == 201

    applicant_data = applicant_response.json()

    assert applicant_data["name"] == "Alice Johnson"
    assert applicant_data["email"] == "alice.persistence@example.com"
    assert applicant_data["vacancy_id"] == vacancy_id


def test_create_applicant_with_missing_vacancy():
    client.post(
        "/auth/register",
        json={
            "email": "foreignkeyuser@example.com",
            "password": "MyPassword123",
        },
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "foreignkeyuser@example.com",
            "password": "MyPassword123",
        },
    )

    token = login_response.json()["access_token"]

    response = client.post(
        "/applicants",
        json={
            "name": "Bob Smith",
            "email": "bob.foreignkey@example.com",
            "years_of_experience": 2,
            "vacancy_id": 999999,
        },
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Vacancy not found"


def test_duplicate_user_email_is_rejected():
    user_data = {
        "email": "duplicate@example.com",
        "password": "MyPassword123",
    }

    first_response = client.post(
        "/auth/register",
        json=user_data,
    )

    second_response = client.post(
        "/auth/register",
        json=user_data,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Email already registered"



def test_invalid_jwt_is_rejected():
    response = client.get(
        "/auth/me",
        headers={
            "Authorization": "Bearer this-is-not-a-valid-jwt",
        },
    )

    assert response.status_code == 401


def test_tampered_jwt_is_rejected():
    client.post(
        "/auth/register",
        json={
            "email": "tampered@example.com",
            "password": "MyPassword123",
        },
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "tampered@example.com",
            "password": "MyPassword123",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    header, payload, signature = token.split(".")

    tampered_signature = (
        "A" if signature[0] != "A" else "B"
    )

    tampered_token = (
        f"{header}.{payload}.{tampered_signature}{signature[1:]}"
    )

    response = client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {tampered_token}",
        },
    )

    assert response.status_code == 401


def test_expired_jwt_is_rejected():
    from datetime import timedelta

    from secure_candidate_app.security import create_access_token

    expired_token = create_access_token(
        "duplicate@example.com",
        expires_delta=timedelta(seconds=-1),
    )

    response = client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {expired_token}",
        },
    )

    assert response.status_code == 401


def test_normal_user_cannot_create_vacancy():
    client.post(
        "/auth/register",
        json={
            "email": "authorizationuser@example.com",
            "password": "MyPassword123",
        },
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "authorizationuser@example.com",
            "password": "MyPassword123",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.post(
        "/vacancies",
        json={
            "title": "Unauthorized Vacancy",
            "description": "This should not be created",
        },
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"


def test_admin_endpoint_requires_admin_role():
    client.post(
        "/auth/register",
        json={
            "email": "adminendpointuser@example.com",
            "password": "MyPassword123",
        },
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "adminendpointuser@example.com",
            "password": "MyPassword123",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/admin/test",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"


def test_protected_endpoint_requires_authentication():
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_database_failure_returns_safe_error():
    test_client = TestClient(
        app,
        raise_server_exceptions=False,
    )

    failing_session = MagicMock()
    failing_session.scalar.side_effect = Exception(
        "Simulated database failure"
    )

    def override_database_session():
        yield failing_session

    from secure_candidate_app.database import (
        get_database_session,
    )

    app.dependency_overrides[
        get_database_session
    ] = override_database_session

    try:
        response = test_client.post(
            "/auth/register",
            json={
                "email": "databasefailure@example.com",
                "password": "MyPassword123",
            },
        )

        assert response.status_code == 500
        assert response.json()["detail"] == (
            "Internal server error"
        )

    finally:
        app.dependency_overrides.clear()