import json
import os
import re

from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()


DEFAULT_MODEL = "Qwen/Qwen2.5-7B-Instruct"
UNSUPPORTED_MODELS = {
    "microsoft/Phi-3-mini-4k-instruct",
    "google/gemma-2-2b-it"
}

client = InferenceClient(
    token=os.getenv("HF_TOKEN")
)


def get_model_name():
    model = os.getenv("HF_MODEL", DEFAULT_MODEL).strip()
    if not model or model in UNSUPPORTED_MODELS:
        return DEFAULT_MODEL
    return model


def generate_text(prompt, max_tokens=700, temperature=0.2):
    if not os.getenv("HF_TOKEN"):
        raise RuntimeError(
            "HF_TOKEN is missing. Create a free Hugging Face token "
            "and add HF_TOKEN=your_token to .env."
        )

    model = get_model_name()
    request = {
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    if model:
        request["model"] = model

    response = client.chat_completion(**request)
    message = response.choices[0].message

    if isinstance(message, dict):
        return message.get("content", "").strip()

    return message.content.strip()


def _remove_markdown_fences(text: str) -> str:
    """Strip Markdown code fences and preserve the enclosed JSON text."""
    text = re.sub(r"```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    return text.replace("```", "").strip()


def _find_first_balanced_json(text: str) -> str:
    """Locate the first balanced JSON object in the text."""
    start_positions = [i for i, char in enumerate(text) if char == "{"]

    for start in start_positions:
        depth = 0
        in_string = False
        escape = False

        for index in range(start, len(text)):
            char = text[index]

            if escape:
                escape = False
                continue

            if char == "\\":
                escape = True
                continue

            if char == '"':
                in_string = not in_string
                continue

            if in_string:
                continue

            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1

            if depth == 0:
                return text[start : index + 1]

    raise ValueError("No balanced JSON object found in the text.")


def _repair_trailing_commas(json_text: str) -> str:
    """Remove trailing commas from JSON objects and arrays."""
    json_text = re.sub(r",\s*(?=[}\]])", "", json_text)
    return json_text


def extract_json_from_text(text: str) -> dict:
    """Extract the first JSON object from an LLM response string.

    Handles Markdown fences, extra explanatory text, trailing commas,
    and multiple JSON blocks by selecting the first balanced object.
    """
    raw_text = text or ""
    cleaned_text = _remove_markdown_fences(raw_text)

    json_text = _find_first_balanced_json(cleaned_text)
    repaired_text = _repair_trailing_commas(json_text)

    try:
        parsed = json.loads(repaired_text)
    except json.JSONDecodeError as error:
        raise json.JSONDecodeError(
            f"Failed to parse extracted JSON. Text: {repaired_text}",
            repaired_text,
            error.pos,
        ) from error

    if not isinstance(parsed, dict):
        raise ValueError(
            "Extracted JSON must be an object (dictionary) but parsed to a different type."
        )

    return parsed


def generate_json(prompt, max_tokens=700, temperature=0.1):
    text = generate_text(
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=temperature,
    )

    print("RAW LLM RESPONSE:")
    print(text)

    try:
        result = extract_json_from_text(text)
    except json.JSONDecodeError as error:
        print("EXTRACTED JSON:")
        print("<failed to extract valid JSON>")
        print(f"JSON decoding error: {error}")
        raise
    except ValueError as error:
        print("EXTRACTED JSON:")
        print("<failed to extract valid JSON>")
        print(f"Extraction error: {error}")
        raise

    print("EXTRACTED JSON:")
    print(json.dumps(result, indent=2))

    return result
