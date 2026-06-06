from tools.llm import generate_text


def generate_summary(state):

    prompt = f"""
You are the Chairperson of an investment committee.

Review the outputs from all analysts.

Fundamental Agent:

Score: {state.fundamental_result.score}

Strengths:
{chr(10).join(state.fundamental_result.strengths)}

Weaknesses:
{chr(10).join(state.fundamental_result.weaknesses)}

------------------------------------------------

Sentiment Agent:

Score: {state.sentiment_result.score}

Strengths:
{chr(10).join(state.sentiment_result.strengths)}

Weaknesses:
{chr(10).join(state.sentiment_result.weaknesses)}

------------------------------------------------

Quant Agent:

Score: {state.quant_result.score if state.quant_result else "Not available"}

Strengths:
{chr(10).join(state.quant_result.strengths) if state.quant_result else "Not available"}

Weaknesses:
{chr(10).join(state.quant_result.weaknesses) if state.quant_result else "Not available"}

------------------------------------------------

Devil's Advocate:

Risks:
{chr(10).join(state.devil_result.weaknesses)}

------------------------------------------------

Final Committee Decision:

{state.final_decision}

Final Score:

{state.final_score}

Write:

1. Executive Summary
2. Key Positives
3. Key Risks
4. Final Recommendation

Keep professional tone.
Limit to 250 words.
"""
    try:
        summary = generate_text(
            prompt,
            max_tokens=600,
            temperature=0.2
        )
    except Exception as error:
        summary = (
            "Committee summary unavailable because the LLM request failed.\n\n"
            f"Reason: {error}"
        )

    state.committee_summary = summary

    return state
