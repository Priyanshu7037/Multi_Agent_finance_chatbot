from tools.llm import generate_text


KNOWN_CONCEPTS = {
    "ebitda": (
        "EBITDA means earnings before interest, taxes, depreciation, and "
        "amortization. It is a rough measure of operating profit before "
        "financing, tax, and some accounting costs. Investors use it to compare "
        "how efficiently companies generate earnings from core operations, but "
        "it does not show capital spending, debt burden, or actual cash left "
        "for shareholders."
    ),
    "pe ratio": (
        "The PE ratio compares a company's share price with its earnings per "
        "share. A higher PE often means investors expect stronger future "
        "growth, while a lower PE can suggest cheaper valuation or weaker "
        "expectations. It is most useful when compared with peers, growth, "
        "profit quality, and the company's own history."
    ),
    "p/e ratio": (
        "The PE ratio compares a company's share price with its earnings per "
        "share. A higher PE often means investors expect stronger future "
        "growth, while a lower PE can suggest cheaper valuation or weaker "
        "expectations. It is most useful when compared with peers, growth, "
        "profit quality, and the company's own history."
    ),
    "rsi": (
        "RSI, or Relative Strength Index, is a momentum indicator from 0 to "
        "100. Readings above 70 often suggest a stock may be overbought, while "
        "readings below 30 may suggest it is oversold. It should be used with "
        "trend, volume, and fundamentals rather than as a standalone signal."
    ),
    "market cap": (
        "Market capitalization is the total market value of a company: share "
        "price multiplied by shares outstanding. It helps investors understand "
        "company size, compare peers, and think about risk. Large-cap companies "
        "are often more stable, while smaller companies may offer higher growth "
        "with higher risk."
    ),
    "free cash flow": (
        "Free cash flow is the cash a company has left after operating expenses "
        "and capital spending. It matters because it can fund dividends, debt "
        "repayment, buybacks, and reinvestment. Strong free cash flow usually "
        "makes earnings quality more credible."
    ),
    "debt to equity": (
        "Debt-to-equity compares a company's debt with shareholder equity. It "
        "shows how much leverage the business uses. A high ratio can increase "
        "risk when profits fall or interest rates rise, while a low ratio often "
        "means the balance sheet is more conservative."
    ),
}


TUTOR_PROMPT = """
You are the Finance Tutor inside a multi-agent investing assistant.

Explain the user's finance or investing question clearly and maturely.

Guidelines:
- Start with a direct answer in plain language.
- Use a simple example when useful.
- Explain why the concept matters for investors.
- Keep recommendations educational, not personalized financial advice.
- Do not invent live market data or company-specific facts.
- If the question is vague, answer the likely concept and ask one focused
  follow-up question.
- Keep the response under 220 words.

Conversation Memory:
{memory_context}

User Question:
{query}
"""


def fallback_tutor_response(query: str) -> str:
    cleaned = (query or "").strip()
    normalized = cleaned.lower().replace("-", " ")

    if not cleaned:
        return (
            "Ask me a finance concept you want explained, such as PE ratio, "
            "EBITDA, RSI, market cap, diversification, or free cash flow."
        )

    for concept, explanation in KNOWN_CONCEPTS.items():
        if concept in normalized:
            return explanation

    return (
        "I can explain that finance concept, but the LLM is not available "
        "right now. Try asking again in a moment, or ask about a specific term "
        "like PE ratio, EBITDA, RSI, revenue growth, debt-to-equity, or free "
        "cash flow."
    )


def tutor_response(query: str, memory_context: str = "") -> str:
    prompt = TUTOR_PROMPT.format(
        query=query,
        memory_context=memory_context or "No previous chat memory.",
    )

    try:
        response = generate_text(
            prompt,
            max_tokens=300,
            temperature=0.25,
        )

        if response:
            return response

    except Exception as exc:
        print(f"Tutor Error: {exc}")

    return fallback_tutor_response(query)
