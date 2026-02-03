#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
SERVICE_NAME="compose-watchdog"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
TIMER_FILE="/etc/systemd/system/${SERVICE_NAME}.timer"

if [[ $EUID -ne 0 ]]; then
  echo "Please run as root (sudo)."
  exit 1
fi

cat <<SERVICE >"${SERVICE_FILE}"
[Unit]
Description=Docker Compose Watchdog
After=network-online.target docker.service
Wants=network-online.target

[Service]
Type=oneshot
WorkingDirectory=${ROOT_DIR}
Environment=LOG_DIR=${ROOT_DIR}/logs
Environment=DATA_FILE=${ROOT_DIR}/data/last_update.txt
Environment=COMPOSE_DIR=${ROOT_DIR}
ExecStart=${ROOT_DIR}/scripts/watchdog.sh
SERVICE

cat <<TIMER >"${TIMER_FILE}"
[Unit]
Description=Run Docker Compose Watchdog every 5 minutes

[Timer]
OnBootSec=2min
OnUnitActiveSec=5min
Unit=${SERVICE_NAME}.service

[Install]
WantedBy=timers.target
TIMER

systemctl daemon-reload
systemctl enable --now "${SERVICE_NAME}.timer"

systemctl status "${SERVICE_NAME}.timer" --no-pager
