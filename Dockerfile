##################  Builder  ##################
FROM python:3.13-slim AS builder

RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential curl \
 && rm -rf /var/lib/apt/lists/*

ENV POETRY_HOME="/opt/poetry" \
    PATH="/opt/poetry/bin:${PATH}"
RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /app

COPY pyproject.toml poetry.lock* ./
COPY README.md ./
COPY alembic.ini ./

RUN poetry config virtualenvs.create false \
 && poetry install --only main --no-root --no-interaction --no-ansi

COPY src ./src
COPY alembic alembic


##################  Runtime  ##################
FROM python:3.13-slim
RUN adduser --disabled-password --gecos "" appuser
USER appuser
WORKDIR /app

COPY --from=builder /usr/local/lib/python3.13 /usr/local/lib/python3.13
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app/src ./src
COPY --from=builder /app/alembic ./alembic
COPY --from=builder /app/alembic.ini ./alembic.ini

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
