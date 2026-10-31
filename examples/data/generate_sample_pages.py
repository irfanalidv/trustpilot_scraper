"""Regenerate the synthetic sample pages in this folder.

The pages copy the structure of Trustpilot's embedded ``__NEXT_DATA__`` JSON (as checked
against a live page on 2026-10-31) but every company, reviewer and review is invented.
The output is deterministic, so re-running this script reproduces the committed files.

Run: python examples/data/generate_sample_pages.py
"""

from __future__ import annotations

import json
import random
from datetime import datetime, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
PER_PAGE = 8

THEMES = {
    5: [
        ("Arrived a day early", "Parcel arrived a day early and the tracking was spot on."),
        ("Great support", "Support answered in minutes and sorted my address change."),
        ("Smooth refund", "Refund landed in my account two days after I sent it back."),
    ],
    4: [
        ("Good overall", "Good service overall, the app could show clearer delivery slots."),
        ("Fast but noisy updates", "Fast delivery, though I got five text messages about it."),
    ],
    3: [
        ("Average", "Delivery was fine but the box was damaged on one corner."),
        ("Okay", "Okay experience, the courier left it with a neighbour without asking."),
    ],
    2: [
        ("Late delivery", "Late delivery again, three days after the promised date."),
        ("Slow refund", "Still waiting for my refund after two weeks and several emails."),
    ],
    1: [
        ("Lost parcel", "Parcel marked delivered but never arrived. Lost parcel, no answer."),
        ("Rude customer service", "Customer service was rude and closed my chat twice."),
        ("Damaged item", "Item arrived damaged and the refund form keeps failing."),
    ],
}

COMPANIES = {
    "brightparcel": {"name": "BrightParcel", "pages": 3, "weights": [6, 2, 2, 4, 9], "reply": 0.6},
    "swiftcart": {"name": "SwiftCart", "pages": 2, "weights": [2, 2, 2, 5, 7], "reply": 0.3},
}
COUNTRIES = ["GB", "US", "DE", "FR", "IE", "NL"]


def make_review(
    rng: random.Random, slug: str, idx: int, rating: int, when: datetime, reply_rate: float
) -> dict:
    title, text = rng.choice(THEMES[rating])
    reply = None
    if rng.random() < reply_rate:
        reply_at = when + timedelta(hours=rng.randint(2, 96))
        reply = {
            "id": f"{slug}-reply-{idx}",
            "message": "Thanks for the feedback. We have passed this on to the team.",
            "publishedDate": reply_at.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "updatedDate": None,
        }
    verified = rng.random() < 0.7
    return {
        "id": f"{slug}-{idx:04d}",
        "filtered": False,
        "isPending": False,
        "text": text,
        "rating": rating,
        "labels": {
            "merged": None,
            "verification": {
                "isVerified": verified,
                "createdDateTime": when.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                "reviewSourceName": "Organic",
                "verificationSource": "invitation",
                "verificationLevel": "verified" if verified else "not-verified",
                "hasDachExclusion": False,
            },
        },
        "title": title,
        "likes": rng.randint(0, 6),
        "source": "Organic",
        "dates": {
            "experiencedDate": (when - timedelta(days=rng.randint(0, 5))).strftime(
                "%Y-%m-%dT00:00:00.000Z"
            ),
            "publishedDate": when.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "updatedDate": None,
            "submittedDate": None,
        },
        "consumer": {
            "id": f"{slug}-c{idx}",
            "displayName": f"Sample Reviewer {idx}",
            "imageUrl": "",
            "numberOfReviews": rng.randint(1, 12),
            "countryCode": rng.choice(COUNTRIES),
            "hasImage": False,
            "isVerified": False,
        },
        "reply": reply,
        "language": "en",
        "location": None,
    }


def main() -> None:
    for slug, spec in COMPANIES.items():
        rng = random.Random(slug)
        total = spec["pages"] * PER_PAGE
        start = datetime(2026, 10, 30, 18, 0)
        reviews = []
        for idx in range(1, total + 1):
            rating = rng.choices([1, 2, 3, 4, 5], weights=spec["weights"])[0]
            when = start - timedelta(hours=idx * rng.randint(20, 70))
            reviews.append(make_review(rng, slug, idx, rating, when, spec["reply"]))
        for page in range(1, spec["pages"] + 1):
            chunk = reviews[(page - 1) * PER_PAGE : page * PER_PAGE]
            data = {
                "props": {
                    "pageProps": {
                        "pageUrl": f"https://www.trustpilot.com/review/{slug}.example",
                        "businessUnit": {
                            "displayName": spec["name"],
                            "identifyingName": f"{slug}.example",
                            "numberOfReviews": total,
                        },
                        "reviews": chunk,
                        "filters": {
                            "pagination": {
                                "currentPage": page,
                                "perPage": PER_PAGE,
                                "totalCount": total,
                                "totalPages": spec["pages"],
                            }
                        },
                    }
                },
                "page": "/review/[businessUnit]",
                "query": {"businessUnit": f"{slug}.example", "page": str(page)},
            }
            html = (
                '<!DOCTYPE html><html lang="en"><head><title>'
                f"{spec['name']} Reviews (synthetic sample)</title></head><body>"
                '<div id="__next"></div><script id="__NEXT_DATA__" type="application/json">'
                f"{json.dumps(data)}</script></body></html>\n"
            )
            (HERE / f"{slug}_page{page}.html").write_text(html, encoding="utf-8")
            print(f"wrote {slug}_page{page}.html ({len(chunk)} reviews)")


if __name__ == "__main__":
    main()
