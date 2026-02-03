#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
LOG_DIR="${LOG_DIR:-${ROOT_DIR}/logs}"
DATA_FILE="${DATA_FILE:-${ROOT_DIR}/data/last_update.txt}"
MAX_STALE_SECONDS="${MAX_STALE_SECONDS:-900}"
MIN_DISK_FREE_PERCENT="${MIN_DISK_FREE_PERCENT:-10}"
COMPOSE_DIR="${COMPOSE_DIR:-${ROOT_DIR}}"
COMPOSE_CMD=(docker compose)

mkdir -p "${LOG_DIR}"

log() {
  local level="$1"
  shift
  printf '%s [%s] %s\n' "$(date -Is)" "${level}" "$*" | tee -a "${LOG_DIR}/healthcheck.log"
}

failures=0

check_compose_running() {
  local services running missing
  if ! services="$(${COMPOSE_CMD[@]} -f "${COMPOSE_DIR}/docker-compose.yml" ps --services 2>/dev/null)"; then
    log "ERROR" "Unable to list docker compose services."
    return 1
  fi

  if [[ -z "${services}" ]]; then
    log "WARN" "No docker compose services found."
    return 0
  fi

  running="$(${COMPOSE_CMD[@]} -f "${COMPOSE_DIR}/docker-compose.yml" ps --status running --services 2>/dev/null || true)"
  missing=$(comm -23 <(printf '%s\n' "${services}" | sort) <(printf '%s\n' "${running}" | sort) || true)
  if [[ -n "${missing}" ]]; then
    log "ERROR" "Services not running: ${missing//$'\n'/, }"
    return 1
  fi

  log "INFO" "All compose services are running."
  return 0
}

check_last_update() {
  if [[ ! -f "${DATA_FILE}" ]]; then
    log "ERROR" "Last update file missing: ${DATA_FILE}"
    return 1
  fi

  local last_update now age
  last_update=$(cat "${DATA_FILE}" || echo 0)
  if [[ ! "${last_update}" =~ ^[0-9]+$ ]]; then
    log "ERROR" "Invalid last update timestamp in ${DATA_FILE}: ${last_update}"
    return 1
  fi

  now=$(date +%s)
  age=$((now - last_update))
  if (( age > MAX_STALE_SECONDS )); then
    log "ERROR" "Data stale: last update ${age}s ago (threshold ${MAX_STALE_SECONDS}s)."
    return 1
  fi

  log "INFO" "Data freshness OK: ${age}s ago."
  return 0
}

check_disk_space() {
  local used_percent free_percent
  used_percent=$(df -P "${ROOT_DIR}" | awk 'NR==2 {gsub(/%/, "", $5); print $5}')
  free_percent=$((100 - used_percent))
  if (( free_percent < MIN_DISK_FREE_PERCENT )); then
    log "ERROR" "Low disk space: ${free_percent}% free (threshold ${MIN_DISK_FREE_PERCENT}%)."
    return 1
  fi

  log "INFO" "Disk space OK: ${free_percent}% free."
  return 0
}

if ! check_compose_running; then
  failures=$((failures + 1))
fi

if ! check_last_update; then
  failures=$((failures + 1))
fi

if ! check_disk_space; then
  failures=$((failures + 1))
fi

if (( failures > 0 )); then
  log "ERROR" "Healthcheck failed with ${failures} issue(s)."
  exit 1
fi

log "INFO" "Healthcheck passed."
