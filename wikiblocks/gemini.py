"""Gemini client used by wiki ingest.

There is no bundled offline model. Ingest without a key only works when the
caller supplies analysis JSON (`--analysis-file` or an `analyzer` callable).
"""

from __future__ import annotations

import json
import re
import time

from wikiblocks.env import env_value, require_env

DEFAULT_INGEST_MODEL = "gemini-3.1-flash-lite"
DEFAULT_LINT_MODEL = "gemini-2.5-flash"

ANALYZE_PROMPT = """
You maintain a markdown LLM wiki for transcripts and essays.

Return ONLY valid JSON. Do not include markdown fences.

Analyze this source and produce:
- concise source summary
- key ideas
- entities (people, companies, products, organizations)
- topics
- notable claims
- useful quotes
- tags

JSON schema:
{{
  "summary": "string",
  "key_ideas": ["string"],
  "entities": [
    {{"name": "string", "type": "person|company|product|organization|project|other", "description": "string", "importance": "string"}}
  ],
  "topics": [
    {{"name": "string", "summary": "string"}}
  ],
  "claims": [
    {{"claim": "string", "evidence": "string"}}
  ],
  "quotes": ["string"],
  "tags": ["string"]
}}

Metadata:
Title: {title}
Video ID: {video_id}
Channel: {channel}
Published: {published}
URL: {url}

Transcript:
{transcript}
"""


def extract_json(text: str) -> dict:
    """Parse the first JSON object from a model response. Same repairs as Founder Book ingest.py."""
    if not text or not text.strip():
        raise ValueError("Gemini returned empty response")

    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    start = cleaned.find("{")
    if start == -1:
        raise ValueError("Gemini response did not contain JSON object")

    decoder = json.JSONDecoder()
    try:
        obj, _ = decoder.raw_decode(cleaned, start)
        return obj
    except json.JSONDecodeError:
        pass

    end = cleaned.rfind("}")
    if end == -1:
        raise ValueError("No closing brace in Gemini response")
    raw = cleaned[start : end + 1]

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    repaired = re.sub(r",\s*([}\]])", r"\1", raw)
    repaired = repaired.replace("\n", "\\n")
    try:
        return json.loads(repaired)
    except json.JSONDecodeError:
        pass

    for i in range(len(raw) - 1, 0, -1):
        if raw[i] == "}":
            try:
                return json.loads(raw[: i + 1])
            except json.JSONDecodeError:
                continue
    raise ValueError("Could not parse Gemini JSON response")


def configure_gemini(*, lint: bool = False) -> dict:
    require_env("GEMINI_API_KEY", "wiki ingest (or lint --gemini)")
    from google import genai

    api_key = env_value("GEMINI_API_KEY")
    if lint:
        model_name = (
            env_value("GEMINI_MODEL_LINT")
            or env_value("GEMINI_MODEL")
            or DEFAULT_LINT_MODEL
        )
    else:
        model_name = env_value("GEMINI_MODEL") or DEFAULT_INGEST_MODEL
    return {"client": genai.Client(api_key=api_key), "model_name": model_name}


def analyze_record(gemini: dict, record: dict, max_chars: int) -> dict:
    from google.genai import types

    metadata = record["metadata"]
    prompt = ANALYZE_PROMPT.format(
        title=record["title"],
        video_id=record["video_id"],
        channel=metadata.get("channel", metadata.get("channel_title", "Unknown")),
        published=metadata.get("published", metadata.get("published_at", "Unknown")),
        url=metadata.get("url", ""),
        transcript=record["transcript"][:max_chars],
    )
    for attempt in range(3):
        try:
            response = gemini["client"].models.generate_content(
                model=gemini["model_name"],
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2 + (attempt * 0.1),
                    response_mime_type="application/json",
                ),
            )
        except Exception as api_err:
            if attempt == 2:
                raise ValueError(f"Gemini API error after 3 attempts: {api_err}") from api_err
            time.sleep(5 * (attempt + 1))
            continue
        try:
            return extract_json(response.text)
        except (ValueError, json.JSONDecodeError) as exc:
            if attempt == 2:
                raise ValueError(f"Failed to parse Gemini JSON after 3 attempts: {exc}") from exc
            time.sleep(3 * (attempt + 1))
    raise ValueError("Failed to analyze source")
