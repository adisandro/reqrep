FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Copy package metadata and source needed for installation.
COPY pyproject.toml README.md LICENSE.txt /app/
COPY src /app/src

RUN python -m pip install --upgrade pip && \
    python -m pip install .

# Users should bind-mount the project directory here at runtime.
WORKDIR /workspace

CMD ["/bin/sh"]
