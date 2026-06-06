from agents.fundamental import analyze as fundamental_analyze
from agents.sentiment import analyze as sentiment_analyze
from agents.devil import analyze as devil_analyze
from agents.committee_summary import (
    generate_summary
)
from agents.quant import (
    analyze as quant_analyze
)

def run_quant(state):

    state.quant_result = (
        quant_analyze(
            state.ticker
        )
    )

    return state
def run_summary(state):

    state = generate_summary(
        state
    )

    return state

def run_devil(state):

    state.devil_result = devil_analyze(
        state
    )

    return state

def run_fundamental(state):

    state.fundamental_result = (
        fundamental_analyze(state.ticker)
    )

    return state


def run_sentiment(state):

    state.sentiment_result = (
        sentiment_analyze(state.ticker)
    )

    return state