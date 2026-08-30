# Secure Candidate Application API

A secure REST API for managing users, vacancies, and applicants. The application is built with FastAPI, PostgreSQL, SQLAlchemy, and JWT authentication.

## Features

* User registration
* Secure password hashing
* JWT-based authentication
* Token expiration
* Protected endpoints
* Rejection of invalid, expired, and tampered JWTs
* Login rate limiting
* Role-based authorization
* `user` and `admin` roles
* Admin-only vacancy creation
* PostgreSQL database persistence
* SQLAlchemy ORM
* Alembic database migrations
* Automated tests with pytest
* Structured request logging
* Custom error handling

## Technology Stack

* Python
* FastAPI
* PostgreSQL
* SQLAlchemy
* Alembic
* PyJWT
* pwdlib
* pytest
* uv

## Project Structure

```text
secure_candidate_app/
├── migrations/
│   └── versions/
├── src/
│   └── secure_candidate_app/
│       ├── database.py
│       ├── error_handlers.py
│       ├── logging_config.py
│       ├── main.py
│       ├── models.py
│       ├── rate_limit.py
│       ├── schemas.py
│       └── security.py
├── tests/
│   └── test_main.py
├── README.md
├── alembic.ini
├── pyproject.toml
└── uv.lock
```

## Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd secure_candidate_app
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Configure the database

Create a PostgreSQL database and configure the application's database connection settings.

Apply the database migrations:

```bash
uv run alembic upgrade head
```

## Running the Application

Start the FastAPI application:

```bash
uv run fastapi dev src/secure_candidate_app/main.py
```

Open the interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

## Authentication

### Register a User

**POST** `/auth/register`

Example request:

```json
{
  "email": "user@example.com",
  "password": "MyPassword123"
}
```

Newly registered users receive the default role:

```text
user
```

### Login

**POST** `/auth/login`

The login endpoint uses form data:

```text
username: user@example.com
password: MyPassword123
```

A successful login returns a JWT access token.

```json
{
  "access_token": "<jwt-token>",
  "token_type": "bearer"
}
```

The token must be included in protected requests:

```text
Authorization: Bearer <jwt-token>
```

## Authorization

The application supports two roles:

* `user`
* `admin`

Regular users can authenticate and access endpoints allowed to authenticated users.

Admin users can access admin-restricted functionality.

### Admin-Only Endpoint

**POST** `/vacancies`

Only users with the `admin` role can create vacancies.

A regular user attempting this action receives:

```text
403 Forbidden
```

### Admin Test Endpoint

**GET** `/admin/test`

This endpoint requires an authenticated admin user.

## Security Features

### Password Hashing

Passwords are not stored as plaintext. Passwords are hashed before being saved to the database.

### JWT Validation

The API rejects:

* Invalid tokens
* Expired tokens
* Tampered tokens
* Missing authentication tokens

### Login Rate Limiting

The application limits failed login attempts to help protect against repeated authentication attacks.

The current configuration allows:

* Maximum failed attempts: `5`
* Rate-limit window: `60 seconds`

## Database

The application uses PostgreSQL with SQLAlchemy ORM.

Database schema changes are managed with Alembic.

Apply migrations with:

```bash
uv run alembic upgrade head
```

Check the current migration version:

```bash
uv run alembic current
```

## Testing

Run the test suite:

```bash
uv run pytest
```

The test suite covers:

* User registration
* Duplicate email rejection
* User login
* Password authentication
* JWT authentication
* Invalid JWT rejection
* Tampered JWT rejection
* Expired JWT rejection
* Protected endpoint authentication
* Login rate limiting
* Vacancy persistence
* Applicant persistence
* Admin authorization
* Regular-user authorization restrictions

## Current Test Status

```text
17 passed
```
