from __future__ import annotations

from pathlib import Path

REQUIRED_DIRS = [
    "pipeline",
    "experiments",
    "monitor",
    "scripts",
    "tests",
]


def verify_project_layout(base_path: Path) -> list[str]:
    missing = [name for name in REQUIRED_DIRS if not (base_path / name).exists()]
    return missing


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    missing = verify_project_layout(repo_root)
    if missing:
        missing_list = ", ".join(missing)
        raise SystemExit(f"Missing required directories: {missing_list}")
    print("Healthcheck OK: required directories exist.")


if __name__ == "__main__":
    main()
