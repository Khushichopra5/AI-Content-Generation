#!/bin/sh
set -eu

exec celery -A "${CELERY_APP:-config.celery:app}" beat --loglevel "${CELERY_LOGLEVEL:-info}"
