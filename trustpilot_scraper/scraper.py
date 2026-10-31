"""Scrape public Trustpilot reviews from a company's review page.

Trustpilot renders its review pages with Next.js and embeds the page data as JSON
in a ``<script id="__NEXT_DATA__">`` tag. This module reads that JSON rather than
scraping the visual markup, which is far more stable across redesigns.
"""

from __future__ import annotations

import json
import logging
import re
import time
from collections.abc import Iterator, Mapping
from typing import Any
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

__all__ = [
    "DEFAULT_HEADERS",
    "TrustpilotBlockedError",
    "TrustpilotError",
    "TrustpilotParseError",
    "get_reviews_from_page",
    "iter_trustpilot_reviews",
    "normalize_review",
    "normalize_url",
    "parse_next_data",
    "parse_reviews_html",
    "scrape_trustpilot_reviews",
]

DEFAULT_HEADERS: dict[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; trustpilot-scraper; "
        "+https://github.com/irfanalidv/trustpilot_scraper)"
    ),
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
}

_CHALLENGE_MARKERS = ("Verifying Connection", "awswaf.com", "challenge.js")

# "trustpilot" followed by a short public suffix: trustpilot.com, uk.trustpilot.com,
# trustpilot.co.uk. Rejects look-alikes such as nottrustpilot.com or trustpilot.example.org.
_TRUSTPILOT_HOST = re.compile(r"^(?:[a-z0-9-]+\.)*trustpilot(?:\.[a-z]{2,3}){1,2}$")

logger = logging.getLogger(__name__)


class TrustpilotError(RuntimeError):
    """Base class for all errors raised by this package."""


