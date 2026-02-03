#!/usr/bin/env python3
"""Validation utility for daily market data."""

from __future__ import annotations

import argparse
import csv
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Optional


@dataclass(frozen=True)
class ValidationResult:
    missing_values: int
    duplicate_dates: int
    non_monotonic: bool
    total_rows: int


def _parse_date(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d")


def _read_rows(path: str) -> Iterable[dict[str, str]]:
    if path.endswith(".parquet"):
        try:
            import pandas as pd  # type: ignore
        except ImportError as exc:
            raise RuntimeError("Parquet input requires pandas") from exc
        df = pd.read_parquet(path)
        return df.to_dict(orient="records")
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def validate_file(path: str) -> ValidationResult:
    rows = list(_read_rows(path))
    missing = 0
    dates_seen: set[str] = set()
    duplicate_dates = 0
    non_monotonic = False
    last_date: Optional[datetime] = None

    for row in rows:
        if any(value in (None, "") for value in row.values()):
            missing += 1
        date_value = row.get("Date")
        if not date_value:
            missing += 1
            continue
        if date_value in dates_seen:
            duplicate_dates += 1
        dates_seen.add(date_value)
        current = _parse_date(date_value)
        if last_date and current < last_date:
            non_monotonic = True
        last_date = current

    return ValidationResult(
        missing_values=missing,
        duplicate_dates=duplicate_dates,
        non_monotonic=non_monotonic,
        total_rows=len(rows),
    )


def write_report(result: ValidationResult, output_dir: str) -> str:
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(output_dir, f"validate_{timestamp}.md")
    status = "PASS" if (result.missing_values == 0 and result.duplicate_dates == 0 and not result.non_monotonic) else "FAIL"
    with open(report_path, "w", encoding="utf-8") as handle:
        handle.write(f"# Validation Report ({timestamp})\n\n")
        handle.write(f"Status: **{status}**\n\n")
        handle.write(f"- Total rows: {result.total_rows}\n")
        handle.write(f"- Missing values: {result.missing_values}\n")
        handle.write(f"- Duplicate dates: {result.duplicate_dates}\n")
        handle.write(f"- Non-monotonic dates: {result.non_monotonic}\n")
    return report_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate daily market data.")
    parser.add_argument("--input", required=True, help="Input CSV/Parquet file")
    parser.add_argument("--report-dir", default="reports", help="Report output directory")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = validate_file(args.input)
    report_path = write_report(result, args.report_dir)
    print(report_path)


if __name__ == "__main__":
    main()
