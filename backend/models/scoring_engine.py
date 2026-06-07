from __future__ import annotations

import logging

from data.market_data import fetch_ohlcv, latest_price
from data.news_ingestor import fetch_news
from data.polymarket import polymarket_market_sentiment
from data.technical import latest_indicator_snapshot
from models.sentiment_engine import analyze_sentiment, get_average_score, get_signal

logger = logging.getLogger(__name__)


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def map_sentiment_score(raw_score: float) -> float:
    return _clamp((raw_score + 1.0) / 2.0)


def map_rsi_score(rsi_value: float | None) -> float | None:
    if rsi_value is None:
        return None
    centered = (50.0 - float(rsi_value)) / 50.0
    return _clamp(0.5 + centered * 0.5)


def map_macd_score(macd_value: float | None, macd_signal_value: float | None) -> float | None:
    if macd_value is None:
        return None
    spread = float(macd_value) if macd_signal_value is None else float(macd_value) - float(macd_signal_value)
    return _clamp(0.5 + (spread / (abs(spread) + 1.0)) * 0.5)


def map_sma_score(price_value: float | None, sma_21: float | None, sma_50: float | None) -> float | None:
    if price_value is None or sma_21 is None or sma_50 is None:
        return None

    bullish = 0
    bearish = 0

    if price_value >= sma_21:
        bullish += 1
    else:
        bearish += 1

    if price_value >= sma_50:
        bullish += 1
    else:
        bearish += 1

    if sma_21 >= sma_50:
        bullish += 1
    else:
        bearish += 1

    total = bullish + bearish
    if total == 0:
        return None
    return round(bullish / total, 4)


def technical_score(price_info: dict, snap: dict) -> tuple[float | None, list[str]]:
    parts: list[tuple[str, float]] = []
    reasons: list[str] = []

    rsi_value = snap.get("rsi")
    rsi_component = map_rsi_score(rsi_value)
    if rsi_component is not None:
        parts.append(("RSI", rsi_component))
        reasons.append(f"RSI {rsi_value:.1f} -> {rsi_component:.2f}")

    macd_value = snap.get("macd")
    macd_signal_value = snap.get("macd_signal")
    macd_component = map_macd_score(macd_value, macd_signal_value)
    if macd_component is not None:
        parts.append(("MACD", macd_component))
        reasons.append(f"MACD spread -> {macd_component:.2f}")

    sma_component = map_sma_score(
        price_info.get("price"),
        snap.get("sma_21"),
        snap.get("sma_50"),
    )
    if sma_component is not None:
        parts.append(("Trend", sma_component))
        reasons.append(f"Price vs SMA trend -> {sma_component:.2f}")

    if not parts:
        return None, []

    score = round(sum(value for _, value in parts) / len(parts), 4)
    return score, reasons


def score_to_signal(score: float | None) -> str | None:
    if score is None:
        return None
    if score >= 0.75:
        return "STRONG BUY"
    if score >= 0.60:
        return "BUY"
    if score <= 0.25:
        return "STRONG SELL"
    if score <= 0.40:
        return "SELL"
    return "HOLD"


def build_signal_payload(ticker: str) -> dict:
    result: dict = {
        "ticker": ticker.upper(),
        "technical_score": None,
        "technical_signal": None,
        "news_score": None,
        "news_signal": None,
        "polymarket_score": None,
        "polymarket_label": None,
        "final_score": 0.5,
        "final_signal": "HOLD",
        "confidence": 0.0,
        "reasons": [],
        "sources": [],
    }

    reasons: list[str] = []
    components: dict[str, float | None] = {
        "news": None,
        "polymarket": None,
        "technicals": None,
    }
    source_candidates: list[dict] = []

    try:
        price_info = latest_price(ticker)
        df = fetch_ohlcv(ticker, period_days=90)
        snap = latest_indicator_snapshot(df)
        tech_score, tech_details = technical_score(price_info, snap)

        result["technical_score"] = tech_score
        result["technical_signal"] = score_to_signal(tech_score)
        components["technicals"] = tech_score

        if tech_score is not None:
            reasons.append(f"Technical composite={tech_score:.2f} -> {result['technical_signal']}")
            reasons.extend(tech_details[:2])
    except Exception as exc:
        logger.warning("Signal technicals failed for %s: %s", ticker, exc)

    try:
        news_list = fetch_news(ticker, limit=10)
        analyzed_news = analyze_sentiment(news_list) if news_list else []
        avg_score = get_average_score(analyzed_news)
        news_sig = get_signal(avg_score)
        news_score = map_sentiment_score(avg_score)

        result["news_score"] = round(news_score, 4)
        result["news_signal"] = news_sig
        components["news"] = news_score if analyzed_news else None

        if analyzed_news:
            reasons.append(f"News sentiment={avg_score:.2f} normalized={news_score:.2f} -> {news_sig}")
            for article in analyzed_news[:3]:
                source_candidates.append({
                    "title": article.get("title", "News article"),
                    "source": article.get("source", "yahoo"),
                    "url": article.get("url", ""),
                })
    except Exception as exc:
        logger.warning("Signal news failed for %s: %s", ticker, exc)

    try:
        poly = polymarket_market_sentiment(ticker)
        result["polymarket_score"] = poly["score"]
        result["polymarket_label"] = poly["label"]
        components["polymarket"] = poly.get("score")
        if poly.get("score") is not None:
            reasons.append(f"Polymarket={poly['score']:.2f} -> {poly['label']}")
    except Exception as exc:
        logger.warning("Signal polymarket failed for %s: %s", ticker, exc)

    weights = {
        "news": 0.30,
        "polymarket": 0.45,
        "technicals": 0.25,
    }

    available = {name: score for name, score in components.items() if score is not None}
    if available:
        total_weight = sum(weights[name] for name in available)
        final_score = sum(available[name] * weights[name] for name in available) / total_weight
        result["final_score"] = round(final_score, 4)
        result["final_signal"] = score_to_signal(final_score) or "HOLD"
        distance = abs(final_score - 0.5) * 2.0
        support = min(1.0, total_weight)
        result["confidence"] = round(min(1.0, distance * 0.7 + support * 0.3), 3)

    breakdown = {}
    for name, score in components.items():
        if score is not None:
            breakdown[name] = {
                "raw_score": round(score, 4),
                "weight": weights[name],
                "weighted_contribution": round(score * weights[name], 4),
            }
    result["breakdown"] = breakdown

    deduped_sources: list[dict] = []
    seen_urls: set[str] = set()
    for item in source_candidates:
        url = item.get("url", "")
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)
        deduped_sources.append(item)
        if len(deduped_sources) >= 5:
            break

    result["sources"] = deduped_sources
    result["reasons"] = reasons
    return result
