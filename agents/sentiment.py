from data.models import AgentOutput
from tools.llm import generate_json
from tools.yahoo_finance import get_company_news

def sentiment_to_score(sentiment):

    sentiment = sentiment.upper()

    if sentiment == "VERY_POSITIVE":
        return 90, "STRONG BUY"

    elif sentiment == "POSITIVE":
        return 80, "BUY"

    elif sentiment == "NEUTRAL":
        return 50, "HOLD"

    elif sentiment == "NEGATIVE":
        return 30, "SELL"

    elif sentiment == "VERY_NEGATIVE":
        return 10, "STRONG SELL"

    return 50, "HOLD"


def analyze(ticker):

    headlines = get_company_news(
        ticker,
        limit=10
    )

    if not headlines:

        return AgentOutput(
            agent_name="Sentiment",
            score=50,
            confidence=50,
            recommendation="HOLD",
            strengths=[],
            weaknesses=[
                "No news headlines available"
            ],
            reasoning="No news data found."
        )

    news_text = "\n".join(
        [
            f"- {headline}"
            for headline in headlines
        ]
    )

    prompt = f"""
You are a professional financial news analyst.

Analyze the news headlines below
and determine overall market sentiment.

News Headlines:

{news_text}

Return ONLY valid JSON.

{{
    "sentiment": "POSITIVE",
    "confidence": 80,
    "strengths": [
        "positive factor 1",
        "positive factor 2"
    ],
    "weaknesses": [
        "negative factor 1",
        "negative factor 2"
    ]
}}

Allowed sentiment values:

VERY_POSITIVE
POSITIVE
NEUTRAL
NEGATIVE
VERY_NEGATIVE

Rules:

1. Return valid JSON only
2. No markdown
3. No explanations outside JSON
4. confidence must be between 0 and 100
5. strengths and weaknesses should each contain 2-5 items
"""

    try:

        result = generate_json(
            prompt,
            max_tokens=500
        )

        sentiment = result.get(
            "sentiment",
            "NEUTRAL"
        )

        confidence = result.get(
            "confidence",
            50
        )

        strengths = result.get(
            "strengths",
            []
        )

        weaknesses = result.get(
            "weaknesses",
            []
        )

    except Exception as e:

        print(
            "Sentiment Agent Error:",
            e
        )

        sentiment = "NEUTRAL"

        confidence = 50

        strengths = []

        weaknesses = [
            "Failed to analyze sentiment"
        ]

    score, recommendation = (
        sentiment_to_score(
            sentiment
        )
    )

    reasoning = f"""
Sentiment: {sentiment}

News Headlines:
{news_text}
"""

    return AgentOutput(
        agent_name="Sentiment",
        score=score,
        confidence=confidence,
        recommendation=recommendation,
        strengths=strengths,
        weaknesses=weaknesses,
        reasoning=reasoning
    )
