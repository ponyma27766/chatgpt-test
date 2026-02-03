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
