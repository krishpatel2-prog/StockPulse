from __future__ import annotations

from collections import Counter
from math import tanh

from models.sentiment_engine import WEAK_SIGNAL_THRESHOLD, analyze_sentiment, get_average_score


def _public_signal(score: float) -> str:
    if score > 0.25:
        return "BULLISH"
    if score < -0.25:
        return "BEARISH"
    return "NEUTRAL"


def _confidence(analyzed_posts: list[dict], score: float) -> float:
    if not analyzed_posts:
        return 0.0

    volume = len(analyzed_posts)
    volume_factor = tanh(volume / 12.0)

    sentiment_counts = Counter(post.get("sentiment", "neutral") for post in analyzed_posts)
    if score > 0.25:
        agreement = sentiment_counts.get("positive", 0) / volume
    elif score < -0.25:
        agreement = sentiment_counts.get("negative", 0) / volume
    else:
        agreement = sentiment_counts.get("neutral", 0) / volume
        if agreement == 0:
            directional_balance = abs(
                sentiment_counts.get("positive", 0) - sentiment_counts.get("negative", 0)
            ) / volume
            agreement = 1.0 - directional_balance

    meaningful = [
        post for post in analyzed_posts
        if abs(post.get("score", 0.0)) >= WEAK_SIGNAL_THRESHOLD
    ]
    intensity = (
        sum(abs(post.get("score", 0.0)) for post in meaningful) / len(meaningful)
        if meaningful else 0.0
    )

    return round(min(1.0, volume_factor * 0.5 + agreement * 0.35 + intensity * 0.15), 3)


def analyze_public_opinion(posts: list[dict]) -> dict:
    if not posts:
        return {
            "public_sentiment_score": 0.0,
            "public_signal": "NEUTRAL",
            "confidence": 0.0,
            "volume": 0,
            "top_discussions": [],
            "sources": [],
        }

    analyzable_posts: list[dict] = []
    for post in posts:
        text = (post.get("text") or post.get("title") or "").strip()
        if not text:
            continue
        analyzable_posts.append({
            "title": text,
            "source": post.get("source", "public"),
            "url": post.get("url", ""),
            "created_at": post.get("created_at", ""),
            "engagement": post.get("engagement"),
        })

    analyzed_posts = analyze_sentiment(analyzable_posts)
    if not analyzed_posts:
        return {
            "public_sentiment_score": 0.0,
            "public_signal": "NEUTRAL",
            "confidence": 0.0,
            "volume": 0,
            "top_discussions": [],
            "sources": [],
        }

    score = round(get_average_score(analyzed_posts), 4)
    signal = _public_signal(score)
    confidence = _confidence(analyzed_posts, score)

    ranked_discussions = sorted(
        analyzed_posts,
        key=lambda post: (
            abs(post.get("score", 0.0)),
            post.get("engagement") or 0,
        ),
        reverse=True,
    )
    top_discussions = ranked_discussions[:10]

    sources = [
        {
            "title": item.get("title", "Public discussion"),
            "source": item.get("source", "public"),
            "url": item.get("url", ""),
        }
        for item in top_discussions
        if item.get("url")
    ]

    return {
        "public_sentiment_score": score,
        "public_signal": signal,
        "confidence": confidence,
        "volume": len(analyzed_posts),
        "top_discussions": top_discussions,
        "sources": sources[:5],
    }
