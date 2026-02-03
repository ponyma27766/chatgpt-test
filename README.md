# chatgpt-test

## 最小监控与自愈（Docker Compose）

### 目录结构
- `monitor/healthcheck.sh`：健康检查（服务运行、数据更新、磁盘空间）
- `scripts/watchdog.sh`：定期执行健康检查，失败则自动重启 compose
- `scripts/install_watchdog_systemd.sh`：安装 systemd service + timer（Ubuntu 22.04）
- `data/last_update.txt`：最近一次数据更新时间（占位，写入 epoch 秒）
- `logs/`：健康检查与自愈日志

### 使用方式（systemd + timer，Ubuntu 22.04）
1. 先确保 `docker compose` 与 `docker-compose.yml` 已就绪，并能在仓库根目录运行。
2. 安装定时器（每 5 分钟执行一次）：
   ```bash
   sudo scripts/install_watchdog_systemd.sh
   ```
3. 查看运行状态：
   ```bash
   systemctl status compose-watchdog.timer
   ```
4. 手动触发一次：
   ```bash
   /workspace/chatgpt-test/scripts/watchdog.sh
   ```

### 配置参数（可选环境变量）
- `MAX_STALE_SECONDS`：数据更新阈值（默认 900 秒）
- `MIN_DISK_FREE_PERCENT`：磁盘最低可用百分比（默认 10）
- `DATA_FILE`：数据更新时间文件路径（默认 `data/last_update.txt`）
- `LOG_DIR`：日志目录（默认 `logs/`）
- `COMPOSE_DIR`：compose 目录（默认仓库根目录）

## 验收方式（DoD）
> 目标：服务挂了能自动拉起；磁盘/进程/端口异常能报警（先日志报警占位）。

1. **服务挂掉自动拉起**
   - 制造故障：
     ```bash
     docker compose stop <service>
     ```
   - 观察：等待 5 分钟或手动运行 `scripts/watchdog.sh`，查看 `logs/watchdog.log` 与 `logs/healthcheck.log`，确认出现“Healthcheck failed”与“restart complete”。

2. **数据更新超时报警（日志占位）**
   - 制造故障：
     ```bash
     echo $(( $(date +%s) - 99999 )) > data/last_update.txt
     ```
   - 观察：运行 `monitor/healthcheck.sh` 或等待 watchdog，查看 `logs/healthcheck.log` 中的 “Data stale”。

3. **磁盘空间不足报警（日志占位）**
   - 制造故障（示例，仅限测试环境）：
     ```bash
     fallocate -l 1G /tmp/disk-fill-test
     ```
     或调整 `MIN_DISK_FREE_PERCENT` 为较高数值后运行健康检查。
   - 观察：查看 `logs/healthcheck.log` 中的 “Low disk space”。

4. **端口/进程异常报警（日志占位）**
   - 目前通过 “compose 服务不在 running” 的检查来覆盖端口/进程异常。
   - 可模拟：`docker compose stop <service>` 或手动杀进程，观察日志告警。

## 常见故障排查
- **healthcheck 报错无法读取 compose 状态**：确认 `docker compose` 可在仓库根目录运行，且 `docker-compose.yml` 存在。
- **数据更新时间无效**：确保 `data/last_update.txt` 内容是 epoch 秒（纯数字）。
- **日志没有更新**：检查 `logs/` 目录权限；确认 systemd timer 已启用：`systemctl status compose-watchdog.timer`。
- **自动重启无效**：查看 `logs/watchdog.log`，确认 `docker compose restart` 是否成功执行。
