"""LLM clients used by ingest and `lint --review`.

Two providers:
- `gemini`: Google Gemini via `google-genai` (`GEMINI_API_KEY`).
- `openai`: any OpenAI-compatible Chat Completions API — OpenAI, OpenRouter,
  Groq, Together, or a local server such as Ollama or LM Studio
  (`OPENAI_BASE_URL`, `OPENAI_MODEL`, optional `OPENAI_API_KEY`).

`LLM_PROVIDER` picks one explicitly; otherwise the first configured provider wins.
Without any provider, ingest only works with precomputed analysis JSON.
"""

from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any

from openwiki.env import env_value

DEFAULT_GEMINI_MODEL = "gemini-3.1-flash-lite"
DEFAULT_OPENAI_BASE_URL = "https://api.openai.com/v1"
PROVIDERS = ("gemini", "openai")

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


class LLMNotConfigured(RuntimeError):
    pass


def extract_json(text: str) -> dict:
    """Parse the first JSON object from a model response, repairing common slips."""
    if not text or not text.strip():
        raise ValueError("LLM returned an empty response")

    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    start = cleaned.find("{")
    if start == -1:
        raise ValueError("LLM response did not contain a JSON object")

    decoder = json.JSONDecoder()
    try:
        obj, _ = decoder.raw_decode(cleaned, start)
        return obj
    except json.JSONDecodeError:
        pass

    end = cleaned.rfind("}")
    if end == -1:
        raise ValueError("No closing brace in LLM response")
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
    raise ValueError("Could not parse JSON from the LLM response")


def detect_provider() -> str | None:
    explicit = (env_value("LLM_PROVIDER") or "").lower()
    if explicit:
        if explicit not in PROVIDERS:
            raise LLMNotConfigured(f"LLM_PROVIDER must be one of {', '.join(PROVIDERS)}, got {explicit!r}")
        return explicit
    if env_value("GEMINI_API_KEY"):
        return "gemini"
    if env_value("OPENAI_API_KEY") or env_value("OPENAI_BASE_URL"):
        return "openai"
    return None


@dataclass
class GeminiClient:
    model: str
    api_key: str
    provider: str = "gemini"
    _client: Any = field(default=None, repr=False)

    def generate(self, prompt: str, *, json_mode: bool = False, temperature: float = 0.2) -> str:
        from google import genai
        from google.genai import types

        if self._client is None:
            self._client = genai.Client(api_key=self.api_key)
        config = types.GenerateContentConfig(
            temperature=temperature,
            response_mime_type="application/json" if json_mode else None,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        )
        response = self._client.models.generate_content(model=self.model, contents=prompt, config=config)
        return response.text or ""


@dataclass
class OpenAICompatClient:
    model: str
    base_url: str
    api_key: str | None = None
    timeout: int = 600
    provider: str = "openai"
    _json_mode_supported: bool = True

    def _post(self, payload: dict) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        req = urllib.request.Request(
            self.base_url.rstrip("/") + "/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def generate(self, prompt: str, *, json_mode: bool = False, temperature: float = 0.2) -> str:
        payload: dict = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
        }
        if json_mode and self._json_mode_supported:
            payload["response_format"] = {"type": "json_object"}
        try:
            data = self._post(payload)
        except urllib.error.HTTPError as exc:
            # Some local servers reject response_format; retry once without it.
            if exc.code == 400 and "response_format" in payload:
                self._json_mode_supported = False
                payload.pop("response_format")
                data = self._post(payload)
            else:
                detail = exc.read().decode("utf-8", errors="replace")[:300]
                raise RuntimeError(f"HTTP {exc.code} from {self.base_url}: {detail}") from exc
        return data["choices"][0]["message"].get("content") or ""


def make_client(*, provider: str | None = None, lint: bool = False):
    """Build the configured LLM client. Raises LLMNotConfigured with a fix-it message."""
    provider = (provider or detect_provider() or "").lower()
    if not provider:
        raise LLMNotConfigured(
            "No LLM configured. Set GEMINI_API_KEY, or OPENAI_BASE_URL + OPENAI_MODEL "
            "(OpenAI, OpenRouter, Ollama, LM Studio...), or pass --analysis-file."
        )
    if provider == "gemini":
        api_key = env_value("GEMINI_API_KEY")
        if not api_key:
            raise LLMNotConfigured("Set GEMINI_API_KEY to use the Gemini provider.")
        model = (lint and env_value("GEMINI_MODEL_LINT")) or env_value("GEMINI_MODEL") or DEFAULT_GEMINI_MODEL
        return GeminiClient(model=model, api_key=api_key)
    if provider == "openai":
        model = (lint and env_value("OPENAI_MODEL_LINT")) or env_value("OPENAI_MODEL")
        if not model:
            raise LLMNotConfigured(
                "Set OPENAI_MODEL (e.g. the model name your OpenAI-compatible server serves)."
            )
        return OpenAICompatClient(
            model=model,
            base_url=env_value("OPENAI_BASE_URL") or DEFAULT_OPENAI_BASE_URL,
            api_key=env_value("OPENAI_API_KEY"),
        )
    raise LLMNotConfigured(f"Unknown provider {provider!r}. Use one of: {', '.join(PROVIDERS)}")


def analyze_record(client, record: dict, max_chars: int) -> dict:
    metadata = record["metadata"]
    prompt = ANALYZE_PROMPT.format(
        title=record["title"],
        video_id=record["video_id"],
        channel=metadata.get("channel", metadata.get("channel_title", "Unknown")),
        published=metadata.get("published", metadata.get("published_at", "Unknown")),
        url=metadata.get("url") or metadata.get("source", ""),
        transcript=record["transcript"][:max_chars],
    )
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            text = client.generate(prompt, json_mode=True, temperature=0.2 + attempt * 0.1)
        except Exception as exc:
            last_error = exc
            if attempt < 2:
                time.sleep(5 * (attempt + 1))
            continue
        try:
            return extract_json(text)
        except ValueError as exc:
            last_error = exc
    raise ValueError(f"{client.provider} analysis failed after 3 attempts: {last_error}")
