"""Offline tests. Fixtures mirror the live ``__NEXT_DATA__`` structure (checked 2026-10-31)
but contain synthetic review content."""

from __future__ import annotations

import json
from pathlib import Path
from unittest import mock

import pytest
import requests

import trustpilot_scraper as tp
from trustpilot_scraper import cli, scraper

FIXTURES = Path(__file__).parent / "fixtures"


def load(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


class FakeResponse:
    def __init__(self, text: str = "", status_code: int = 200) -> None:
        self.text = text
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")


def fake_get(pages: dict[int, FakeResponse], calls: list[str]):
    def _get(url, headers=None, timeout=None):
        calls.append(url)
        page = int(url.rsplit("page=", 1)[1])
        return pages.get(page, FakeResponse("", 404))

    return _get


@pytest.fixture
def two_pages(monkeypatch):
    calls: list[str] = []
    pages = {1: FakeResponse(load("page1.html")), 2: FakeResponse(load("page2.html"))}
    monkeypatch.setattr(scraper.requests, "get", fake_get(pages, calls))
    return calls


def test_version_and_exports():
    assert isinstance(tp.__version__, str) and tp.__version__
    for name in tp.__all__:
        assert hasattr(tp, name)


def test_legacy_import_path():
    from trustpilot_scraper.scraper import scrape_trustpilot_reviews

    assert scrape_trustpilot_reviews is tp.scrape_trustpilot_reviews


@pytest.mark.parametrize(
    ("given", "expected"),
    [
        ("www.example.com", "https://www.trustpilot.com/review/www.example.com"),
        ("example.com/", "https://www.trustpilot.com/review/example.com"),
        (
            "https://www.trustpilot.com/review/www.example.com?page=3#x",
            "https://www.trustpilot.com/review/www.example.com",
        ),
        (
            "https://uk.trustpilot.com/review/foo.co.uk/",
            "https://uk.trustpilot.com/review/foo.co.uk",
        ),
        ("www.trustpilot.com/review/foo.com", "https://www.trustpilot.com/review/foo.com"),
    ],
)
def test_normalize_url(given, expected):
    assert tp.normalize_url(given) == expected


@pytest.mark.parametrize("bad", ["", "   ", "https://example.com/review/x"])
def test_normalize_url_rejects(bad):
    with pytest.raises(ValueError):
        tp.normalize_url(bad)


def test_parse_reviews_html():
    reviews = tp.parse_reviews_html(load("page1.html"))
    assert [r["id"] for r in reviews] == ["rev0001", "rev0002", "rev0003"]


def test_parse_challenge_page_raises_blocked():
    with pytest.raises(tp.TrustpilotBlockedError):
        tp.parse_reviews_html(load("challenge.html"))


def test_parse_missing_next_data_raises():
    with pytest.raises(tp.TrustpilotParseError):
        tp.parse_reviews_html("<html><body>nothing</body></html>")


def test_parse_invalid_json_raises():
    html = '<script id="__NEXT_DATA__">{not json</script>'
    with pytest.raises(tp.TrustpilotParseError):
        tp.parse_next_data(html)


def test_parse_missing_reviews_key_raises():
    html = '<script id="__NEXT_DATA__">' + json.dumps({"props": {"pageProps": {}}}) + "</script>"
    with pytest.raises(tp.TrustpilotParseError):
        tp.parse_reviews_html(html)


def test_normalize_review_default_keys():
    raw = tp.parse_reviews_html(load("page1.html"))[0]
    assert tp.normalize_review(raw) == {
        "Date": "2026-10-29",
        "Author": "Reviewer 1",
        "Body": "Synthetic review body number 1.",
        "Heading": "Synthetic heading 1",
        "Rating": 5,
        "Location": "US",
    }


def test_normalize_review_extended_with_reply():
    raw = tp.parse_reviews_html(load("page1.html"))[1]
    row = tp.normalize_review(raw, extended=True)
    assert row["ReviewId"] == "rev0002"
    assert row["Reply"] == "Sorry to hear that."
    assert row["ReplyDate"] == "2026-10-29"
    assert row["ExperienceDate"] == "2026-10-27"
    assert row["Verified"] is False
    assert row["Likes"] == 2
    assert row["Language"] == "en"


def test_normalize_review_tolerates_missing_fields():
    assert tp.normalize_review({})["Author"] is None
    assert tp.normalize_review({}, extended=True)["Reply"] is None


def test_scrape_paginates_dedupes_and_stops_at_total_pages(two_pages):
    with mock.patch.object(scraper.time, "sleep") as sleep:
        reviews = tp.scrape_trustpilot_reviews("www.example.com", delay=1.5)
    assert [r["Author"] for r in reviews] == [f"Reviewer {i}" for i in range(1, 6)]
    assert two_pages == [
        "https://www.trustpilot.com/review/www.example.com?page=1",
        "https://www.trustpilot.com/review/www.example.com?page=2",
    ]
    sleep.assert_called_once_with(1.5)


def test_scrape_max_pages(two_pages):
    reviews = tp.scrape_trustpilot_reviews("www.example.com", max_pages=1, delay=0)
    assert len(reviews) == 3
    assert len(two_pages) == 1


def test_scrape_invalid_max_pages():
    with pytest.raises(ValueError):
        tp.scrape_trustpilot_reviews("www.example.com", max_pages=0)


def test_iter_is_lazy(two_pages):
    it = tp.iter_trustpilot_reviews("www.example.com", delay=0)
    assert next(it)["Author"] == "Reviewer 1"
    assert len(two_pages) == 1


@pytest.mark.parametrize("status", [403, 429])
def test_blocked_status_raises(monkeypatch, status):
    monkeypatch.setattr(
        scraper.requests, "get", lambda *a, **k: FakeResponse(load("challenge.html"), status)
    )
    with pytest.raises(tp.TrustpilotBlockedError):
        tp.scrape_trustpilot_reviews("www.example.com")


def test_challenge_with_200_raises(monkeypatch):
    monkeypatch.setattr(
        scraper.requests, "get", lambda *a, **k: FakeResponse(load("challenge.html"))
    )
    with pytest.raises(tp.TrustpilotBlockedError):
        tp.get_reviews_from_page("https://www.trustpilot.com/review/x.com?page=1")


def test_not_found_and_server_error(monkeypatch):
    monkeypatch.setattr(scraper.requests, "get", lambda *a, **k: FakeResponse("", 404))
    with pytest.raises(tp.TrustpilotError, match="not found"):
        tp.get_reviews_from_page("https://www.trustpilot.com/review/x.com")
    monkeypatch.setattr(scraper.requests, "get", lambda *a, **k: FakeResponse("", 500))
    with pytest.raises(tp.TrustpilotError):
        tp.get_reviews_from_page("https://www.trustpilot.com/review/x.com")


def test_network_error_wrapped(monkeypatch):
    def boom(*a, **k):
        raise requests.ConnectionError("down")

    monkeypatch.setattr(scraper.requests, "get", boom)
    with pytest.raises(tp.TrustpilotError, match="down"):
        tp.get_reviews_from_page("https://www.trustpilot.com/review/x.com")


def test_custom_session_is_used():
    session = mock.Mock(spec=requests.Session)
    session.get.return_value = FakeResponse(load("page1.html"))
    reviews = tp.get_reviews_from_page("https://www.trustpilot.com/review/x.com", session=session)
    assert len(reviews) == 3
    session.get.assert_called_once()


def test_cli_csv(two_pages, tmp_path, capsys):
    out = tmp_path / "r.csv"
    assert cli.main(["www.example.com", "--max-pages", "2", "--delay", "0", "-o", str(out)]) == 0
    lines = out.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "Date,Author,Body,Heading,Rating,Location"
    assert len(lines) == 6
    assert "wrote 5 reviews" in capsys.readouterr().err


def test_cli_json_stdout_extended(two_pages, capsys):
    assert cli.main(["www.example.com", "--extended"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert len(data) == 3 and "ReviewId" in data[0]


def test_cli_jsonl(two_pages, tmp_path):
    out = tmp_path / "r.jsonl"
    assert cli.main(["www.example.com", "-o", str(out)]) == 0
    assert len(out.read_text(encoding="utf-8").splitlines()) == 3


def test_cli_error_exit_code(monkeypatch, capsys):
    monkeypatch.setattr(scraper.requests, "get", lambda *a, **k: FakeResponse("", 403))
    assert cli.main(["www.example.com"]) == 1
    assert "blocked" in capsys.readouterr().err
