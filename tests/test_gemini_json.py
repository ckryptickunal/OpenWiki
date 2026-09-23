from wikiblocks.gemini import extract_json


def test_extract_json_from_fenced_block():
    raw = '```json\n{"summary": "ok", "tags": ["a"]}\n```'
    assert extract_json(raw)["summary"] == "ok"


def test_extract_json_trailing_data_and_commas():
    raw = '{"summary": "ok", "tags": ["a"],}\nThanks!'
    assert extract_json(raw)["summary"] == "ok"


def test_extract_json_rejects_empty():
    try:
        extract_json("   ")
    except ValueError as exc:
        assert "empty" in str(exc).lower()
    else:
        raise AssertionError("expected ValueError")
