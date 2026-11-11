"""Offline CLI tests for output-file handling (no network access)."""

from __future__ import annotations

from unittest import mock

from trustpilot_scraper import cli


def test_output_missing_directory_returns_clean_error(tmp_path, capsys):
    """-o into a nonexistent folder exits 1 with a message, not a traceback."""
    reviews = [{"Date": "2026-01-01", "Author": "alice"}]
    target = tmp_path / "no-such-dir" / "out.json"
    with mock.patch.object(cli, "scrape_trustpilot_reviews", return_value=reviews):
        rc = cli.main(["example.com", "-o", str(target)])
    assert rc == 1
    err = capsys.readouterr().err
    assert "no-such-dir" in err
    assert "Traceback" not in err
