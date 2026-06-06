from collections import Counter


def normalize_recommendation(recommendation):

    recommendation = (
        recommendation
        or
        "HOLD"
    ).upper()

    if recommendation == "STRONG BUY":
        return "BUY"

    if recommendation == "STRONG SELL":
        return "SELL"

    if recommendation in [
        "BUY",
        "HOLD",
        "SELL"
    ]:
        return recommendation

    return "HOLD"


def has_governance_risk(devil):

    keywords = [
        "bribery",
        "fraud",
        "corruption",
        "governance",
        "accounting",
        "money laundering",
        "regulatory investigation"
    ]

    for risk in devil.weaknesses:

        risk_lower = risk.lower()

        for keyword in keywords:

            if keyword in risk_lower:
                return True

    return False


def has_earnings_decline(fundamental):

    for weakness in fundamental.weaknesses:

        if "earnings declined" in weakness.lower():
            return True

    return False


def build_votes(state):

    votes = []

    votes.append(
        normalize_recommendation(
            state.fundamental_result.recommendation
        )
    )

    votes.append(
        normalize_recommendation(
            state.sentiment_result.recommendation
        )
    )

    if getattr(state, "quant_result", None):

        votes.append(
            normalize_recommendation(
                state.quant_result.recommendation
            )
        )

    return votes


def committee_decision(state):

    fundamental = state.fundamental_result
    sentiment = state.sentiment_result
    devil = state.devil_result

    quant = getattr(
        state,
        "quant_result",
        None
    )

    reasoning = []

    # ---------------------------------
    # Weighted Score
    # ---------------------------------

    positive_score = (
        0.6 * fundamental.score +
        0.4 * sentiment.score
    )

    if quant:

        positive_score = (
            0.4 * fundamental.score +
            0.3 * sentiment.score +
            0.3 * quant.score
        )

        reasoning.append(
            "Quant agent included."
        )

    reasoning.append(
        f"Initial score: {positive_score:.2f}"
    )

    # ---------------------------------
    # Agreement / Conflict Detection
    # ---------------------------------

    conflict = False

    fundamental_vote = normalize_recommendation(
        fundamental.recommendation
    )

    sentiment_vote = normalize_recommendation(
        sentiment.recommendation
    )

    if (
        fundamental_vote !=
        sentiment_vote
    ):

        conflict = True

        positive_score -= 5

        reasoning.append(
            "Conflict detected between Fundamental and Sentiment."
        )

    quant_vote = None

    if quant:
        quant_vote = normalize_recommendation(
            quant.recommendation
        )

    if (
        quant
        and
        quant_vote !=
        fundamental_vote
    ):

        conflict = True

        positive_score -= 5

        reasoning.append(
            "Conflict detected between Quant and Fundamental."
        )

    # ---------------------------------
    # Earnings Penalty
    # ---------------------------------

    if has_earnings_decline(
        fundamental
    ):

        positive_score -= 5

        reasoning.append(
            "Declining earnings penalty applied."
        )

    # ---------------------------------
    # Devil Risk Adjustment
    # ---------------------------------

    if devil.score >= 70:

        risk_level = "HIGH"

        multiplier = 0.8

    elif devil.score >= 40:

        risk_level = "MEDIUM"

        multiplier = 0.9

    else:

        risk_level = "LOW"

        multiplier = 1.0

    positive_score *= multiplier

    reasoning.append(
        f"{risk_level} risk level detected."
    )

    # ---------------------------------
    # Governance Veto
    # ---------------------------------

    governance_risk = (
        has_governance_risk(
            devil
        )
    )

    if governance_risk:

        reasoning.append(
            "Governance veto triggered."
        )

    # ---------------------------------
    # Voting Layer
    # ---------------------------------

    votes = build_votes(
        state
    )

    vote_counter = Counter(
        votes
    )

    state.committee_votes = dict(
        vote_counter
    )

    reasoning.append(
        f"Votes: {dict(vote_counter)}"
    )

    # ---------------------------------
    # Final Score
    # ---------------------------------

    final_score = round(
        positive_score,
        2
    )

    state.final_score = final_score

    # ---------------------------------
    # Final Decision
    # ---------------------------------

    if governance_risk:

        decision = "HOLD"

    elif vote_counter.get(
        "SELL",
        0
    ) >= 2:

        decision = "SELL"

    elif vote_counter.get(
        "BUY",
        0
    ) >= 2:

        if final_score >= 60:
            if final_score >= 80:
                decision = "STRONG BUY"
            else:
                decision = "BUY"
        else:
            decision = "HOLD"

    else:

        if final_score >= 80:

            decision = "STRONG BUY"

        elif final_score >= 60:

            decision = "BUY"

        elif final_score >= 40:

            decision = "HOLD"

        else:

            decision = "SELL"

    state.final_decision = decision

    # ---------------------------------
    # Committee Confidence
    # ---------------------------------

    confidences = [
        fundamental.confidence,
        sentiment.confidence,
        devil.confidence
    ]

    if quant:

        confidences.append(
            quant.confidence
        )

    confidence = (
        sum(confidences)
        /
        len(confidences)
    )

    if conflict:

        confidence -= 10

    if governance_risk:

        confidence -= 10

    confidence = max(
        0,
        min(
            confidence,
            100
        )
    )

    state.committee_confidence = round(
        confidence,
        2
    )

    # ---------------------------------
    # Store Extra Info
    # ---------------------------------

    state.detected_conflicts = conflict

    state.risk_level = risk_level

    state.committee_reasoning = (
        "\n".join(reasoning)
    )

    return state
