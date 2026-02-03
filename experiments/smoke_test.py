from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path


def main() -> None:
    config = {
        "data": {"seed": 3, "size": 128, "noise": 0.05, "version": "toy-v1"},
        "train": {"steps": 120, "lr": 0.2},
    }
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.json"
        config_path.write_text(json.dumps(config), encoding="utf-8")
        subprocess.check_call(["python", "-m", "experiments.train", "--config", str(config_path)])
        # Find latest run directory by mtime.
        runs_root = Path("runs")
        run_dirs = sorted(
            [p for p in runs_root.iterdir() if p.is_dir()],
            key=lambda p: (p.stat().st_mtime, p.name),
            reverse=True,
        )
        if not run_dirs:
            raise SystemExit("No runs created during smoke test")
        run_dir = run_dirs[0]
        subprocess.check_call(["python", "-m", "experiments.eval", "--run-dir", str(run_dir)])
        subprocess.check_call(["python", "-m", "experiments.compare_runs", "-n", "1"])


if __name__ == "__main__":
    main()
