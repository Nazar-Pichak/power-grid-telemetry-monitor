FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install \
    --no-cache-dir \
    --requirement requirements.txt

COPY app ./app


FROM base AS test

COPY requirements-dev.txt .

RUN pip install \
    --no-cache-dir \
    --requirement requirements-dev.txt

COPY tests ./tests

CMD ["pytest", "--cov=app", "--cov-report=term-missing", "tests"]


FROM base AS runtime

CMD ["python", "-m", "app.main"]