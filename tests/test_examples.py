"""Run the offline examples end to end so the README's recipes cannot silently rot."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"

OFFLINE = {
    "complaint_themes.py": "Company replied to 13/24 reviews",
    "competitor_benchmark.py": "reply rate",
    "offline_pipeline_test.py": "collected 24 reviews from 3 pages",
    "monthly_trend_pandas.py": "wrote 24 rows",
}
NETWORK = {"live_scrape.py"}


@pytest.mark.parametrize("script", sorted(OFFLINE))
def test_example_runs_offline(script: str) -> None:
    if script == "monthly_trend_pandas.py" and importlib.util.find_spec("pandas") is None:
        pytest.skip("pandas not installed (pip install 'trustpilot_scraper[pandas]')")
    proc = subprocess.run(
        [sys.executable, str(EXAMPLES / script)],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    assert OFFLINE[script] in proc.stdout


def test_every_example_is_listed() -> None:
    scripts = {p.name for p in EXAMPLES.glob("*.py") if not p.name.startswith("_")}
    assert scripts == set(OFFLINE) | NETWORK


def test_sample_pages_are_reproducible(tmp_path: Path) -> None:
    """The committed synthetic pages match what the generator produces."""
    generator = EXAMPLES / "data" / "generate_sample_pages.py"
    committed = {p.name: p.read_bytes() for p in (EXAMPLES / "data").glob("*.html")}
    copy = tmp_path / generator.name
    copy.write_bytes(generator.read_bytes())
    subprocess.run([sys.executable, str(copy)], check=True, capture_output=True)
    regenerated = {p.name: p.read_bytes() for p in tmp_path.glob("*.html")}
    assert regenerated == committed
