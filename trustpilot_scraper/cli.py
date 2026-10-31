"""Command-line interface: ``trustpilot-scraper www.example.com --max-pages 2 -o out.csv``."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from . import __version__
from .scraper import TrustpilotError, scrape_trustpilot_reviews


def _write(reviews: list[dict[str, Any]], output: str | None) -> None:
    if output is None or output == "-":
        json.dump(reviews, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return
    path = Path(output)
    if path.suffix.lower() == ".csv":
        fields = list(reviews[0].keys()) if reviews else []
        with path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fields)
            writer.writeheader()
            writer.writerows(reviews)
    elif path.suffix.lower() == ".jsonl":
        with path.open("w", encoding="utf-8") as fh:
            for row in reviews:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    else:
        path.write_text(json.dumps(reviews, ensure_ascii=False, indent=2), encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="trustpilot-scraper",
        description="Scrape public Trustpilot reviews for a company.",
    )
    parser.add_argument("company", help="company domain (www.example.com) or Trustpilot URL")
    pages = parser.add_mutually_exclusive_group()
    pages.add_argument("--max-pages", type=int, default=1, help="pages to fetch (default: 1)")
    pages.add_argument("--all-pages", action="store_true", help="fetch every page (mind the delay)")
    parser.add_argument(
        "--delay", type=float, default=2.0, help="seconds between requests (default: 2)"
    )
    parser.add_argument(
        "--timeout", type=float, default=30.0, help="per-request timeout in seconds (default: 30)"
    )
    parser.add_argument("--extended", action="store_true", help="include extra review fields")
    parser.add_argument(
        "-o", "--output", help="output file (.json, .jsonl or .csv); default: JSON to stdout"
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = parser.parse_args(argv)

    try:
        reviews = scrape_trustpilot_reviews(
            args.company,
            max_pages=None if args.all_pages else args.max_pages,
            delay=args.delay,
            extended=args.extended,
            timeout=args.timeout,
        )
    except (TrustpilotError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    _write(reviews, args.output)
    if args.output and args.output != "-":
        print(f"wrote {len(reviews)} reviews to {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
