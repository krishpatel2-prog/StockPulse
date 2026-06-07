import json
import re
from urllib.parse import urlencode
from urllib.request import Request, urlopen

# 🔥 Mapping ticker → company name
TICKER_TO_NAME = {
    "NVDA": "nvidia",
    "TSLA": "tesla",
    "AAPL": "apple",
    "MSFT": "microsoft",
    "AMZN": "amazon",
    "GOOGL": "google",
    "META": "meta"
}

# 🔥 Mapping company name → ticker
NAME_TO_TICKER = {
    "nvidia": "NVDA",
    "tesla": "TSLA",
    "amazon": "AMZN",
    "google": "GOOGL",
    "alphabet": "GOOGL",
    "meta": "META",
    "facebook": "META",
    "apple": "AAPL",
    "microsoft": "MSFT"
}

TICKER_KEYWORDS = {
    "NVDA": ["nvidia", "nvda", "chip", "gpu"],
    "TSLA": ["tesla", "tsla", "ev"],
    "AAPL": ["apple", "aapl", "iphone"],
    "MSFT": ["microsoft", "msft", "azure"],
    "AMZN": ["amazon", "amzn"],
    "GOOGL": ["google", "alphabet", "googl"],
    "META": ["meta", "facebook"]
}

YAHOO_SEARCH_URL = "https://query2.finance.yahoo.com/v1/finance/search"
US_EXCHANGES = {"NMS", "NYQ", "ASE", "BTS", "PCX", "NGM", "NCM"}
OTC_EXCHANGES = {"PNK", "OQB", "OEM", "OQX"}
GENERIC_NAME_WORDS = {
    "inc", "incorporated", "corp", "corporation", "group", "holdings", "holding",
    "limited", "ltd", "plc", "company", "co", "ag", "sa", "nv", "se", "spa", "motors"
}


def _fetch_symbol_candidates(query: str, limit: int = 5):
    url = YAHOO_SEARCH_URL + "?" + urlencode({
        "q": query,
        "quotesCount": limit,
        "newsCount": 0
    })
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})

    try:
        with urlopen(request, timeout=15) as response:
            data = json.load(response)
    except Exception:
        return []

    return data.get("quotes", [])


def _normalize_name(value: str):
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def _candidate_score(candidate, query: str):
    normalized_query = _normalize_name(query)
    symbol = (candidate.get("symbol") or "").lower()
    shortname = candidate.get("shortname") or ""
    longname = candidate.get("longname") or ""
    exchange = candidate.get("exchange") or ""
    quote_type = candidate.get("quoteType") or ""

    normalized_short = _normalize_name(shortname)
    normalized_long = _normalize_name(longname)

    score = 0

    if quote_type == "EQUITY":
        score += 100

    if symbol == query.lower():
        score += 90

    if normalized_short == normalized_query or normalized_long == normalized_query:
        score += 80

    if normalized_query and (
        normalized_short.startswith(normalized_query)
        or normalized_long.startswith(normalized_query)
    ):
        score += 50

    if normalized_query and (
        normalized_query in normalized_short
        or normalized_query in normalized_long
    ):
        score += 25

    if exchange in US_EXCHANGES:
        score += 20
    if exchange in OTC_EXCHANGES:
        score -= 40

    return score


def resolve_stock(user_input: str):
    """
    Resolve a user-provided company name or ticker to a Yahoo symbol and keywords.
    """
    cleaned = user_input.strip()
    lowered = cleaned.lower()

    if lowered in NAME_TO_TICKER:
        symbol = NAME_TO_TICKER[lowered]
        return {
            "symbol": symbol,
            "company_name": TICKER_TO_NAME.get(symbol, cleaned),
            "keywords": TICKER_KEYWORDS.get(symbol, [symbol.lower(), lowered]),
            "exchange": None,
            "resolved_from": cleaned
        }

    candidates = _fetch_symbol_candidates(cleaned)
    preferred = max(candidates, key=lambda candidate: _candidate_score(candidate, cleaned), default=None)

    if preferred is None:
        return {
            "symbol": cleaned.upper(),
            "company_name": cleaned,
            "keywords": [cleaned.lower()],
            "exchange": None,
            "resolved_from": cleaned
        }

    symbol = preferred.get("symbol", cleaned.upper())
    company_name = preferred.get("shortname") or preferred.get("longname") or cleaned
    name_parts = [
        part for part in re.findall(r"[A-Za-z]{3,}", company_name.lower())
        if part not in GENERIC_NAME_WORDS
    ]
    keywords = list(dict.fromkeys(TICKER_KEYWORDS.get(symbol, []) + [symbol.lower(), cleaned.lower(), *name_parts]))

    return {
        "symbol": symbol,
        "company_name": company_name,
        "keywords": keywords,
        "exchange": preferred.get("exchange"),
        "resolved_from": cleaned
    }


def normalize_ticker(user_input: str):
    """
    Convert user input (company name or ticker) → proper ticker
    """
    return resolve_stock(user_input)["symbol"]


def fetch_news(ticker: str, limit: int = 10):
    """
    Fetch and filter latest news headlines for a given stock ticker.
    """
    import feedparser

    stock = resolve_stock(ticker)
    ticker = stock["symbol"]

    url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US"

    try:
        feed = feedparser.parse(url)
    except Exception as e:
        print("Error fetching RSS feed:", e)
        return []

    raw_news = []

    # Fetch extra for better filtering
    for entry in feed.entries[:limit * 2]:
        raw_news.append({
            "title": entry.title,
            "source": "yahoo",
            "url": getattr(entry, "link", ""),
            "link": getattr(entry, "link", ""),
            "published": getattr(entry, "published", "N/A")
        })

    # Avoid overfitting on tiny datasets.
    if len(raw_news) < 5:
        return raw_news[:limit]

    filtered_news = filter_news(raw_news, stock)
    return filtered_news[:limit]


def filter_news(news_list, stock):
    if isinstance(stock, str):
        stock = resolve_stock(stock)

    keywords = stock.get("keywords", [stock["symbol"].lower()])

    filtered = []

    for news in news_list:
        title = news["title"].lower()

        if any(keyword in title for keyword in keywords):
            filtered.append(news)

    if not filtered:
        return news_list[:10]

    return filtered


# 🔥 TEST BLOCK
if __name__ == "__main__":
    user_input = input("Enter stock ticker or company: ")
    ticker = normalize_ticker(user_input)

    news = fetch_news(ticker)

    print(f"\nUsing ticker: {ticker}")
    print("\nLatest Headlines:\n")

    if not news:
        print("No news found.")
    else:
        for i, item in enumerate(news, 1):
            print(f"{i}. {item['title']}")
            print(f"   Link: {item['link']}")
            print(f"   Date: {item['published']}\n")
