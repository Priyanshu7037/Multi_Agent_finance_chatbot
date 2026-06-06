from agents.router import route_query


TEST_QUERIES = [
    "Should I invest in Wipro or TCS?",
    "Compare TCS and Infosys",
    "Which is better Reliance or HDFC Bank?",
    "Should I buy TCS?",
    "Show Infosys stock history",
    "Latest news about Reliance",
    "What is EBITDA?",
    "How should I allocate my portfolio?",
]


def main():
    print("=" * 80)
    print("ROUTER TEST")
    print("=" * 80)

    for query in TEST_QUERIES:
        print("\n")
        print("-" * 80)
        print(f"QUERY: {query}")

        result = route_query(query)

        print("RESULT:")
        print(result)

        print(f"WORKFLOW: {result.get('workflow')}")
        print(f"TICKER: {result.get('ticker')}")
        print(f"TICKERS: {result.get('tickers')}")
        print(f"CONFIDENCE: {result.get('confidence')}")
        print(f"REASON: {result.get('reason')}")

    print("\n")
    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()