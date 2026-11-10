FROM python:3.13-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build

RUN python -m venv /opt/venv

ENV PATH="/opt/venv/bin:${PATH}"

COPY pyproject.toml ./
COPY src ./src

RUN pip install --upgrade pip \
    && pip install ".[deploy]"


FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:${PATH}"

RUN groupadd --system app \
    && useradd --system --gid app --home-dir /app app

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv

COPY --chown=app:app wsgi.py ./
COPY --chown=app:app migrations ./migrations
COPY --chown=app:app openapi ./openapi
COPY --chown=app:app docker-entrypoint.sh ./

RUN sed -i 's/\r$//' docker-entrypoint.sh \
    && chmod +x docker-entrypoint.sh \
    && mkdir -p /app/instance \
    && chown -R app:app /app

USER app

EXPOSE 5000

ENTRYPOINT ["./docker-entrypoint.sh"]

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--access-logfile", "-", "--error-logfile", "-", "wsgi:app"]