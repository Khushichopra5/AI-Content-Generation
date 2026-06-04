#!/bin/sh
set -eu

exec celery -A "${CELERY_APP:-config.celery:app}" worker --loglevel "${CELERY_LOGLEVEL:-info}"
