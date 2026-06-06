from tools.llm import generate_text


GENERAL_ASSISTANT_PROMPT = """
You are a mature, professional assistant inside a financial AI app.

Respond to the user's message naturally and helpfully.

Guidelines:
- For greetings, brief small talk, thanks, or unclear non-essential messages,
  reply warmly and invite the user to ask a finance or investing question.
- Do not force every answer into a stock recommendation.
- If the user asks something outside finance, answer briefly if it is harmless,
  then gently mention you are best at market and finance analysis.
- Keep the tone polished, calm, and concise.
- Do not invent live market data.

Conversation Memory:
{memory_context}

User Message:
{query}
"""


def fallback_general_response(query: str) -> str:
    normalized = (query or "").strip().lower()

    greetings = {
        "hi",
        "hii",
        "hello",
        "hey",
        "hey there",
        "good morning",
        "good afternoon",
        "good evening",
    }

    if normalized in greetings:
        return (
            "Hello. How can I help you today? You can ask me about stocks, "
            "market news, portfolio allocation, comparisons, or financial "
            "concepts."
        )

    if normalized in {"thanks", "thank you", "ok", "okay"}:
        return (
            "You are welcome. Ask me whenever you want to explore a stock, "
            "compare companies, review portfolio allocation, or understand a "
            "finance concept."
        )

    return (
        "I can help with that in a general way. For the best results, ask me "
        "about a stock, market news, portfolio allocation, a comparison, or a "
        "financial concept you want explained."
    )


def general_assistant_response(query: str, memory_context: str = "") -> str:
    prompt = GENERAL_ASSISTANT_PROMPT.format(
        query=query,
        memory_context=memory_context or "No previous chat memory.",
    )

    try:
        response = generate_text(
            prompt,
            max_tokens=220,
            temperature=0.35,
        )

        if response:
            return response

    except Exception as exc:
        print(f"General Assistant Error: {exc}")

    return fallback_general_response(query)
