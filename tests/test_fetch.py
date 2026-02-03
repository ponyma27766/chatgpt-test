import os

import pipeline.fetch as fetch


class DummyResponse:
    def __init__(self, text: str, status_code: int = 200) -> None:
        self.text = text
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError("bad status")


SAMPLE_CSV = """Date,Open,High,Low,Close,Volume
2024-01-01,1,1,1,1,10
2024-01-02,2,2,2,2,20
"""


def test_fetch_caches_download(tmp_path, monkeypatch):
    calls = {"count": 0}

    def fake_get(url, params=None, timeout=10):
        calls["count"] += 1
        return DummyResponse(SAMPLE_CSV)

    monkeypatch.setattr(fetch.requests, "get", fake_get)

    config = fetch.FetchConfig(
        symbol="aapl.us",
        start="2024-01-01",
        end="2024-01-02",
        output_dir=str(tmp_path),
        fmt="csv",
        retries=2,
        backoff=0,
    )

    first = fetch.fetch_data(config)
    second = fetch.fetch_data(config)

    assert first == second
    assert os.path.exists(first)
    assert calls["count"] == 1
