from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict, List

from experiments.utils import load_config, save_json


def load_metrics(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    return load_config(path)


def summarize_run(run_dir: Path) -> Dict[str, Any]:
    metadata = load_metrics(run_dir / "metadata.json")
    train_metrics = load_metrics(run_dir / "train_metrics.json")
    eval_metrics = load_metrics(run_dir / "eval_metrics.json")

    return {
        "run_id": metadata.get("run_id", run_dir.name),
        "start_time": metadata.get("start_time", ""),
        "data_version": metadata.get("data_version", ""),
        "git_commit": metadata.get("git_commit", ""),
        "train_loss": train_metrics.get("train_loss", ""),
        "eval_mse": eval_metrics.get("eval_mse", ""),
    }


def collect_runs(root: Path, limit: int) -> List[Dict[str, Any]]:
    run_dirs = [p for p in root.iterdir() if p.is_dir()]
    run_dirs.sort(key=lambda p: (p.stat().st_mtime, p.name), reverse=True)
    summaries = [summarize_run(run_dir) for run_dir in run_dirs[:limit]]
    return summaries


def render_markdown(rows: List[Dict[str, Any]]) -> str:
    headers = ["run_id", "start_time", "data_version", "git_commit", "train_loss", "eval_mse"]
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(h, "")) for h in headers) + " |")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare recent experiment runs.")
    parser.add_argument("-n", "--num", type=int, default=5, help="Number of runs to compare.")
    parser.add_argument("--runs-root", default="runs", help="Runs directory.")
    parser.add_argument("--output", default="reports/compare.md", help="Output markdown path.")
    args = parser.parse_args()

    runs_root = Path(args.runs_root)
    runs_root.mkdir(parents=True, exist_ok=True)

    rows = collect_runs(runs_root, args.num)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_markdown(rows), encoding="utf-8")

    save_json(output.with_suffix(".json"), {"rows": rows})
    print(f"Wrote report to {output}")


if __name__ == "__main__":
    main()
