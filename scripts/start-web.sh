#!/bin/sh
set -eu

exec gunicorn \
  --bind "0.0.0.0:${PORT:-8000}" \
  --workers "${WEB_CONCURRENCY:-2}" \
  --timeout "${GUNICORN_TIMEOUT:-120}" \
  "${DJANGO_WSGI_MODULE:-config.wsgi:application}"