class TrustpilotBlockedError(TrustpilotError):
    """Trustpilot refused the request (HTTP 403/429 or a bot-verification page).

    Attributes:
        status_code: The HTTP status, or ``None`` for a verification page served with 200.
        retry_after: Seconds from a numeric ``Retry-After`` header, if Trustpilot sent one.
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        retry_after: float | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.retry_after = retry_after


class TrustpilotParseError(TrustpilotError):
    """The page was fetched but its review data could not be found or decoded."""


def normalize_url(company: str) -> str:
    """Turn a domain (``"www.amazon.com"``) or review URL into a clean review-page URL.

    Query strings and fragments are dropped so pagination can be appended safely.
    """
    company = company.strip()
    if not company:
        raise ValueError("company must be a non-empty domain or Trustpilot URL")
    if "://" not in company:
        if company.startswith(("trustpilot.com/", "www.trustpilot.com/")):
            company = "https://" + company
        else:
            return f"https://www.trustpilot.com/review/{company.strip('/')}"
    parsed = urlparse(company)
    host = (parsed.hostname or "").lower()
    if parsed.scheme not in ("http", "https") or not _TRUSTPILOT_HOST.match(host):
        raise ValueError(f"not a Trustpilot URL: {company!r}")
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path.rstrip('/')}"


def parse_next_data(html: str) -> dict[str, Any]:
    """Return the decoded ``__NEXT_DATA__`` JSON object embedded in a Trustpilot page.

    Raises:
        TrustpilotBlockedError: the HTML is a bot-verification interstitial.
        TrustpilotParseError: the script tag is missing or is not valid JSON.
    """
    soup = BeautifulSoup(html, "html.parser")
    tag = soup.find("script", id="__NEXT_DATA__")
    if tag is None or not tag.string:
        if any(marker in html for marker in _CHALLENGE_MARKERS):
            raise TrustpilotBlockedError(
                "Trustpilot returned a bot-verification page instead of reviews. "
                "Plain HTTP clients are currently being challenged; see the README "
                "for options (e.g. parse HTML you saved from a browser)."
            )
        raise TrustpilotParseError("no __NEXT_DATA__ script found in the page")
    try:
        data = json.loads(tag.string)
    except json.JSONDecodeError as exc:
        raise TrustpilotParseError(f"__NEXT_DATA__ is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise TrustpilotParseError("__NEXT_DATA__ JSON is not an object")
    return data


def _page_props(data: dict[str, Any]) -> dict[str, Any]:
    try:
        props = data["props"]["pageProps"]
    except (KeyError, TypeError) as exc:
        raise TrustpilotParseError("__NEXT_DATA__ has no props.pageProps") from exc
    if not isinstance(props, dict):
        raise TrustpilotParseError("props.pageProps is not an object")
    return props


def parse_reviews_html(html: str) -> list[dict[str, Any]]:
    """Return the raw review objects from a Trustpilot review-page HTML string.

    Useful when you fetched the page yourself (for example saved from a browser).
    """
    reviews = _page_props(parse_next_data(html)).get("reviews")
    if reviews is None:
        raise TrustpilotParseError("props.pageProps has no 'reviews' list")
    if not isinstance(reviews, list):
        raise TrustpilotParseError("props.pageProps.reviews is not a list")
    return reviews


def _total_pages(html_data: dict[str, Any]) -> int | None:
    try:
        total = _page_props(html_data)["filters"]["pagination"]["totalPages"]
    except (KeyError, TypeError, TrustpilotParseError):
        return None
    return total if isinstance(total, int) else None


def _request_headers(session: requests.Session | None) -> dict[str, str]:
    """Default headers, minus any the caller deliberately set on their ``session``.

    ``requests`` gives every session a ``python-requests`` User-Agent and ``Accept: */*``;
    those generic values are replaced, but a header you changed yourself is left alone.
    """
    headers = dict(DEFAULT_HEADERS)
    session_headers = getattr(session, "headers", None)
    if not isinstance(session_headers, Mapping):
        return headers
    generic = requests.utils.default_headers()
    customised = {
        name.lower() for name, value in session_headers.items() if value != generic.get(name)
    }
    return {name: value for name, value in headers.items() if name.lower() not in customised}


def _retry_after(resp: Any) -> float | None:
    value = (getattr(resp, "headers", None) or {}).get("Retry-After")
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None  # HTTP-date form; not parsed


def _fetch(url: str, session: requests.Session | None, timeout: float) -> str:
    getter = session.get if session is not None else requests.get
    logger.debug("GET %s", url)
    try:
        resp = getter(url, headers=_request_headers(session), timeout=timeout)
    except requests.RequestException as exc:
        raise TrustpilotError(f"request to {url} failed: {exc}") from exc
    if resp.status_code in (403, 429):
        raise TrustpilotBlockedError(
            f"Trustpilot blocked the request to {url} (HTTP {resp.status_code}). "
            "It may be rate-limiting or showing a bot-verification page.",
            status_code=resp.status_code,
            retry_after=_retry_after(resp),
        )
    if resp.status_code == 404:
        raise TrustpilotError(f"page not found: {url}")
    try:
        resp.raise_for_status()
    except requests.HTTPError as exc:
        raise TrustpilotError(str(exc)) from exc
    return resp.text


def get_reviews_from_page(
    url: str,
    *,
    session: requests.Session | None = None,
    timeout: float = 30.0,
) -> list[dict[str, Any]]:
    """Fetch one Trustpilot review page and return its raw review objects.

    Unlike versions before 1.0, errors are raised instead of returning ``[]``.
    """
    return parse_reviews_html(_fetch(url, session, timeout))


def _date(value: Any) -> str | None:
    if isinstance(value, str) and len(value) >= 10:
        return value[:10]
    return None


def normalize_review(review: dict[str, Any], *, extended: bool = False) -> dict[str, Any]:
    """Map a raw Trustpilot review object to the flat dict returned by the scraper.

    The default keys are ``Date``, ``Author``, ``Body``, ``Heading``, ``Rating`` and
    ``Location`` (unchanged since 0.x). With ``extended=True`` these are added:
    ``ReviewId``, ``ExperienceDate``, ``Verified``, ``Likes``, ``Language``,
    ``Reply`` and ``ReplyDate``.
    """
    dates = review.get("dates") or {}
    consumer = review.get("consumer") or {}
    row: dict[str, Any] = {
        "Date": _date(dates.get("publishedDate")),
        "Author": consumer.get("displayName"),
        "Body": review.get("text"),
        "Heading": review.get("title"),
        "Rating": review.get("rating"),
        "Location": consumer.get("countryCode"),
    }
    if extended:
        verification = (review.get("labels") or {}).get("verification") or {}
        reply = review.get("reply") or {}
        row.update(
            {
                "ReviewId": review.get("id"),
                "ExperienceDate": _date(dates.get("experiencedDate")),
                "Verified": verification.get("isVerified"),
                "Likes": review.get("likes"),
                "Language": review.get("language"),
                "Reply": reply.get("message"),
                "ReplyDate": _date(reply.get("publishedDate")),
            }
        )
    return row


def iter_trustpilot_reviews(
    base_url: str,
    *,
    max_pages: int | None = None,
    delay: float = 2.0,
    extended: bool = False,
    session: requests.Session | None = None,
    timeout: float = 30.0,
) -> Iterator[dict[str, Any]]:
    """Yield normalized reviews page by page, stopping at the last page.

    Args:
        base_url: Trustpilot review URL or bare company domain.
        max_pages: Stop after this many pages (``None`` means every page).
        delay: Seconds to sleep between page requests. Please keep this polite.
        extended: Include extra fields (see :func:`normalize_review`).
        session: Optional ``requests.Session`` (to reuse connections or set
            your own headers/cookies/proxies).
        timeout: Per-request timeout in seconds.

    Raises:
        TrustpilotBlockedError: if Trustpilot challenges or blocks the request.
        TrustpilotError: on other HTTP failures or unparseable pages.
    """
    if max_pages is not None and max_pages < 1:
        raise ValueError("max_pages must be >= 1 or None")
    url = normalize_url(base_url)
    seen: set[str] = set()
    page = 1
    total: int | None = None
    while True:
        html = _fetch(f"{url}?page={page}", session, timeout)
        data = parse_next_data(html)
        if total is None:
            total = _total_pages(data)
        reviews = _page_props(data).get("reviews") or []
        logger.debug("page %d: %d reviews (total pages: %s)", page, len(reviews), total)
        if not reviews:
            return
        for review in reviews:
            key = review.get("id") or json.dumps(review, sort_keys=True, default=str)
            if key in seen:
                continue
            seen.add(key)
            yield normalize_review(review, extended=extended)
        if (max_pages is not None and page >= max_pages) or (total is not None and page >= total):
            return
        page += 1
        if delay > 0:
            time.sleep(delay)


def scrape_trustpilot_reviews(
    base_url: str,
    *,
    max_pages: int | None = None,
    delay: float = 2.0,
    extended: bool = False,
    session: requests.Session | None = None,
    timeout: float = 30.0,
) -> list[dict[str, Any]]:
    """Scrape reviews from a Trustpilot company page and return them as a list of dicts.

    See :func:`iter_trustpilot_reviews` for the arguments. Reviews are returned in
    page order (newest first by default) and de-duplicated by review id.
    """
    return list(
        iter_trustpilot_reviews(
            base_url,
            max_pages=max_pages,
            delay=delay,
            extended=extended,
            session=session,
            timeout=timeout,
        )
    )
