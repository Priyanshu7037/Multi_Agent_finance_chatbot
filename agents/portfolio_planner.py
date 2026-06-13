from __future__ import annotations

import re
from typing import Any

from tools.llm import generate_json


def _normalize_risk_profile(value: Any) -> str:
    if not isinstance(value, str):
        return "moderate"

    value = value.strip().lower()

    if "aggress" in value:
        return "aggressive"
    if "conserv" in value or "defens" in value or "preserv" in value:
        return "conservative"
    if "moderate" in value or "balanced" in value:
        return "moderate"
    if "growth" in value and "aggress" not in value:
        return "growth"

    return value or "moderate"


def _parse_numeric_value(value: Any) -> float | None:
    if value is None:
        return None

    if isinstance(value, (int, float)):
        return float(value)

    text = str(value)
    text = text.replace("₹", "")
    text = text.replace(",", "")
    text = text.strip().lower()

    match = re.search(r"([0-9]+(?:\.[0-9]+)?)", text)
    if match:
        return float(match.group(1))

    return None


def build_portfolio_planner_prompt(query: str) -> str:
    return (
        "You are a portfolio planning assistant. "
        "Convert the user query into structured investment inputs. "
        "Return only valid JSON with no markdown or extra text.\n"
        "Required fields: amount, age, goal, risk_profile, horizon_years, existing_holdings, sector_preferences, constraints.\n"
        "If a field is unavailable, return null or an empty list/dictionary.\n"
        "Do not invent information. Use only the user query.\n"
        "Examples:\n"
        "{\n"
        "  \"amount\": 1000000,\n"
        "  \"age\": 25,\n"
        "  \"goal\": \"growth\",\n"
        "  \"risk_profile\": \"aggressive\",\n"
        "  \"horizon_years\": 15,\n"
        "  \"existing_holdings\": [\"TCS.NS\", \"RELIANCE.NS\"],\n"
        "  \"sector_preferences\": [\"Technology\"],\n"
        "  \"constraints\": {\"liquidity\": \"high\"}\n"
        "}\n"
        "User Query:\n"
        f"{query.strip()}\n"
    )


def parse_portfolio_query(query: str) -> dict[str, Any]:
    prompt = build_portfolio_planner_prompt(query)

    try:
        result = generate_json(
            prompt=prompt,
            max_tokens=260,
            temperature=0.0,
        )

    except Exception:
        result = {}

    age_value = _parse_numeric_value(result.get("age"))
    horizon_value = _parse_numeric_value(result.get("horizon_years"))

    data = {
        "amount": _parse_numeric_value(result.get("amount")),
        "age": int(age_value) if age_value is not None else None,
        "goal": result.get("goal") if isinstance(result.get("goal"), str) else "",
        "risk_profile": _normalize_risk_profile(result.get("risk_profile")),
        "horizon_years": int(horizon_value) if horizon_value is not None else None,
        "existing_holdings": result.get("existing_holdings") if isinstance(result.get("existing_holdings"), list) else [],
        "sector_preferences": result.get("sector_preferences") if isinstance(result.get("sector_preferences"), list) else [],
        "constraints": result.get("constraints") if isinstance(result.get("constraints"), dict) else {},
    }

    return data
