import json
import logging
import re
from typing import Iterable
from urllib.parse import quote_plus, urljoin

import requests
from bs4 import BeautifulSoup

from data.news_ingestor import resolve_stock

logger = logging.getLogger(__name__)

URL_RE = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
WHITESPACE_RE = re.compile(r"\s+")
SPAM_PATTERNS = (
    re.compile(r"\b(join|follow|subscribe|dm|telegram|whatsapp)\b", re.IGNORECASE),
    re.compile(r"\b(?:100|1000)x\b", re.IGNORECASE),
    re.compile(r"\b(?:pump|moon|airdrop|giveaway)\b", re.IGNORECASE),
)
MIN_TEXT_LENGTH = 25
MIN_TEXT_LENGTH_BY_SOURCE = {
    "stocktwits": 15,
}
REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}
REDDIT_BASE_URL = "https://www.reddit.com"
OLD_REDDIT_BASE_URL = "https://old.reddit.com"
STOCKTWITS_API_URL = "https://api.stocktwits.com/api/2/streams/symbol/{ticker}.json"


def _clean_text(text: str) -> str:
    cleaned = URL_RE.sub("", text or "")
    cleaned = WHITESPACE_RE.sub(" ", cleaned).strip()
    return cleaned


def _is_spam_like(text: str) -> bool:
    lowered = (text or "").lower()
    if not lowered:
        return True
    if any(pattern.search(lowered) for pattern in SPAM_PATTERNS):
        return True
    if lowered.count("$") > 5 or lowered.count("#") > 8:
        return True
    return False


def _normalize_item(
    source: str,
    text: str,
    url: str,
    created_at,
    engagement: int | None = None,
):
    cleaned = _clean_text(text)
    min_length = MIN_TEXT_LENGTH_BY_SOURCE.get(source, MIN_TEXT_LENGTH)
    if len(cleaned) < min_length or _is_spam_like(cleaned):
        return None

    item = {
        "source": source,
        "text": cleaned,
        "url": url or "",
        "created_at": created_at.isoformat() if hasattr(created_at, "isoformat") else (str(created_at) if created_at else None),
    }
    if engagement is not None:
        item["engagement"] = engagement
    return item


def _dedupe(items: Iterable[dict], limit: int) -> list[dict]:
    seen: set[tuple[str, str]] = set()
    results: list[dict] = []

    for item in items:
        key = (item.get("source", ""), item.get("url", "") or item.get("text", ""))
        if key in seen:
            continue
        seen.add(key)
        results.append(item)
        if len(results) >= limit:
            break

    return results


def _reddit_queries(ticker: str, company_name: str) -> list[str]:
    queries = [ticker]
    if company_name.lower() != ticker.lower():
        queries.append(company_name)
    return queries


