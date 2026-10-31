"""Competitor benchmark: compare two companies on rating, verification and reply speed.

Shows:
  * the ``extended=True`` fields: ``Verified``, ``Reply``, ``ReplyDate``
  * turning review dicts into a small comparison table with the standard library

Needs: ``pip install trustpilot_scraper``. Offline: uses the bundled synthetic pages for two
invented companies ("BrightParcel" and "SwiftCart"); no request reaches Trustpilot.

Run: python examples/competitor_benchmark.py
"""

from __future__ import annotations

from datetime import date
from statistics import mean, median
from typing import Any

from _samples import load_reviews


def summarize(reviews: list[dict[str, Any]]) -> dict[str, str]:
    replied = [r for r in reviews if r["Reply"] and r["ReplyDate"]]
    reply_days = [
        (date.fromisoformat(r["ReplyDate"]) - date.fromisoformat(r["Date"])).days for r in replied
    ]
    return {
        "reviews": str(len(reviews)),
        "avg rating": f"{mean(r['Rating'] for r in reviews):.2f}",
        "1-star share": f"{sum(r['Rating'] == 1 for r in reviews) / len(reviews):.0%}",
        "verified share": f"{sum(bool(r['Verified']) for r in reviews) / len(reviews):.0%}",
        "reply rate": f"{len(replied) / len(reviews):.0%}",
        "median reply (days)": f"{median(reply_days):.1f}" if reply_days else "n/a",
    }


def main() -> None:
    table = {name: summarize(load_reviews(name)) for name in ("brightparcel", "swiftcart")}
    metrics = list(next(iter(table.values())))
    print(f"{'metric':<22}" + "".join(f"{name:>14}" for name in table))
    for metric in metrics:
        print(f"{metric:<22}" + "".join(f"{table[name][metric]:>14}" for name in table))


if __name__ == "__main__":
    main()
