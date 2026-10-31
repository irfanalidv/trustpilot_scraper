# Contributing to trustpilot_scraper

Thanks for helping improve `trustpilot_scraper`!

## Development setup

```bash
git clone https://github.com/irfanalidv/trustpilot_scraper.git
cd trustpilot_scraper
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"   # or: uv pip install -e ".[dev,pandas]"
pre-commit install        # optional: ruff on every commit
```

## Before opening a pull request

```bash
ruff check .                    # lint
ruff format --check .           # formatting
mypy trustpilot_scraper         # types
pytest --cov=trustpilot_scraper --cov-fail-under=100  # tests (offline) and coverage
```

Tests never contact Trustpilot: they use saved fixtures in `tests/fixtures/`, and
`tests/test_examples.py` runs the offline examples.

- Add or update tests for any behaviour change.
- Add a line to `CHANGELOG.md` under **Unreleased**.
- Keep pull requests focused: one fix or feature per PR.

## Reporting bugs and requesting features

Use the [issue templates](https://github.com/irfanalidv/trustpilot_scraper/issues/new/choose).
