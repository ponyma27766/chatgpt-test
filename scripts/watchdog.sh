#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
LOG_DIR="${LOG_DIR:-${ROOT_DIR}/logs}"
HEALTHCHECK_SCRIPT="${HEALTHCHECK_SCRIPT:-${ROOT_DIR}/monitor/healthcheck.sh}"
COMPOSE_DIR="${COMPOSE_DIR:-${ROOT_DIR}}"
COMPOSE_CMD=(docker compose)

mkdir -p "${LOG_DIR}"

log() {
  local level="$1"
  shift
  printf '%s [%s] %s\n' "$(date -Is)" "${level}" "$*" | tee -a "${LOG_DIR}/watchdog.log"
}

if "${HEALTHCHECK_SCRIPT}"; then
  log "INFO" "Healthcheck succeeded."
  exit 0
fi

log "ERROR" "Healthcheck failed. Restarting docker compose services."
if ${COMPOSE_CMD[@]} -f "${COMPOSE_DIR}/docker-compose.yml" restart >>"${LOG_DIR}/watchdog.log" 2>&1; then
  log "INFO" "Docker compose restart complete."
  exit 0
fi

log "ERROR" "Docker compose restart failed."
exit 1
