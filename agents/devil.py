from data.models import AgentOutput
from tools.llm import generate_json


def calculate_risk_score(risks):

    severity_weights = {
        "LOW": 5,
        "MEDIUM": 10,
        "HIGH": 15
    }

    score = sum(
        severity_weights.get(
            risk["severity"],
            10
        )
        for risk in risks
    )

    return min(score, 75)


def calculate_confidence(risks):

    if len(risks) >= 5:
        return 90

    elif len(risks) >= 3:
        return 80

    return 70


def analyze(state):

    fundamental = state.fundamental_result
    sentiment = state.sentiment_result

    prompt = f"""
You are a professional hedge fund Devil's Advocate.

Your role is to challenge the investment thesis.

Identify hidden risks, weak assumptions,
business threats, valuation concerns,
competitive threats, macroeconomic risks,
and execution risks.

Fundamental Analysis

Score: {fundamental.score}

Strengths:
{chr(10).join(fundamental.strengths)}

Weaknesses:
{chr(10).join(fundamental.weaknesses)}

Reasoning:
{fundamental.reasoning}


Sentiment Analysis

Score: {sentiment.score}

Strengths:
{chr(10).join(sentiment.strengths)}

Weaknesses:
{chr(10).join(sentiment.weaknesses)}

Reasoning:
{sentiment.reasoning}


Return ONLY valid JSON.

{{
    "risks": [
        {{
            "risk": "description",
            "severity": "LOW"
        }},
        {{
            "risk": "description",
            "severity": "MEDIUM"
        }},
        {{
            "risk": "description",
            "severity": "HIGH"
        }}
    ]
}}

Rules:

1. Generate 3 to 5 risks
2. severity must be LOW, MEDIUM or HIGH
3. Return valid JSON only
4. No markdown
5. No explanation outside JSON
"""

    try:

        result = generate_json(
            prompt,
            max_tokens=700
        )

        risks = result.get(
            "risks",
            []
        )

    except Exception as e:

        print(
            "Devil Agent JSON Error:",
            e
        )

        risks = [
            {
                "risk":
                "Failed to parse LLM response",
                "severity":
                "MEDIUM"
            }
        ]

    risk_score = calculate_risk_score(
        risks
    )

    confidence = calculate_confidence(
        risks
    )

    weaknesses = []

    for risk in risks:

        weaknesses.append(
            f"[{risk['severity']}] "
            f"{risk['risk']}"
        )

    reasoning = "\n".join(
        weaknesses
    )

    return AgentOutput(
        agent_name="DevilAdvocate",
        score=risk_score,
        confidence=confidence,
        recommendation="CAUTION",
        strengths=[],
        weaknesses=weaknesses,
        reasoning=reasoning
    )
