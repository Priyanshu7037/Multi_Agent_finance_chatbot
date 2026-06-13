from __future__ import annotations

from typing import Optional


def _normalize_profile(value: Optional[str]) -> str:
    if not value:
        return "moderate"

    value = value.strip().lower()

    if "aggress" in value or "high" in value:
        return "aggressive"
    if "conserv" in value or "defens" in value or "preserv" in value or "low" in value:
        return "conservative"
    if "mod" in value or "balanced" in value:
        return "moderate"
    if "growth" in value and "aggress" not in value:
        return "moderate"

    return "moderate"


def profile_risk(
    age: Optional[int],
    horizon_years: Optional[int],
    goal: str,
    user_risk_preference: Optional[str],
) -> dict[str, object]:
    goal_text = (goal or "").strip().lower()
    preference = _normalize_profile(user_risk_preference)

    score = 50.0

    if horizon_years is not None:
        if horizon_years >= 15:
            score += 20
        elif horizon_years >= 10:
            score += 12
        elif horizon_years >= 5:
            score += 3
        elif horizon_years >= 3:
            score -= 5
        else:
            score -= 12

    if age is not None:
        if age < 30:
            score += 12
        elif age < 45:
            score += 6
        elif age < 60:
            score += 1
        else:
            score -= 10

    if "retire" in goal_text or "retirement" in goal_text:
        score += 8
    if "income" in goal_text or "preservation" in goal_text:
        score -= 8
    if "growth" in goal_text and "aggress" in goal_text:
        score += 8

    if preference == "aggressive":
        score += 16
    elif preference == "conservative":
        score -= 16
    elif preference == "moderate":
        score += 0

    score = max(10.0, min(90.0, score))

    if score >= 70:
        risk_profile = "aggressive"
    elif score >= 45:
        risk_profile = "moderate"
    else:
        risk_profile = "conservative"

    return {
        "risk_profile": risk_profile,
        "risk_score": round(score, 2),
    }
