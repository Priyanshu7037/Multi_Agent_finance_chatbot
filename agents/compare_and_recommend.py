from __future__ import annotations

from typing import Any, Dict, List, Tuple

from agents.fundamental import analyze as fundamental_analyze
from agents.sentiment import analyze as sentiment_analyze
from agents.market_workflows import comparison_analysis
from tools.llm import generate_text


def _format_list(items: List[str]) -> str:
    if not items:
        return "None"

    return "; ".join(items)


def _build_company_insight(ticker: str, fundamental: Any, sentiment: Any) -> str:
    return (
        f"Ticker: {ticker}\n"
        f"Fundamental score: {fundamental.score}\n"
        f"Fundamental recommendation: {fundamental.recommendation}\n"
        f"Fundamental strengths: {_format_list(fundamental.strengths)}\n"
        f"Fundamental weaknesses: {_format_list(fundamental.weaknesses)}\n"
        f"Sentiment score: {sentiment.score}\n"
        f"Sentiment recommendation: {sentiment.recommendation}\n"
        f"Sentiment strengths: {_format_list(sentiment.strengths)}\n"
        f"Sentiment weaknesses: {_format_list(sentiment.weaknesses)}\n"
    )


def _parse_response(text: str) -> Tuple[str, str]:
    normalized = text.strip()
    summary = normalized
    recommendation = ""

    if "RECOMMENDATION:" in normalized:
        parts = normalized.split("RECOMMENDATION:", 1)
        summary = parts[0].replace("SUMMARY:", "").strip()
        recommendation = parts[1].strip()
    elif "SUMMARY:" in normalized:
        parts = normalized.split("SUMMARY:", 1)
        summary = parts[1].strip()

    return summary, recommendation


def _determine_winner(tickers: List[str], fundamentals: Dict[str, Any], sentiments: Dict[str, Any]) -> Tuple[str, float]:
    scores: Dict[str, float] = {}

    for ticker in tickers:
        fundamental = fundamentals[ticker]
        sentiment = sentiments[ticker]
        scores[ticker] = 0.6 * fundamental.score + 0.4 * sentiment.score

    if not scores:
        return "", 0.0

    winner = max(scores, key=scores.get)
    confidence = max(0.0, min(1.0, scores[winner] / 100.0))

    return winner, confidence


def compare_and_recommend_analysis(tickers: List[str]) -> Dict[str, object]:
    tickers = [ticker for ticker in tickers if isinstance(ticker, str)]
    comparison = comparison_analysis(tickers)

    fundamentals = {
        ticker: fundamental_analyze(ticker)
        for ticker in tickers
    }
    sentiments = {
        ticker: sentiment_analyze(ticker)
        for ticker in tickers
    }

    company_sections = [
        _build_company_insight(ticker, fundamentals[ticker], sentiments[ticker])
        for ticker in tickers
    ]

    prompt = (
        "You are a financial recommendation analyst.\n"
        "Compare the following companies and choose the best long-term investment.\n"
        "Use only the provided data, strengths, and weaknesses.\n"
        "Do not invent additional facts.\n"
        "Provide two labeled sections: SUMMARY: and RECOMMENDATION:.\n"
        "Include strengths of each company, weaknesses, key differences, best choice for long-term investment, and a confidence statement.\n"
        "Comparison data:\n"
        f"{chr(10).join(comparison.get('data_lines', []))}\n"
        "Company insights:\n"
        f"{chr(10).join(company_sections)}\n"
    )

    try:
        analysis_text = generate_text(
            prompt,
            max_tokens=500,
            temperature=0.25,
        )
    except Exception as error:
        analysis_text = (
            "SUMMARY: The stock comparison and recommendation could not be fully generated because the language model was unavailable. "
            "Use the available fundamental and sentiment data instead.\n"
            "RECOMMENDATION: Analyze both companies carefully and consider the company with stronger fundamentals and sentiment as the likely better choice."
        )
        print(f"Compare and Recommend Error: {error}")

    comparison_summary, recommendation_text = _parse_response(analysis_text)
    if not recommendation_text:
        recommendation_text = comparison_summary

    winner, confidence = _determine_winner(tickers, fundamentals, sentiments)

    return {
        "workflow": "compare_and_recommend",
        "tickers": tickers,
        "winner": winner,
        "confidence": confidence,
        "comparison_summary": comparison_summary,
        "recommendation": recommendation_text,
    }
