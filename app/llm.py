from __future__ import annotations

import json
import random
import time

from google import genai
from google.genai import types

from .config import settings


def _extract_json(text: str) -> dict:
    text = (text or "").strip()

    if text.startswith("```"):
        text = text.strip("`").strip()

        if text.lower().startswith("json"):
            text = text[4:].strip()

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise ValueError(
            f"Gemini did not return valid JSON.\n\n{text[:1000]}"
        )

    return json.loads(text[start : end + 1])


def generate_text(
    prompt: str,
    system: str = "",
    json_mode: bool = False,
) -> str:
    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Add it to .env and restart the app."
        )

    last_error: Exception | None = None

    for attempt in range(1, settings.max_retries + 1):
        client = None

        try:
            # Create a fresh SDK client for every attempt.
            # Keeping a strong local reference prevents the HTTP client
            # from being cleaned up while the request is still running.
            client = genai.Client(
                api_key=settings.gemini_api_key
            )

            config = types.GenerateContentConfig(
                system_instruction=system or None,
                temperature=0.2,
                response_mime_type=(
                    "application/json"
                    if json_mode
                    else "text/plain"
                ),
            )

            response = client.models.generate_content(
                model=settings.gemini_model,
                contents=prompt,
                config=config,
            )

            if not response.text:
                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            return response.text

        except Exception as exc:
            last_error = exc

            print(
                f"[Gemini] request failed "
                f"(attempt {attempt}/{settings.max_retries}): "
                f"{exc}"
            )

            if attempt >= settings.max_retries:
                break

            wait_seconds = (
                2 ** (attempt - 1)
                + random.uniform(0, 1)
            )

            print(
                f"[Gemini] retrying in "
                f"{wait_seconds:.1f}s..."
            )

            time.sleep(wait_seconds)

        finally:
            if client is not None:
                try:
                    client.close()
                except Exception:
                    pass

    raise RuntimeError(
        f"Gemini request failed after retries: {last_error}"
    ) from last_error


def generate_json(
    prompt: str,
    system: str = "",
) -> dict:
    text = generate_text(
        prompt=prompt,
        system=system,
        json_mode=True,
    )

    return _extract_json(text)