from fastapi.testclient import TestClient

from secure_candidate_app.main import app


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