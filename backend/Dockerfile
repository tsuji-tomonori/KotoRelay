FROM ghcr.io/astral-sh/uv:0.10.0 AS uv
FROM python:3.12-slim
COPY --from=uv /uv /usr/local/bin/uv
RUN apt-get update && apt-get install -y --no-install-recommends tesseract-ocr tesseract-ocr-jpn ca-certificates && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY backend backend
ENV PATH="/app/.venv/bin:$PATH" PYTHONPATH="/app/backend/src" PYTHONUNBUFFERED=1
RUN useradd -m -u 10001 app && mkdir -p /data/objects && chown app:app /data/objects
USER app
CMD ["uvicorn", "kotorelay.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
