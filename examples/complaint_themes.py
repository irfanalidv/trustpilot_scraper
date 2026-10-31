"""Customer-feedback triage: rating distribution, reply coverage and complaint themes.

A support lead saved a company's Trustpilot pages from the browser and wants a quick
summary: how ratings are spread, how many reviews got a reply, and what the 1-2 star
reviews complain about.

Shows:
  * ``parse_reviews_html`` + ``normalize_review(extended=True)`` on HTML you already have
  * working with the plain dicts (no pandas needed)

Needs: ``pip install trustpilot_scraper``. Offline: uses the bundled synthetic pages in
``examples/data/`` (invented company "BrightParcel"), so no request reaches Trustpilot.

Run: python examples/complaint_themes.py
"""

from __future__ import annotations

from collections import Counter

from _samples import load_reviews

THEMES = {
    "late delivery": ("late", "promised date"),
    "lost parcel": ("lost", "never arrived"),
    "refunds": ("refund",),
    "damaged items": ("damaged",),
    "customer service": ("customer service", "rude", "chat"),
}


def main() -> None:
    reviews = load_reviews("brightparcel")
    print(f"{len(reviews)} reviews\n")

    print("Rating distribution")
    counts = Counter(r["Rating"] for r in reviews)
    for stars in range(5, 0, -1):
        n = counts.get(stars, 0)
        print(f"  {stars}*  {'#' * n:<12} {n:>2}  ({n / len(reviews):.0%})")

    replied = [r for r in reviews if r["Reply"]]
    share = len(replied) / len(reviews)
    print(f"\nCompany replied to {len(replied)}/{len(reviews)} reviews ({share:.0%})")
    negative = [r for r in reviews if r["Rating"] <= 2]
    unanswered = [r for r in negative if not r["Reply"]]
    print(f"Negative reviews without a reply: {len(unanswered)}/{len(negative)}")

    print("\nThemes in 1-2 star reviews")
    themes: Counter[str] = Counter()
    for review in negative:
        text = f"{review['Heading']} {review['Body']}".lower()
        for theme, keywords in THEMES.items():
            if any(k in text for k in keywords):
                themes[theme] += 1
    for theme, n in themes.most_common():
        print(f"  {theme:<18} {n}")

    if unanswered:
        oldest = min(unanswered, key=lambda r: r["Date"])
        print(f"\nOldest unanswered complaint: {oldest['Date']} {oldest['Heading']!r}")


if __name__ == "__main__":
    main()
