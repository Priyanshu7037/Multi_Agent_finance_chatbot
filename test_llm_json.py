from tools.llm import extract_json_from_text

TEST_CASES = [
    (
        "valid_json",
        '{"workflow": "committee", "ticker": "TCS.NS"}',
    ),
    (
        "markdown_json",
        "```json\n{\n  \"workflow\": \"committee\",\n  \"ticker\": \"TCS.NS\"\n}\n```",
    ),
    (
        "trailing_comma_json",
        '{\n  \"workflow\": \"committee\",\n  \"ticker\": \"TCS.NS\",\n}',
    ),
    (
        "extra_text_json",
        "Here is the result:\n{\n  \"workflow\": \"committee\",\n  \"ticker\": \"TCS.NS\"\n}\nThank you!",
    ),
    (
        "multiple_json_blocks",
        "First result:\n{\n  \"workflow\": \"committee\",\n  \"ticker\": \"TCS.NS\"\n}\nSecond result:\n{\n  \"workflow\": \"history\",\n  \"ticker\": \"INFY.NS\"\n}",
    ),
]


def main():
    print("LLM JSON extraction tests")
    print("=" * 40)

    for name, text in TEST_CASES:
        try:
            result = extract_json_from_text(text)
            print(f"{name}: PASS -> {result}")
        except Exception as exc:
            print(f"{name}: FAIL -> {exc}")

    print("=" * 40)
    print("Done")


if __name__ == "__main__":
    main()
