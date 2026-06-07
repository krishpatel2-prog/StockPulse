from transformers import pipeline

#load model
classifier = pipeline("sentiment-analysis", model="ProsusAI/finbert")
WEAK_SIGNAL_THRESHOLD = 0.2
NEGATIVE_PHRASES = {
    "refund": 0.55,
    "refunds": 0.55,
    "void": 0.5,
    "red flag": 0.65,
    "pressured": 0.5,
    "share price slide": 0.55,
    "exits": 0.45,
    "losing out": 0.45,
    "price-hike": 0.45,
    "raising prices": 0.45,
    "raise prices": 0.45,
    "price increase": 0.45,
    "prices yet again": 0.45,
}
POSITIVE_PHRASES = {
    "stock a buy": 0.55,
    "buying opportunity": 0.55,
    "beat inflation": 0.6,
    "pile into": 0.55,
    "invest": 0.4,
    "investment": 0.4,
    "growth targets": 0.45,
    "momentum": 0.4,
}


def _apply_title_rules(title: str, score: float):
    lowered = title.lower()
    has_price_language = "price" in lowered or "prices" in lowered
    has_increase_language = any(
        token in lowered for token in ("increase", "increases", "increased", "raise", "raises", "raised", "hike", "hikes", "hiked")
    )

    # Only correct overly positive takes on price hikes; never flip already negative headlines.
    if score > 0 and has_price_language and has_increase_language:
        score *= -1

    heuristic_score = 0.0
    for phrase, weight in NEGATIVE_PHRASES.items():
        if phrase in lowered:
            heuristic_score -= weight

    for phrase, weight in POSITIVE_PHRASES.items():
        if phrase in lowered:
            heuristic_score += weight

    # Only override weak model outputs, or strengthen an existing same-direction signal.
    if abs(score) < WEAK_SIGNAL_THRESHOLD and heuristic_score != 0:
        score = heuristic_score
    elif score > 0 and heuristic_score > 0:
        score = max(score, heuristic_score)
    elif score < 0 and heuristic_score < 0:
        score = min(score, heuristic_score)

    if abs(score) < WEAK_SIGNAL_THRESHOLD:
        score = 0

    score = max(min(score, 1.0), -1.0)
    return score


def _score_to_sentiment(score: float):
    if score >= WEAK_SIGNAL_THRESHOLD:
        return "positive"
    if score <= -WEAK_SIGNAL_THRESHOLD:
        return "negative"
    return "neutral"

def analyze_sentiment(news_list):
    results = []

    for news in news_list:
        text = news['title']

        result = classifier(text)[0]

        label = result['label'].lower()
        score = result['score']

        # convert to + / - score
        if label == 'positive':
            final_score = score
        elif label == 'negative':
            final_score = -score
        else:
            final_score = 0

        final_score = _apply_title_rules(text, final_score)
        final_label = _score_to_sentiment(final_score)

        results.append({
            "title": text,
            "source": news.get("source", "news"),
            "url": news.get("url") or news.get("link", ""),
            "created_at": news.get("created_at") or news.get("published", ""),
            "engagement": news.get("engagement"),
            "sentiment": final_label,
            "score":round(final_score,2)
        })

    return results

def get_average_score(results):
    if not results:
        return 0

    filtered = [item for item in results if abs(item["score"]) >= WEAK_SIGNAL_THRESHOLD]

    if not filtered:
        return 0

    total = sum(item["score"] for item in filtered)
    return round(total / len(filtered), 2)

def get_signal(score):
    if score > 0.4:
        return "STRONG BUY"
    elif score > 0.1:
        return "BUY"
    elif score >= -0.1:
        return "NEUTRAL"
    elif score >= -0.4:
        return "SELL"
    else:
        return "STRONG SELL"


def calculate_confidence(results):
    if not results:
        return 0

    strong = sum(1 for r in results if abs(r["score"]) > 0.6)

    return round(strong / len(results), 2)


def generate_reason(results):
    meaningful = [item for item in results if abs(item["score"]) >= WEAK_SIGNAL_THRESHOLD]

    if not meaningful:
        return "Limited clear sentiment in recent news"

    avg_score = get_average_score(results)
    positive_weight = sum(item["score"] for item in meaningful if item["score"] > 0)
    negative_weight = abs(sum(item["score"] for item in meaningful if item["score"] < 0))

    if -0.1 <= avg_score <= 0.1:
        if negative_weight > positive_weight:
            return "Mixed market sentiment with slight negative bias"
        if positive_weight > negative_weight:
            return "Mixed market sentiment with slight positive bias"
        return "Mixed market sentiment"

    if positive_weight > negative_weight:
        return "Majority positive news sentiment"
    if negative_weight > positive_weight:
        return "Majority negative news sentiment"
    return "Mixed market sentiment"
