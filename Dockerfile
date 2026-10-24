FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY src ./src
COPY config ./config
COPY alembic.ini ./
COPY alembic ./alembic

RUN pip install --no-cache-dir .

RUN useradd -m -u 1000 chainbreaker && \
    mkdir -p runtime/databases runtime/uploads runtime/reports && \
    chown -R chainbreaker:chainbreaker /app

USER chainbreaker

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/api/health || exit 1

CMD ["python", "-m", "uvicorn", "chainbreaker.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