def _extract_reddit_candidates_from_html(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    candidates: list[dict] = []

    for anchor in soup.select("a[href*='/comments/']"):
        href = anchor.get("href", "")
        title = anchor.get_text(" ", strip=True)
        if not href or not title:
            continue

        url = urljoin(REDDIT_BASE_URL, href)
        container = anchor.find_parent()
        subreddit = None
        if container is not None:
            subreddit_anchor = container.find("a", href=re.compile(r"^/r/[^/]+/?$"))
            if subreddit_anchor:
                subreddit = subreddit_anchor.get_text(" ", strip=True)

        text = title
        candidates.append({
            "text": text,
            "url": url,
        })

    return candidates


def _extract_old_reddit_candidates(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    candidates: list[dict] = []

    for result in soup.select("div.search-result"):
        title_anchor = result.select_one("a.search-title")
        subreddit_anchor = result.select_one("a.search-subreddit-link")
        if title_anchor is None:
            continue

        href = title_anchor.get("href", "")
        title = title_anchor.get_text(" ", strip=True)
        subreddit = subreddit_anchor.get_text(" ", strip=True) if subreddit_anchor else None

        if not href or not title or "/comments/" not in href:
            continue

        url = href.replace("https://old.reddit.com", REDDIT_BASE_URL)
        text = title
        candidates.append({
            "text": text,
            "url": url,
        })

    return candidates


def _extract_reddit_candidates_from_json(html: str) -> list[dict]:
    candidates: list[dict] = []

    for match in re.finditer(r'<script id="data">(\{.*?\})</script>', html, flags=re.DOTALL):
        try:
            payload = json.loads(match.group(1))
        except json.JSONDecodeError:
            continue

        stack = [payload]
        while stack:
            node = stack.pop()
            if isinstance(node, dict):
                permalink = node.get("permalink") or node.get("url")
                title = node.get("title")
                subreddit = node.get("subredditName") or node.get("subreddit")
                if permalink and title and "/comments/" in permalink:
                    url = urljoin(REDDIT_BASE_URL, permalink)
                    text = title
                    candidates.append({
                        "text": text,
                        "url": url,
                    })
                stack.extend(node.values())
            elif isinstance(node, list):
                stack.extend(node)

    return candidates


def fetch_reddit_posts(ticker: str, company_name: str, limit: int = 20) -> list[dict]:
    items: list[dict] = []

    for query in _reddit_queries(ticker, company_name):
        url = f"{REDDIT_BASE_URL}/search/?q={quote_plus(query)}"
        try:
            response = requests.get(url, headers=REQUEST_HEADERS, timeout=20)
            html = response.text

            raw_candidates = _extract_reddit_candidates_from_html(html)
            if not raw_candidates:
                raw_candidates = _extract_reddit_candidates_from_json(html)
            if not raw_candidates:
                old_headers = {"User-Agent": "stockpulse-bot/1.0 by local-dev"}
                old_url = f"{OLD_REDDIT_BASE_URL}/search?q={quote_plus(query)}"
                old_response = requests.get(old_url, headers=old_headers, timeout=20)
                old_response.raise_for_status()
                raw_candidates = _extract_old_reddit_candidates(old_response.text)

            for candidate in raw_candidates:
                normalized = _normalize_item(
                    source="reddit",
                    text=candidate["text"],
                    url=candidate["url"],
                    created_at=None,
                )
                if normalized:
                    items.append(normalized)
        except Exception as exc:
            logger.warning("Reddit scrape failed for '%s': %s", query, exc)
            continue

    return _dedupe(items, limit)


def fetch_stocktwits_posts(ticker: str, limit: int = 20) -> list[dict]:
    url = STOCKTWITS_API_URL.format(ticker=ticker.upper())
    items: list[dict] = []

    try:
        response = requests.get(url, headers=REQUEST_HEADERS, timeout=20)
        response.raise_for_status()
        payload = response.json()
    except Exception as exc:
        logger.warning("StockTwits fetch failed for '%s': %s", ticker, exc)
        return []

    messages = payload.get("messages", [])
    for message in messages:
        text = message.get("body", "")
        message_id = message.get("id")
        normalized_text = _clean_text(text)
        text_upper = normalized_text.upper()
        ticker_upper = ticker.upper()
        if ticker_upper not in text_upper and f"${ticker_upper}" not in text_upper:
            continue
        url = (
            f"https://stocktwits.com/symbol/{ticker_upper}?message_id={message_id}"
            if message_id
            else f"https://stocktwits.com/symbol/{ticker_upper}"
        )
        normalized = _normalize_item(
            source="stocktwits",
            text=normalized_text,
            url=url,
            created_at=message.get("created_at"),
            engagement=message.get("likes", {}).get("total"),
        )
        if normalized:
            items.append(normalized)

    return _dedupe(items, limit)


def fetch_social_posts(ticker: str, limit_per_source: int = 20) -> list[dict]:
    stock = resolve_stock(ticker)
    symbol = stock["symbol"]
    company_name = stock.get("company_name") or symbol

    reddit_items = fetch_reddit_posts(symbol, company_name, limit=limit_per_source)
    stocktwits_items = fetch_stocktwits_posts(symbol, limit=limit_per_source)
    return reddit_items + stocktwits_items


if __name__ == "__main__":
    symbol = input("Enter stock ticker or company: ").strip()
    for item in fetch_social_posts(symbol):
        print(item)
