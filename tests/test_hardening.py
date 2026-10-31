"""Tests for URL validation, header handling, Retry-After and CLI options."""

from __future__ import annotations

import json
import runpy
import sys
from pathlib import Path
from unittest import mock

import pytest
import requests

import trustpilot_scraper as tp
from trustpilot_scraper import cli, scraper

FIXTURES = Path(__file__).parent / "fixtures"
PAGE1 = (FIXTURES / "page1.html").read_text(encoding="utf-8")


class Resp:
    def __init__(self, text: str = "", status_code: int = 200, headers=None) -> None:
        self.text = text
        self.status_code = status_code
        self.headers = headers or {}

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")


@pytest.mark.parametrize(
    "url",
    [
        "https://nottrustpilot.com/review/x.com",
        "https://trustpilot.example.org/review/x.com",
        "https://trustpilot.com.evil.io/review/x.com",
        "ftp://www.trustpilot.com/review/x.com",
        "https://user@evil.com/review/trustpilot.com",
    ],
)
def test_normalize_url_rejects_lookalike_hosts(url: str) -> None:
    with pytest.raises(ValueError, match="not a Trustpilot URL"):
        tp.normalize_url(url)


@pytest.mark.parametrize(
    "url",
    [
        "https://trustpilot.com/review/x.com",
        "https://de.trustpilot.com/review/x.de",
        "https://www.trustpilot.co.uk/review/x.co.uk",
        "http://WWW.TRUSTPILOT.COM/review/x.com",
    ],
)
def test_normalize_url_accepts_trustpilot_hosts(url: str) -> None:
    assert tp.normalize_url(url).endswith("/review/" + url.rsplit("/", 1)[1])


def test_default_headers_sent_without_session(monkeypatch) -> None:
    seen = {}

    def get(url, headers=None, timeout=None):
        seen.update(headers=headers, timeout=timeout)
        return Resp(PAGE1)

    monkeypatch.setattr(scraper.requests, "get", get)
    tp.get_reviews_from_page("https://www.trustpilot.com/review/x.com", timeout=5)
    assert seen["headers"] == scraper.DEFAULT_HEADERS
    assert seen["headers"] is not scraper.DEFAULT_HEADERS  # a copy: callers cannot mutate it
    assert seen["timeout"] == 5


def test_session_custom_headers_are_not_overridden() -> None:
    session = requests.Session()
    session.headers["user-agent"] = "my-research-bot/1.0 (me@example.org)"
    with mock.patch.object(session, "get", return_value=Resp(PAGE1)) as get:
        tp.get_reviews_from_page("https://www.trustpilot.com/review/x.com", session=session)
    sent = get.call_args.kwargs["headers"]
    assert "User-Agent" not in sent  # the session's own value wins when requests merges
    assert sent["Accept-Language"] == scraper.DEFAULT_HEADERS["Accept-Language"]


def test_plain_session_still_gets_default_user_agent() -> None:
    session = requests.Session()  # generic python-requests UA
    with mock.patch.object(session, "get", return_value=Resp(PAGE1)) as get:
        tp.get_reviews_from_page("https://www.trustpilot.com/review/x.com", session=session)
    assert get.call_args.kwargs["headers"] == scraper.DEFAULT_HEADERS


@pytest.mark.parametrize(
    ("headers", "expected"),
    [
        ({"Retry-After": "120"}, 120.0),
        ({"Retry-After": "Wed, 21 Oct 2015 07:28:00 GMT"}, None),
        ({}, None),
    ],
)
def test_blocked_error_carries_status_and_retry_after(monkeypatch, headers, expected) -> None:
    monkeypatch.setattr(scraper.requests, "get", lambda *a, **k: Resp("", 429, headers))
    with pytest.raises(tp.TrustpilotBlockedError) as info:
        tp.get_reviews_from_page("https://www.trustpilot.com/review/x.com")
    assert info.value.status_code == 429
    assert info.value.retry_after == expected


def test_challenge_page_blocked_error_has_no_status() -> None:
    challenge = (FIXTURES / "challenge.html").read_text(encoding="utf-8")
    with pytest.raises(tp.TrustpilotBlockedError) as info:
        tp.parse_next_data(challenge)
    assert info.value.status_code is None


def test_parse_edge_cases() -> None:
    def page(obj: object) -> str:
        return f'<script id="__NEXT_DATA__">{json.dumps(obj)}</script>'

    with pytest.raises(tp.TrustpilotParseError, match="not an object"):
        tp.parse_next_data(page([1, 2]))
    with pytest.raises(tp.TrustpilotParseError, match="pageProps"):
        tp.parse_reviews_html(page({"props": {}}))
    with pytest.raises(tp.TrustpilotParseError, match="pageProps is not an object"):
        tp.parse_reviews_html(page({"props": {"pageProps": []}}))
    with pytest.raises(tp.TrustpilotParseError, match="not a list"):
        tp.parse_reviews_html(page({"props": {"pageProps": {"reviews": {}}}}))


def test_scrape_stops_on_empty_page_when_total_unknown(monkeypatch) -> None:
    body = {"props": {"pageProps": {"reviews": [{"id": "a", "text": "x"}]}}}
    empty = {"props": {"pageProps": {"reviews": []}}}
    pages = {
        1: f'<script id="__NEXT_DATA__">{json.dumps(body)}</script>',
        2: f'<script id="__NEXT_DATA__">{json.dumps(empty)}</script>',
    }
    calls: list[str] = []

    def get(url, headers=None, timeout=None):
        calls.append(url)
        return Resp(pages[int(url.rsplit("=", 1)[1])])

    monkeypatch.setattr(scraper.requests, "get", get)
    assert [r["Body"] for r in tp.scrape_trustpilot_reviews("x.com", delay=0)] == ["x"]
    assert len(calls) == 2


def test_cli_all_pages_and_timeout(monkeypatch, capsys) -> None:
    captured = {}

    def fake_scrape(company, **kwargs):
        captured.update(kwargs)
        return []

    monkeypatch.setattr(cli, "scrape_trustpilot_reviews", fake_scrape)
    assert cli.main(["x.com", "--all-pages", "--timeout", "7", "--delay", "3"]) == 0
    assert captured == {"max_pages": None, "delay": 3.0, "extended": False, "timeout": 7.0}
    assert json.loads(capsys.readouterr().out) == []


def test_cli_rejects_both_page_options(capsys) -> None:
    with pytest.raises(SystemExit):
        cli.main(["x.com", "--all-pages", "--max-pages", "2"])
    assert "not allowed with" in capsys.readouterr().err


def test_cli_writes_json_file_and_empty_csv(monkeypatch, tmp_path) -> None:
    rows = [{"Author": "A", "Rating": 5}]
    monkeypatch.setattr(cli, "scrape_trustpilot_reviews", lambda company, **kw: rows)
    out = tmp_path / "r.json"
    assert cli.main(["x.com", "-o", str(out)]) == 0
    assert json.loads(out.read_text(encoding="utf-8")) == rows

    monkeypatch.setattr(cli, "scrape_trustpilot_reviews", lambda company, **kw: [])
    empty = tmp_path / "empty.csv"
    assert cli.main(["x.com", "-o", str(empty)]) == 0
    assert empty.read_text(encoding="utf-8").strip() == ""


def test_python_dash_m_entry_point(monkeypatch, capsys) -> None:
    monkeypatch.setattr(sys, "argv", ["trustpilot_scraper", "--version"])
    with pytest.raises(SystemExit) as info:
        runpy.run_module("trustpilot_scraper", run_name="__main__")
    assert info.value.code == 0
    assert tp.__version__ in capsys.readouterr().out
