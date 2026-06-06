import json
import os
import re

from dotenv import load_dotenv
from huggingface_hub import InferenceClient

try:
    import streamlit as st
except Exception:
    st = None

load_dotenv()

DEFAULT_MODEL = "Qwen/Qwen2.5-7B-Instruct"

UNSUPPORTED_MODELS = {
    "microsoft/Phi-3-mini-4k-instruct",
    "google/gemma-2-2b-it",
}


def get_hf_token():
    """
    Get Hugging Face token from:
    1. Local .env
    2. Streamlit Secrets
    """
    token = os.getenv("HF_TOKEN")

    if token:
        return token

    if st:
        try:
            return st.secrets["HF_TOKEN"]
        except Exception:
            pass

    return None


def get_model_name():
    """
    Get model name from:
    1. Local .env
    2. Streamlit Secrets
    """
    model = os.getenv("HF_MODEL")

    if not model and st:
        try:
            model = st.secrets.get("HF_MODEL")
        except Exception:
            pass

    if not model:
        model = DEFAULT_MODEL

    model = model.strip()

    if model in UNSUPPORTED_MODELS:
        return DEFAULT_MODEL

    return model


def get_client():
    token = get_hf_token()

    if not token:
        raise RuntimeError(
            "HF_TOKEN not found. "
            "Provide it in .env locally or Streamlit Secrets when deployed."
        )

    return InferenceClient(token=token)


def generate_text(prompt, max_tokens=700, temperature=0.2):
    """
    Generate plain text response from Hugging Face Inference API.
    """
    model = get_model_name()
    client = get_client()

    response = client.chat_completion(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        max_tokens=max_tokens,
        temperature=temperature,
    )

    message = response.choices[0].message

    if isinstance(message, dict):
        return message.get("content", "").strip()

    return message.content.strip()


def _remove_markdown_fences(text: str) -> str:
    """Strip Markdown code fences and preserve enclosed JSON."""
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
                return text[start:index + 1]

    raise ValueError("No balanced JSON object found in the text.")


def _repair_trailing_commas(json_text: str) -> str:
    """Remove trailing commas from JSON objects and arrays."""
    return re.sub(r",\s*(?=[}\]])", "", json_text)


def extract_json_from_text(text: str) -> dict:
    """
    Extract the first JSON object from an LLM response.

    Handles:
    - Markdown code fences
    - Extra explanatory text
    - Trailing commas
    - Multiple JSON blocks (uses first balanced object)
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
            "Extracted JSON must be an object (dictionary)."
        )

    return parsed


def generate_json(prompt, max_tokens=700, temperature=0.1):
    """
    Generate and parse JSON response from the LLM.
    """
    text = generate_text(
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=temperature,
    )

    print("RAW LLM RESPONSE:")
    print(text)

    result = extract_json_from_text(text)

    print("EXTRACTED JSON:")
    print(json.dumps(result, indent=2))

    return result