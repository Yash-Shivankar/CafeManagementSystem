# syntax=docker/dockerfile:1

# A-07: there was no container story at all — "works on my machine" was the
# deployment plan. Two stages so the image that runs in production does not
# carry a compiler or the dev dependencies.

# ---------- build ----------
FROM python:3.12-slim AS build

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Only the dependency manifest, so this layer is cached until it changes —
# rebuilding after a code edit does not reinstall SQLAlchemy.
COPY requirements.txt ./
RUN python -m venv /opt/venv \
 && /opt/venv/bin/pip install --upgrade pip \
 && /opt/venv/bin/pip install -r requirements.txt

# ---------- runtime ----------
FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH"

# Not root. A container that runs as root turns a file-write bug into a host
# problem, and this app accepts uploads.
RUN useradd --create-home --uid 10001 caelum

WORKDIR /app

COPY --from=build /opt/venv /opt/venv
COPY --chown=caelum:caelum . .

# Uploaded documents live here; the volume is mounted over it in compose.
RUN mkdir -p /app/app/media && chown -R caelum:caelum /app/app/media

USER caelum

EXPOSE 8000

# /health/ready checks the database, which is what "ready to take traffic"
# actually means; /health alone only proves the process is up.
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health/ready', timeout=4).status==200 else 1)"

# No --reload: that is a development flag, and it disables the worker model.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
