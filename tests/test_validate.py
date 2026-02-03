import csv
import os

import pipeline.validate as validate


def _write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["Date", "Open"])
        writer.writeheader()
        writer.writerows(rows)


def test_validate_detects_issues_and_writes_report(tmp_path):
    rows = [
        {"Date": "2024-01-02", "Open": "2"},
        {"Date": "2024-01-01", "Open": ""},
        {"Date": "2024-01-01", "Open": "1"},
    ]
    csv_path = tmp_path / "data.csv"
    _write_csv(csv_path, rows)

    result = validate.validate_file(str(csv_path))
    assert result.total_rows == 3
    assert result.missing_values >= 1
    assert result.duplicate_dates == 1
    assert result.non_monotonic is True

    report_path = validate.write_report(result, str(tmp_path))
    assert os.path.exists(report_path)
