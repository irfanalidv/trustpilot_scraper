"""Live scrape with polite settings and an honest fallback when Trustpilot blocks you.

Shows:
  * ``scrape_trustpilot_reviews`` against the real site (``max_pages``, ``delay``, ``timeout``)
  * catching ``TrustpilotBlockedError`` and respecting ``retry_after`` instead of hammering
  * the fallback the README recommends: save the page in your browser, then parse it

Needs: ``pip install trustpilot_scraper`` and NETWORK ACCESS. Trustpilot currently puts a
bot-verification page in front of many review pages, so expect the blocked branch. The script
makes at most one request per page, two seconds apart, and never tries to bypass the check.
Not run by the test suite.

Run: python examples/live_scrape.py [company-domain]
"""

from __future__ import annotations

import sys

from trustpilot_scraper import TrustpilotBlockedError, TrustpilotError, scrape_trustpilot_reviews


def main(company: str) -> int:
    try:
        reviews = scrape_trustpilot_reviews(company, max_pages=2, delay=2.0, timeout=20)
    except TrustpilotBlockedError as exc:
        wait = f" Trustpilot asked to wait {exc.retry_after:.0f}s." if exc.retry_after else ""
        print(f"Blocked (HTTP {exc.status_code}).{wait}")
        print(
            "Fallback: open the review page in your browser, save it as HTML, then run\n"
            "  parse_reviews_html(Path('page.html').read_text())"
        )
        return 0
    except TrustpilotError as exc:
        print(f"Request failed: {exc}")
        return 1
    print(f"{len(reviews)} reviews; first: {reviews[0] if reviews else None}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "www.amazon.com"))
