from __future__ import annotations

import io
import json
import urllib.error

import pytest

from openwiki import llm
from openwiki.llm import LLMNotConfigured, OpenAICompatClient, analyze_record, detect_provider, make_client

LLM_ENV = ["LLM_PROVIDER", "GEMINI_API_KEY", "OPENAI_API_KEY", "OPENAI_BASE_URL", "OPENAI_MODEL"]


@pytest.fixture
def clean_env(monkeypatch):
    for name in LLM_ENV:
        monkeypatch.delenv(name, raising=False)
    return monkeypatch


def test_detect_provider(clean_env):
    assert detect_provider() is None
    clean_env.setenv("OPENAI_BASE_URL", "http://localhost:11434/v1")
    assert detect_provider() == "openai"
    clean_env.setenv("GEMINI_API_KEY", "x")
    assert detect_provider() == "gemini"
    clean_env.setenv("LLM_PROVIDER", "openai")
    assert detect_provider() == "openai"


def test_make_client_explains_missing_config(clean_env):
    with pytest.raises(LLMNotConfigured, match="GEMINI_API_KEY"):
        make_client()
    clean_env.setenv("OPENAI_BASE_URL", "http://localhost:11434/v1")
    with pytest.raises(LLMNotConfigured, match="OPENAI_MODEL"):
        make_client()


def test_ollama_style_client_needs_no_key(clean_env):
    clean_env.setenv("OPENAI_BASE_URL", "http://localhost:11434/v1")
    clean_env.setenv("OPENAI_MODEL", "llama3.1")
    client = make_client()
    assert isinstance(client, OpenAICompatClient)
    assert client.api_key is None
    assert client.base_url == "http://localhost:11434/v1"


def test_openai_client_retries_without_json_mode(monkeypatch):
    client = OpenAICompatClient(model="m", base_url="http://local/v1")
    sent: list[dict] = []

    def fake_post(payload):
        sent.append(dict(payload))
        if "response_format" in payload:
            raise urllib.error.HTTPError("u", 400, "bad", {}, io.BytesIO(b"response_format unsupported"))
        return {"choices": [{"message": {"content": '{"summary": "ok"}'}}]}

    monkeypatch.setattr(client, "_post", fake_post)
    assert client.generate("hi", json_mode=True) == '{"summary": "ok"}'
    assert "response_format" in sent[0] and "response_format" not in sent[1]
    client.generate("again", json_mode=True)
    assert "response_format" not in sent[2]


def test_analyze_record_parses_fenced_json(monkeypatch):
    class Fake:
        provider = "fake"

        def generate(self, prompt, *, json_mode=False, temperature=0.2):
            assert "Transcript:" in prompt
            return '```json\n{"summary": "s", "tags": ["a"]}\n```'

    record = {"title": "T", "video_id": "v", "metadata": {}, "transcript": "body"}
    assert analyze_record(Fake(), record, 1000)["summary"] == "s"


def test_analyze_record_reports_provider_after_retries(monkeypatch):
    monkeypatch.setattr(llm.time, "sleep", lambda s: None)

    class Broken:
        provider = "openai"

        def generate(self, *a, **k):
            return "not json"

    with pytest.raises(ValueError, match="openai analysis failed"):
        analyze_record(Broken(), {"title": "T", "video_id": "v", "metadata": {}, "transcript": ""}, 10)


def test_gemini_default_model_is_not_retired(clean_env):
    clean_env.setenv("GEMINI_API_KEY", "x")
    client = make_client()
    assert client.model == llm.DEFAULT_GEMINI_MODEL
    assert make_client(lint=True).model == llm.DEFAULT_GEMINI_MODEL
    assert "2.5" not in llm.DEFAULT_GEMINI_MODEL
    json.dumps({"model": client.model})
