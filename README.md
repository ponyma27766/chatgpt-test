
# chatgpt-test

## 可复现实验框架（轻量版）

### 目录结构

- `experiments/train.py`：训练入口，写入 `runs/<run_id>/`
- `experiments/eval.py`：评估入口，写入同一 run 目录
- `experiments/compare_runs.py`：对比最近 N 次 run，输出 `reports/compare.md`

默认输出目录：

- `runs/<run_id>/metadata.json`：记录参数、数据版本标识、当前 git commit、运行时间
- `runs/<run_id>/config.json`：保存当次运行配置
- `runs/<run_id>/model.json`：保存 toy 模型参数
- `runs/<run_id>/train_metrics.json`、`eval_metrics.json`

### 快速开始

#### 1) 训练（支持 JSON/YAML 配置）

```bash
python -m experiments.train --config configs/toy.json
```

> 如果使用 YAML，需要安装 PyYAML：`pip install pyyaml`。

**示例配置（JSON）**

```json
{
  "data": {
    "seed": 7,
    "size": 256,
    "noise": 0.1,
    "version": "toy-v1"
  },
  "train": {
    "steps": 200,
    "lr": 0.1
  }
}
```

运行结束后会在 `runs/<run_id>/metadata.json` 中记录：

- 参数（config 内容）
- 数据版本标识（`data.version` 或由 data 参数哈希生成）
- 当前 git commit
- 开始/结束时间

#### 2) 评估

```bash
python -m experiments.eval --run-id <run_id>
```

或：

```bash
python -m experiments.eval --run-dir runs/<run_id>
```

评估结果写入 `runs/<run_id>/eval_metrics.json`。

#### 3) 对比最近 N 次 run

```bash
python -m experiments.compare_runs -n 5
```

对比结果写入 `reports/compare.md`（同时生成 JSON 版本）。

### 复现实验建议

1. 记录并固定配置文件（JSON/YAML）。
2. 使用相同的数据版本标识（`data.version`）。
3. 确认 `metadata.json` 中的 `git_commit` 与代码版本一致。
4. 通过 `compare_runs.py` 快速对比历史结果。

### Smoke Test（1-2 分钟内）

```bash
python -m experiments.smoke_test
```

该测试会跑最小训练、评估并生成一次对比报告，适合 CI 快速验证。

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

---

# Data pipeline (daily market data)

> 这部分是“抓取数据 + 校验数据”的最小用法示例。

## From zero to success

### 1) Fetch data

```bash
python3 -m pipeline.fetch \
  --symbol aapl.us \
  --start 2024-01-01 \
  --end 2024-01-31 \
  --output-dir data \
  --format csv
```

Expected output (path printed):

```text
data/aapl.us_2024-01-01_2024-01-31.csv
```

### 2) Validate data

```bash
python3 -m pipeline.validate \
  --input data/aapl.us_2024-01-01_2024-01-31.csv \
  --report-dir reports
```

Expected output (path printed):

```text
reports/validate_<timestamp>.md
```

### 3) Make targets (if Makefile exists)

```bash
make data
make validate
```



## 坦克大战小游戏

运行：

```bash
python tank_battle.py
```

操作：
- `WASD` 或方向键：移动/转向
- `Space` 或 `J`：开火
- `R`：失败后重开
- `Esc`：退出
