from __future__ import annotations

from pathlib import Path

from monitor.healthcheck import verify_project_layout


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    missing = verify_project_layout(repo_root)
    if missing:
        missing_list = ", ".join(missing)
        raise SystemExit(f"Smoke test failed. Missing: {missing_list}")
    print("Smoke test passed.")


if __name__ == "__main__":
    main()
