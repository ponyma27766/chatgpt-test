#!/usr/bin/env python3
"""Minimal daily market data fetcher with caching and retries."""

from __future__ import annotations

import argparse
import csv
import os
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Optional

try:
    import requests  # type: ignore
except ImportError:  # pragma: no cover - fallback for minimal environments
    import urllib.error
    import urllib.parse
    import urllib.request

    class _Response:
        def __init__(self, text: str, status_code: int) -> None:
            self.text = text
            self.status_code = status_code

        def raise_for_status(self) -> None:
            if self.status_code >= 400:
                raise RuntimeError(f"HTTP {self.status_code}")

    class _RequestsShim:
        @staticmethod
        def get(url: str, params: Optional[dict[str, str]] = None, timeout: int = 10) -> _Response:
            query = urllib.parse.urlencode(params or {})
            full_url = f"{url}?{query}" if query else url
            try:
                with urllib.request.urlopen(full_url, timeout=timeout) as response:
                    text = response.read().decode("utf-8")
                    return _Response(text, response.status)
            except urllib.error.HTTPError as exc:
                return _Response(exc.read().decode("utf-8"), exc.code)

    requests = _RequestsShim()  # type: ignore

DEFAULT_BASE_URL = "https://stooq.com/q/d/l/"


@dataclass(frozen=True)
class FetchConfig:
    symbol: str
    start: Optional[str]
    end: Optional[str]
    output_dir: str
    fmt: str
    retries: int
    backoff: float
    base_url: str = DEFAULT_BASE_URL


class FetchError(RuntimeError):
    pass


def _parse_date(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d")


def _iter_filtered_rows(rows: Iterable[dict[str, str]], start: Optional[str], end: Optional[str]) -> list[dict[str, str]]:
    start_dt = _parse_date(start) if start else None
    end_dt = _parse_date(end) if end else None
    filtered: list[dict[str, str]] = []
    for row in rows:
        if not row.get("Date"):
            continue
        current = _parse_date(row["Date"])
        if start_dt and current < start_dt:
            continue
        if end_dt and current > end_dt:
            continue
        filtered.append(row)
    return filtered


def _build_output_path(config: FetchConfig) -> str:
    start = config.start or "start"
    end = config.end or "end"
    filename = f"{config.symbol}_{start}_{end}.{config.fmt}"
    return os.path.join(config.output_dir, filename)


def fetch_data(config: FetchConfig) -> str:
    os.makedirs(config.output_dir, exist_ok=True)
    output_path = _build_output_path(config)

    if os.path.exists(output_path):
        return output_path

    params = {"s": config.symbol, "i": "d"}
    for attempt in range(1, config.retries + 1):
        try:
            response = requests.get(config.base_url, params=params, timeout=10)
            response.raise_for_status()
            rows = list(csv.DictReader(response.text.splitlines()))
            filtered = _iter_filtered_rows(rows, config.start, config.end)
            if not filtered:
                raise FetchError("No data returned for requested range")

            if config.fmt == "csv":
                with open(output_path, "w", newline="", encoding="utf-8") as handle:
                    writer = csv.DictWriter(handle, fieldnames=filtered[0].keys())
                    writer.writeheader()
                    writer.writerows(filtered)
            elif config.fmt == "parquet":
                try:
                    import pandas as pd  # type: ignore
                except ImportError as exc:
                    raise FetchError("Parquet output requires pandas") from exc
                df = pd.DataFrame(filtered)
                df.to_parquet(output_path, index=False)
            else:
                raise FetchError(f"Unsupported format: {config.fmt}")

            return output_path
        except Exception as exc:  # noqa: BLE001 - retryable fetch errors
            if attempt < config.retries:
                time.sleep(config.backoff * attempt)
            else:
                raise FetchError(f"Failed to fetch data after {config.retries} attempts") from exc
    raise FetchError("Unexpected fetch failure")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch daily market data with caching.")
    parser.add_argument("--symbol", required=True, help="Market symbol, e.g. aapl.us")
    parser.add_argument("--start", help="Start date YYYY-MM-DD")
    parser.add_argument("--end", help="End date YYYY-MM-DD")
    parser.add_argument("--output-dir", default="data", help="Output directory")
    parser.add_argument("--format", default="csv", choices=["csv", "parquet"], help="Output format")
    parser.add_argument("--retries", type=int, default=3, help="Retry attempts")
    parser.add_argument("--backoff", type=float, default=1.0, help="Backoff seconds multiplier")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = FetchConfig(
        symbol=args.symbol,
        start=args.start,
        end=args.end,
        output_dir=args.output_dir,
        fmt=args.format,
        retries=args.retries,
        backoff=args.backoff,
    )
    output_path = fetch_data(config)
    print(output_path)


if __name__ == "__main__":
    main()
