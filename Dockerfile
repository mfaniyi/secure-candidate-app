FROM python:3.14-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev --no-install-project

COPY src ./src

COPY migrations ./migrations

COPY alembic.ini ./

COPY README.md ./

RUN uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH"

ENV PYTHONPATH="/app/src"

EXPOSE 8000

CMD ["uvicorn", "secure_candidate_app.main:app", "--host", "0.0.0.0", "--port", "8000"]