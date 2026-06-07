"""
main.py - FastAPI
"""

from __future__ import annotations

import logging
import traceback
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from data.market_data import fetch_ohlcv, latest_price, to_records
from data.news_ingestor import fetch_news
from data.polymarket import polymarket_market_sentiment, search_markets
from data.social_ingestor import fetch_social_posts
from data.technical import add_all_indicators, latest_indicator_snapshot, rsi_signal
from models.public_opinion_engine import analyze_public_opinion
from models.scoring_engine import build_signal_payload
from models.sentiment_engine import (
    analyze_sentiment,
    calculate_confidence,
    generate_reason,
    get_average_score,
    get_signal,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Market Prediction API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


def _official_analysis_payload(ticker: str) -> dict:
    news_list = fetch_news(ticker, limit=20)
    analyzed_news = analyze_sentiment(news_list) if news_list else []

    if not analyzed_news:
        return {
            "summary": {
                "signal": "NEUTRAL",
                "score": 0.0,
                "confidence": 0.0,
                "reason": "No recent Yahoo Finance news found.",
            },
            "articles": [],
            "sources": [],
        }

    avg_score = get_average_score(analyzed_news)
    signal = get_signal(avg_score)
    confidence = calculate_confidence(analyzed_news)
    reason = generate_reason(analyzed_news)
    sources = [
        {
            "title": article.get("title", "Yahoo article"),
            "source": article.get("source", "yahoo"),
            "url": article.get("url", ""),
        }
        for article in analyzed_news[:5]
        if article.get("url")
    ]

    return {
        "summary": {
            "signal": signal,
            "score": avg_score,
            "confidence": confidence,
            "reason": reason,
        },
        "articles": analyzed_news,
        "sources": sources,
    }


def _public_opinion_payload(ticker: str) -> dict:
    try:
        posts = fetch_social_posts(ticker, limit_per_source=10)
    except Exception as exc:
        logger.warning("Public opinion fetch failed for %s: %s", ticker, exc)
        posts = []

    return analyze_public_opinion(posts)


@app.get("/")
def root():
    return {
        "app": "Market Prediction Dashboard",
        "status": "running",
        "docs": "http://localhost:8000/docs",
        "endpoints": [
            "/health",
            "/api/price-history",
            "/api/polymarket",
            "/api/kpis",
            "/api/sentiment",
            "/api/public-opinion",
            "/api/signal",
        ],
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/price-history")
def price_history(
    ticker: str = Query("AAPL"),
    period_days: int = Query(180, ge=5, le=730),
    interval: str = Query("1d"),
    indicators: bool = Query(True),
):
    try:
        df = fetch_ohlcv(ticker, period_days=period_days, interval=interval)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.error("price-history error:\n%s", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Data fetch error: {exc}")

    if indicators:
        try:
            df = add_all_indicators(df)
        except Exception:
            logger.error("Indicator error:\n%s", traceback.format_exc())

    records = to_records(df)
    return {
        "ticker": ticker.upper(),
        "interval": interval,
        "count": len(records),
        "records": records,
    }


@app.get("/api/polymarket")
def polymarket_endpoint(
    ticker: str = Query("SPY"),
    keyword: Optional[str] = Query(None),
):
    if keyword:
        return {
            "keyword": keyword,
            "markets": search_markets(keyword, limit=10),
        }

    return polymarket_market_sentiment(ticker)


@app.get("/api/kpis")
def kpis(ticker: str = Query("AAPL")):
    try:
        price_info = latest_price(ticker)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.error("KPI price error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))

    snap: dict = {}
    try:
        df = fetch_ohlcv(ticker, period_days=90)
        snap = latest_indicator_snapshot(df)
    except Exception as exc:
        logger.warning("Technicals failed for %s: %s", ticker, exc)

    poly_score: float | None = None
    poly_label = "Unavailable"
    poly_markets: list = []

    try:
        poly = polymarket_market_sentiment(ticker)
        poly_score = poly["score"]
        poly_label = poly["label"]
        poly_markets = poly.get("markets", [])
        logger.info("Polymarket %s -> %.3f (%s)", ticker, poly_score, poly_label)
    except Exception as exc:
        logger.warning("Polymarket failed for %s: %s", ticker, exc)

    return {
        "ticker": price_info["ticker"],
        "as_of": price_info["as_of"],
        "price": price_info["price"],
        "prev_close": price_info["prev_close"],
        "change_pct": price_info["change_pct"],
        "rsi": snap.get("rsi"),
        "rsi_signal": rsi_signal(snap.get("rsi")),
        "macd": snap.get("macd"),
        "macd_signal": snap.get("macd_signal"),
        "macd_hist": snap.get("macd_hist"),
        "bb_upper": snap.get("bb_upper"),
        "bb_lower": snap.get("bb_lower"),
        "sma_7": snap.get("sma_7"),
        "sma_21": snap.get("sma_21"),
        "sma_50": snap.get("sma_50"),
        "polymarket_score": poly_score,
        "polymarket_label": poly_label,
        "polymarket_markets": poly_markets[:5],
    }


@app.get("/api/sentiment")
def sentiment_endpoint(ticker: str = Query("AAPL")):
    try:
        return {
            "ticker": ticker.upper(),
            "official_analysis": _official_analysis_payload(ticker),
            "public_opinion": _public_opinion_payload(ticker),
        }
    except Exception as exc:
        logger.error("Sentiment failed for %s: %s", ticker, exc)
        raise HTTPException(
            status_code=500,
            detail="Failed to process sentiment analysis.",
        )


@app.get("/api/public-opinion")
def public_opinion_endpoint(ticker: str = Query("AAPL")):
    try:
        summary = _public_opinion_payload(ticker)
        return {
            "ticker": ticker.upper(),
            "public_opinion": summary,
        }
    except Exception as exc:
        logger.error("Public opinion failed for %s: %s", ticker, exc)
        raise HTTPException(
            status_code=500,
            detail="Failed to process public opinion analysis.",
        )


@app.get("/api/signal")
def signal_endpoint(ticker: str = Query("AAPL")):
    return build_signal_payload(ticker)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
