"""Monthly rating trend with pandas, plus a CSV export for a dashboard.

Shows:
  * ``pandas.DataFrame(reviews)`` on the scraper's output
  * grouping by month and exporting the review table to CSV

Needs: ``pip install "trustpilot_scraper[pandas]"``. Offline: uses the bundled synthetic pages
(invented company "BrightParcel"); no request reaches Trustpilot. The CSV is written to a
temporary directory.

Run: python examples/monthly_trend_pandas.py
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pandas as pd
from _samples import load_reviews


def main() -> None:
    df = pd.DataFrame(load_reviews("brightparcel"))
    df["Date"] = pd.to_datetime(df["Date"])
    df["Month"] = df["Date"].dt.to_period("M")

    monthly = df.groupby("Month").agg(
        reviews=("Rating", "size"),
        avg_rating=("Rating", "mean"),
        negative_share=("Rating", lambda s: (s <= 2).mean()),
    )
    print(monthly.round(2).to_string())

    by_country = df.groupby("Location")["Rating"].agg(["size", "mean"]).sort_values("size")
    print("\nBy reviewer country\n" + by_country.round(2).to_string())

    out = Path(tempfile.mkdtemp()) / "brightparcel_reviews.csv"
    df.drop(columns=["Month"]).to_csv(out, index=False)
    print(f"\nwrote {len(df)} rows to {out}")


if __name__ == "__main__":
    main()
