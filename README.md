# Python Project Skeleton (Beginner-Friendly)

Lightweight, reproducible, and deployable skeleton for Ubuntu 22.04 + Docker Compose.

## Project Structure

```text
.
├── docker-compose.yml
├── .env.example
├── pipeline/        # Data / ingestion artifacts
├── experiments/     # Training and evaluation notebooks/scripts
├── monitor/         # Health checks
├── scripts/         # start/stop/status/smoke_test
├── tests/           # Smoke tests
└── .github/
    └── workflows/   # CI
```

## Quick Start (Definition of Done)

### 1) One-click start

```bash
cp .env.example .env
./scripts/start.sh
```

### 2) Verify status

```bash
./scripts/status.sh
```

### 3) Run smoke test (inside container)

```bash
docker compose run --rm app
```

Expected output:

```text
Smoke test passed.
```

### 4) One-click stop

```bash
./scripts/stop.sh
```

## Notes

- The smoke test ensures required directories exist and checks the basic layout.
- The container uses the official `python:3.11-slim` image with the repo mounted at `/app`.

---

# 最小监控与自愈（Docker Compose）

> 这部分不影响你现在合并 PR，只是“多一个能力”：服务挂了能检测到，必要时自动重启（先记日志，后续可接告警）。

## 目录结构（说明）
- `monitor/healthcheck.sh`：健康检查（服务运行、数据更新、磁盘空间）
- `scripts/watchdog.sh`：定期执行健康检查，失败则自动重启 compose
- `scripts/install_watchdog_systemd.sh`：安装 systemd service + timer（Ubuntu 22.04）
- `data/last_update.txt`：最近一次数据更新时间（占位，写入 epoch 秒）
- `logs/`：健康检查与自愈日志

## 使用方式（systemd + timer，Ubuntu 22.04）
1. 确保仓库根目录能运行 `docker compose`（且有 `docker-compose.yml`）。
2. 安装定时器（每 5 分钟执行一次）：
   ```bash
   sudo scripts/install_watchdog_systemd.sh
   ```
3. 查看运行状态：
   ```bash
   systemctl status compose-watchdog.timer
   ```
4. 手动触发一次（可选）：
   ```bash
   scripts/watchdog.sh
   ```

## 配置参数（可选环境变量）
- `MAX_STALE_SECONDS`：数据更新阈值（默认 900 秒）
- `MIN_DISK_FREE_PERCENT`：磁盘最低可用百分比（默认 10）
- `DATA_FILE`：数据更新时间文件路径（默认 `data/last_update.txt`）
- `LOG_DIR`：日志目录（默认 `logs/`）
- `COMPOSE_DIR`：compose 目录（默认仓库根目录）
