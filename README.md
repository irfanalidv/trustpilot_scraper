<div align="center">

# trustpilot-scraper

**Turn a company's public Trustpilot reviews into clean Python dicts, CSV or JSON, in one call.**

[![PyPI](https://img.shields.io/pypi/v/trustpilot_scraper?color=3fb950&label=PyPI)](https://pypi.org/project/trustpilot_scraper/)
[![Python](https://img.shields.io/pypi/pyversions/trustpilot_scraper)](https://pypi.org/project/trustpilot_scraper/)
[![Tests](https://github.com/irfanalidv/trustpilot_scraper/actions/workflows/tests.yml/badge.svg)](https://github.com/irfanalidv/trustpilot_scraper/actions/workflows/tests.yml)
[![Downloads](https://static.pepy.tech/badge/trustpilot_scraper)](https://pepy.tech/project/trustpilot_scraper)
[![License: MIT](https://img.shields.io/github/license/irfanalidv/trustpilot_scraper)](https://github.com/irfanalidv/trustpilot_scraper/blob/main/LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

</div>

The `trustpilot_scraper` library is a Python package for scraping Trustpilot reviews. Give it a
Trustpilot review page (or just the company's domain) and it returns every review as a dictionary.

Businesses can use it to collect Trustpilot reviews for market analysis, sentiment analysis and
competitor benchmarking, and to learn from customer feedback to improve products, services and
online reputation.

> **Heads-up (October 2026):** Trustpilot currently puts an AWS WAF bot-verification page in front
> of its review pages, and plain HTTP clients such as `requests` often get **HTTP 403**. When that
> happens this library raises `TrustpilotBlockedError` rather than quietly returning an empty list.
> The library does not try to get around the check. If you are blocked, save the page from your
> browser and parse it with `parse_reviews_html()` (see [below](#parse-html-you-already-have)). The
> page's data format was checked against a live page on 2026-10-31.

## Features

- Reads the page's embedded `__NEXT_DATA__` JSON instead of brittle CSS selectors.
- Handles pagination automatically, stopping at the real last page (or at `max_pages`).
- Retrieves date, author, body, heading, rating and location, and with `extended=True` also the
  review id, experience date, verification flag, likes, language and the company's reply.
- Removes duplicate reviews (by review id) and keeps page order.
- Waits politely between requests (2 s by default) and lets you pass your own `requests.Session`.
- Raises clear exceptions when something goes wrong: `TrustpilotBlockedError`,
  `TrustpilotParseError` and `TrustpilotError`.
- Includes a `trustpilot-scraper` command that writes JSON, JSONL or CSV.
- Fully typed (`py.typed`) and light: only `requests` and `beautifulsoup4` are required.

## Installation

```bash
pip install trustpilot_scraper
# optional: pandas, for working with results as a DataFrame
pip install "trustpilot_scraper[pandas]"
```

Requires Python 3.10+.

## Quick start

```python
from trustpilot_scraper import scrape_trustpilot_reviews

reviews = scrape_trustpilot_reviews(
    "https://www.trustpilot.com/review/www.example.com",  # or just "www.example.com"
    max_pages=2,   # omit to fetch every page
    delay=2.0,     # seconds between requests
)

for review in reviews:
    print(review)
```

Each review is a dict with the same keys as earlier versions:

```python
{'Date': '2026-10-29', 'Author': 'Reviewer 1', 'Body': 'Synthetic review body number 1.',
 'Heading': 'Synthetic heading 1', 'Rating': 5, 'Location': 'US'}
```

With `extended=True` each dict also has `ReviewId`, `ExperienceDate`, `Verified`, `Likes`,
`Language`, `Reply` and `ReplyDate`.

### Parse HTML you already have

```python
from pathlib import Path
from trustpilot_scraper import parse_reviews_html, normalize_review

html = Path("amazon_page1.html").read_text(encoding="utf-8")  # saved from your browser
reviews = [normalize_review(r, extended=True) for r in parse_reviews_html(html)]
```

### Handle blocking explicitly

```python
from trustpilot_scraper import scrape_trustpilot_reviews, TrustpilotBlockedError

try:
    reviews = scrape_trustpilot_reviews("www.example.com", max_pages=1)
except TrustpilotBlockedError as exc:
    print("Trustpilot refused the request:", exc)
```

### Command line

```bash
trustpilot-scraper www.example.com --max-pages 3 -o reviews.csv
trustpilot-scraper https://www.trustpilot.com/review/www.example.com --extended -o reviews.jsonl
trustpilot-scraper www.example.com            # JSON to stdout, first page only
```

The exit code is `1` and the error goes to stderr when a request is blocked or fails.

## Use cases

- **Sentiment analysis:** feed `Body` and `Rating` into your NLP pipeline.
- **Competitor benchmarking:** compare rating distributions across companies.
- **Customer-support QA:** use `extended=True` to see which reviews got a company reply.
- **Dashboards:** `pandas.DataFrame(reviews)` gives a ready-to-plot table.

## API overview

| Function | Purpose |
| --- | --- |
| `scrape_trustpilot_reviews(base_url, *, max_pages=None, delay=2.0, extended=False, session=None, timeout=30.0)` | Fetch all (or `max_pages`) pages and return a list of dicts. |
| `iter_trustpilot_reviews(...)` | The same, but as a lazy generator that fetches page by page. |
| `get_reviews_from_page(url, *, session=None, timeout=30.0)` | Fetch one page and return the raw Trustpilot review objects. |
| `parse_reviews_html(html)` | Pull the raw review objects out of an HTML string. |
| `parse_next_data(html)` | Return the whole decoded `__NEXT_DATA__` JSON. |
| `normalize_review(raw, *, extended=False)` | Turn a raw review object into the flat dict shown above. |
| `normalize_url(company)` | `"www.example.com"` becomes `"https://www.trustpilot.com/review/www.example.com"`. |

Exceptions: `TrustpilotError` (base class), `TrustpilotBlockedError` (HTTP 403/429 or a
verification page) and `TrustpilotParseError` (the page has no review data).

### Upgrading from 0.x

- `from trustpilot_scraper.scraper import scrape_trustpilot_reviews` still works, and the output
  keys are unchanged.
- Version 0.10 on PyPI shipped a wheel without the Python package in it. 1.0.0 fixes the packaging.
- Errors now raise exceptions instead of returning `[]`.
- `pandas` is no longer a required dependency.

## Responsible use

Only scrape public pages, keep the request rate low (the default delay is 2 s), and follow
Trustpilot's terms of use and the data-protection law that applies to you.

## Contributing

Pull requests are welcome. See [CONTRIBUTING.md](https://github.com/irfanalidv/trustpilot_scraper/blob/main/CONTRIBUTING.md).

```bash
pip install -e ".[dev]"
ruff check . && ruff format --check . && pytest
```

The tests run offline against saved HTML fixtures in `tests/fixtures/`.

## License

MIT. See [LICENSE](https://github.com/irfanalidv/trustpilot_scraper/blob/main/LICENSE).
