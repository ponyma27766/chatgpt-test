from __future__ import annotations

import argparse
import math
import random
from pathlib import Path
from typing import Any, Dict, Tuple

from experiments.utils import load_config, save_json, set_seed


def generate_toy_data(seed: int, size: int, noise: float) -> Tuple[list[float], list[float]]:
    set_seed(seed)
    xs = [random.uniform(-1.0, 1.0) for _ in range(size)]
    ys = [2.0 * x + 1.0 + random.gauss(0.0, noise) for x in xs]
    return xs, ys


def evaluate(model: Dict[str, float], config: Dict[str, Any]) -> Dict[str, Any]:
    data_cfg = config.get("data", {})
    seed = int(data_cfg.get("eval_seed", data_cfg.get("seed", 11)))
    size = int(data_cfg.get("eval_size", 128))
    noise = float(data_cfg.get("noise", 0.1))

    xs, ys = generate_toy_data(seed, size, noise)
    w = float(model.get("w", 0.0))
    b = float(model.get("b", 0.0))
    mse = 0.0
    for x, y in zip(xs, ys):
        pred = w * x + b
        mse += (pred - y) ** 2
    mse /= len(xs)
    return {
        "eval_mse": mse,
        "eval_rmse": math.sqrt(mse),
        "eval_samples": len(xs),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate a trained run and write metrics.")
    parser.add_argument("--run-id", help="Run id to evaluate.")
    parser.add_argument("--run-dir", help="Run directory to evaluate.")
    args = parser.parse_args()

    if not args.run_id and not args.run_dir:
        raise SystemExit("Provide --run-id or --run-dir")

    run_dir = Path(args.run_dir) if args.run_dir else Path("runs") / args.run_id
    config_path = run_dir / "config.json"
    model_path = run_dir / "model.json"

    if not config_path.exists() or not model_path.exists():
        raise SystemExit(f"Missing config/model in {run_dir}")

    config = load_config(config_path)
    model = load_config(model_path)

    metrics = evaluate(model, config)
    save_json(run_dir / "eval_metrics.json", metrics)

    print(f"Eval completed for {run_dir.name}: {metrics}")


if __name__ == "__main__":
    main()
