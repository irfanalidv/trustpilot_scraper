"""Helpers shared by the examples: load the bundled synthetic pages.

``examples/data/`` holds saved review pages for two invented companies, ``brightparcel``
(3 pages) and ``swiftcart`` (2 pages). They mirror the structure of a real Trustpilot page
but contain no real reviews. Regenerate them with ``data/generate_sample_pages.py``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trustpilot_scraper import normalize_review, parse_reviews_html

DATA = Path(__file__).resolve().parent / "data"


def sample_pages(company: str) -> list[Path]:
    """Saved pages for ``company`` in page order."""
    pages = sorted(DATA.glob(f"{company}_page*.html"))
    if not pages:
        raise FileNotFoundError(f"no sample pages for {company!r} in {DATA}")
    return pages


def load_reviews(company: str, *, extended: bool = True) -> list[dict[str, Any]]:
    """Parse every saved page for ``company`` into normalized review dicts."""
    rows: list[dict[str, Any]] = []
    for page in sample_pages(company):
        html = page.read_text(encoding="utf-8")
        rows.extend(normalize_review(r, extended=extended) for r in parse_reviews_html(html))
    return rows
