from __future__ import annotations

import argparse
import math
import random
from pathlib import Path
from typing import Any, Dict, Tuple

from experiments.utils import data_version, generate_run_id, git_commit, load_config, save_json, set_seed, utc_now


def generate_toy_data(seed: int, size: int, noise: float) -> Tuple[list[float], list[float]]:
    set_seed(seed)
    xs = [random.uniform(-1.0, 1.0) for _ in range(size)]
    ys = [2.0 * x + 1.0 + random.gauss(0.0, noise) for x in xs]
    return xs, ys


def train_linear_regression(xs: list[float], ys: list[float], steps: int, lr: float) -> Tuple[float, float, float]:
    w, b = 0.0, 0.0
    n = len(xs)
    loss = 0.0
    for _ in range(steps):
        dw = 0.0
        db = 0.0
        loss = 0.0
        for x, y in zip(xs, ys):
            pred = w * x + b
            error = pred - y
            loss += error ** 2
            dw += 2.0 * error * x
            db += 2.0 * error
        loss /= n
        w -= lr * dw / n
        b -= lr * db / n
    return w, b, loss


def train(config: Dict[str, Any], run_dir: Path) -> Dict[str, Any]:
    data_cfg = config.get("data", {})
    train_cfg = config.get("train", {})

    seed = int(data_cfg.get("seed", 7))
    size = int(data_cfg.get("size", 256))
    noise = float(data_cfg.get("noise", 0.1))
    steps = int(train_cfg.get("steps", 200))
    lr = float(train_cfg.get("lr", 0.1))

    xs, ys = generate_toy_data(seed, size, noise)
    w, b, loss = train_linear_regression(xs, ys, steps, lr)

    metrics = {
        "train_loss": loss,
        "train_rmse": math.sqrt(loss),
        "steps": steps,
    }
    save_json(run_dir / "model.json", {"w": w, "b": b})
    save_json(run_dir / "train_metrics.json", metrics)
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Train a toy model and log reproducible metadata.")
    parser.add_argument("--config", required=True, help="Path to YAML or JSON config.")
    parser.add_argument("--run-id", help="Override run id.")
    args = parser.parse_args()

    config_path = Path(args.config)
    config = load_config(config_path)

    run_id = args.run_id or generate_run_id()
    run_dir = Path("runs") / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    start_time = utc_now()
    metrics = train(config, run_dir)
    end_time = utc_now()

    metadata = {
        "run_id": run_id,
        "config": config,
        "config_path": str(config_path),
        "data_version": data_version(config),
        "git_commit": git_commit(),
        "start_time": start_time,
        "end_time": end_time,
    }
    save_json(run_dir / "metadata.json", metadata)
    save_json(run_dir / "config.json", config)

    print(f"Run completed: {run_id}")
    print(f"Metrics: {metrics}")


if __name__ == "__main__":
    main()
