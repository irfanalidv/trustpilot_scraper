# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-10-31

### Fixed
- **Packaging:** the 0.10 wheel on PyPI contained no Python code, because the modules sat at
  the repo root (`scraper.py`, `init.py`) instead of in a `trustpilot_scraper/` package. The
  package now installs and imports properly.
- Errors no longer fail silently. Network errors, HTTP 403/429, Trustpilot's bot-verification
  page and pages without review data now raise `TrustpilotError`,
  `TrustpilotBlockedError` or `TrustpilotParseError` instead of returning `[]`.
- Pagination stops at `filters.pagination.totalPages` instead of requesting pages until one
  fails.
- De-duplication now uses the review id and keeps page order (it used to scramble the order).

### Added
- `max_pages`, `delay`, `extended`, `session` and `timeout` options on
  `scrape_trustpilot_reviews`.
- `iter_trustpilot_reviews` (lazy generator), `parse_reviews_html`, `parse_next_data`,
  `normalize_review` and `normalize_url`. You can pass a bare domain such as `www.amazon.com`.
- `extended=True` adds `ReviewId`, `ExperienceDate`, `Verified`, `Likes`, `Language`, `Reply`
  and `ReplyDate`.
- `trustpilot-scraper` CLI with JSON, JSONL and CSV output.
- `__version__`, `py.typed`, type hints, an offline pytest suite with HTML fixtures, and CI on
  Python 3.10 to 3.13 with ruff.
- `SECURITY.md`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `CITATION.cff`, issue/PR templates and
  Dependabot.

### Changed
- Python 3.10+ required. Packaging moved to `pyproject.toml` (PEP 639 license metadata) and
  `setup.py` was removed.
- `pandas` is no longer required (it was only used to format dates). Install
  `trustpilot_scraper[pandas]` if you want it.

## [0.10] - 2024-04-16

- Last 0.x release.
