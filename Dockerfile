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

COPY src ./src

RUN poetry config virtualenvs.create false \
 && poetry install --only main --no-interaction --no-ansi

##################  Runtime  ##################
FROM python:3.13-slim
RUN adduser --disabled-password --gecos "" appuser
USER appuser
WORKDIR /app

COPY --from=builder /usr/local/lib/python3.13 /usr/local/lib/python3.13
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app/src ./src

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

EXPOSE 8000
CMD ["uvicorn", "whatsapp:app", "--host", "0.0.0.0", "--port", "8000"]