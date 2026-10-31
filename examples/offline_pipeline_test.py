"""Exercise the full scraping loop offline by plugging a fake transport into a Session.

When you build a pipeline on top of ``scrape_trustpilot_reviews`` you want to test the real
pagination, de-duplication and error handling without sending traffic to Trustpilot. The
``session=`` argument accepts any ``requests.Session``, so a transport adapter can serve
saved pages instead of the network.

Shows:
  * ``iter_trustpilot_reviews`` with ``session=``, ``max_pages`` and ``delay``
  * pagination stopping at the page count embedded in the page
  * ``TrustpilotBlockedError`` (with ``status_code``) for an HTTP 403

Needs: ``pip install trustpilot_scraper``. Offline: the adapter answers from
``examples/data/``; no request leaves the machine.

Run: python examples/offline_pipeline_test.py
"""

from __future__ import annotations

from urllib.parse import parse_qs, urlparse

import requests
from _samples import sample_pages
from requests.adapters import BaseAdapter

from trustpilot_scraper import TrustpilotBlockedError, iter_trustpilot_reviews


class SavedPagesAdapter(BaseAdapter):
    """Answer ``/review/<company>?page=N`` from the bundled sample pages."""

    def __init__(self, blocked: bool = False) -> None:
        super().__init__()
        self.blocked = blocked
        self.requested: list[str] = []

    def send(self, request: requests.PreparedRequest, **kwargs: object) -> requests.Response:
        url = request.url or ""
        self.requested.append(url)
        parsed = urlparse(url)
        company = parsed.path.rsplit("/", 1)[-1].split(".")[0]
        page = int(parse_qs(parsed.query).get("page", ["1"])[0])
        pages = sample_pages(company)

        response = requests.Response()
        response.url = url
        response.request = request
        if self.blocked:
            response.status_code = 403
        elif page <= len(pages):
            response.status_code = 200
            response._content = pages[page - 1].read_bytes()
            response.encoding = "utf-8"
        else:
            response.status_code = 404
        return response

    def close(self) -> None:
        pass


def main() -> None:
    adapter = SavedPagesAdapter()
    with requests.Session() as session:
        session.mount("https://", adapter)
        reviews = list(iter_trustpilot_reviews("brightparcel.example", session=session, delay=0))
        print(f"collected {len(reviews)} reviews from {len(adapter.requested)} pages:")
        for url in adapter.requested:
            print("  GET", url)

        first_two = list(
            iter_trustpilot_reviews("brightparcel.example", session=session, max_pages=2, delay=0)
        )
        print(f"max_pages=2 -> {len(first_two)} reviews")

        session.mount("https://", SavedPagesAdapter(blocked=True))
        try:
            next(iter_trustpilot_reviews("brightparcel.example", session=session))
        except TrustpilotBlockedError as exc:
            print(f"blocked as expected: HTTP {exc.status_code}")


if __name__ == "__main__":
    main()
