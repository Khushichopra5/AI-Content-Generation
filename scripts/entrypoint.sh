#!/bin/sh
set -eu

log() {
  printf '%s %s\n' "[entrypoint]" "$*"
}

wait_for_tcp() {
  host="$1"
  port="$2"
  name="$3"
  timeout="$4"
  elapsed=0

  while ! nc -z "$host" "$port" >/dev/null 2>&1; do
    elapsed=$((elapsed + 1))
    if [ "$elapsed" -ge "$timeout" ]; then
      log "Timed out waiting for ${name} at ${host}:${port}"
      exit 1
    fi
    sleep 1
  done

  log "${name} is available at ${host}:${port}"
}

if [ "${WAIT_FOR_DB:-1}" = "1" ] && [ -n "${POSTGRES_HOST:-}" ]; then
  wait_for_tcp "${POSTGRES_HOST}" "${POSTGRES_PORT:-5432}" "PostgreSQL" "${DB_WAIT_TIMEOUT:-60}"
fi

if [ "${WAIT_FOR_REDIS:-1}" = "1" ] && [ -n "${REDIS_HOST:-}" ]; then
  wait_for_tcp "${REDIS_HOST}" "${REDIS_PORT:-6379}" "Redis" "${REDIS_WAIT_TIMEOUT:-60}"
fi

if [ "${RUN_DB_MIGRATIONS:-0}" = "1" ]; then
  log "Running Django migrations"
  python manage.py migrate --noinput
fi

if [ "${COLLECT_STATIC:-0}" = "1" ]; then
  log "Collecting static assets"
  python manage.py collectstatic --noinput
fi

exec "$@"
