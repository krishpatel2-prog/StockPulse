from math import tanh

from models.sentiment_engine import analyze_sentiment, get_average_score


def analyze_social_sentiment(posts: list[dict]) -> dict:
    if not posts:
        return {
            "score": 0.0,
            "confidence": 0.0,
            "volume": 0,
            "posts": [],
        }

    analyzable_posts = []
    for post in posts:
        text = post.get("text", "").strip()
        if not text:
            continue
        analyzable_posts.append({
            "title": text,
            "url": post.get("url", ""),
            "source": post.get("source", "social"),
            "created_at": post.get("created_at", ""),
            "engagement": post.get("engagement"),
        })

    analyzed_posts = analyze_sentiment(analyzable_posts)
    score = get_average_score(analyzed_posts)
    volume = len(analyzed_posts)
    confidence = round(min(1.0, tanh(volume / 12.0)), 3)

    return {
        "score": round(score, 4),
        "confidence": confidence,
        "volume": volume,
        "posts": analyzed_posts,
    }
