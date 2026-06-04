FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    APP_HOME=/app

WORKDIR ${APP_HOME}

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        libpq-dev \
        netcat-openbsd \
        postgresql-client \
        redis-tools \
    && rm -rf /var/lib/apt/lists/*

COPY . ${APP_HOME}

RUN python -m pip install --upgrade pip setuptools wheel \
    && if [ -f requirements.txt ]; then pip install -r requirements.txt; \
       elif [ -f pyproject.toml ]; then pip install .; \
       else echo "Missing requirements.txt or pyproject.toml in ${APP_HOME}" >&2; exit 1; \
       fi \
    && chmod +x ${APP_HOME}/scripts/*.sh

RUN groupadd --system app \
    && useradd --system --gid app --create-home --home-dir /home/app app \
    && mkdir -p ${APP_HOME}/staticfiles ${APP_HOME}/media \
    && chown -R app:app ${APP_HOME} /home/app

USER app

ENTRYPOINT ["/app/scripts/entrypoint.sh"]
CMD ["/app/scripts/start-web.sh"]
