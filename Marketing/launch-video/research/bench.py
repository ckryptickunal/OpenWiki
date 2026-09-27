"""Measure OpenWiki 0.3.x speed and cost on real videos, for the commercial's numbers.

Runs the real CLI in-process on a fresh workspace, with the Gemini client wrapped to record
wall time and the token counts Gemini reports (usage_metadata). Writes bench.json.

  set -a; . ../../../.env.local; set +a
  uv run --no-project --with-editable ../../.. python bench.py WORKDIR
"""
import json
import sys
import time
from pathlib import Path

from openwiki import cli, llm

VIDEOS = ["-7Qz7tSTfUU", "wr6PMD06hP0", "0LNQxT9LvM0", "12D8zEdOPYo", "1D2j8nTjOZ4"]
PRICE_IN, PRICE_OUT = 0.25, 1.50  # USD per 1M tokens, Gemini 3.1 Flash-Lite standard (ai.google.dev/gemini-api/docs/pricing, 2026-09-28)

calls = []
_orig = llm.GeminiClient.generate


def generate(self, prompt, *, json_mode=False, temperature=0.2):
    from google import genai
    from google.genai import types

    if self._client is None:
        self._client = genai.Client(api_key=self.api_key)
    config = types.GenerateContentConfig(
        temperature=temperature,
        response_mime_type="application/json" if json_mode else None,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )
    t = time.perf_counter()
    r = self._client.models.generate_content(model=self.model, contents=prompt, config=config)
    u = r.usage_metadata
    calls.append({"model": self.model, "s": time.perf_counter() - t, "in": u.prompt_token_count or 0,
                  "out": (u.candidates_token_count or 0) + (u.thoughts_token_count or 0)})
    return r.text or ""


llm.GeminiClient.generate = generate


def timed(argv):
    t = time.perf_counter()
    code = cli.main(argv)
    return time.perf_counter() - t, code


def main():
    root = Path(sys.argv[1]).resolve()
    root.mkdir(parents=True, exist_ok=True)
    out = {"videos": []}
    cli.main(["init", "--root", str(root)]) if not (root / "sources.json").exists() else None
    for vid in VIDEOS:
        s_fetch, _ = timed(["youtube", f"https://www.youtube.com/watch?v={vid}", "--folder", "Y Combinator", "--root", str(root)])
        n0 = len(calls)
        s_ingest, _ = timed(["ingest", "--all", "--root", str(root)])
        c = calls[n0:]
        tin, tout = sum(x["in"] for x in c), sum(x["out"] for x in c)
        row = {"id": vid, "fetch_s": round(s_fetch, 2), "ingest_s": round(s_ingest, 2), "llm_calls": len(c),
               "tokens_in": tin, "tokens_out": tout, "usd": round(tin / 1e6 * PRICE_IN + tout / 1e6 * PRICE_OUT, 5)}
        src = next((root / "raw").rglob(f"{vid}.txt"), None) if (root / "raw").exists() else None
        if src is None:
            src = next(root.rglob(f"{vid}.txt"), None)
        if src:
            head = src.read_text()[:600]
            row["duration"] = next((l.split(":", 1)[1].strip() for l in head.splitlines() if l.startswith("Duration")), None)
        print(row, flush=True)
        out["videos"].append(row)
    for q in ["warm network", "design is the differentiator", "default alive"]:
        t = time.perf_counter(); cli.main(["search", q, "--root", str(root)]); out.setdefault("search_s", []).append(round(time.perf_counter() - t, 3))
    n0 = len(calls)
    s_ask, _ = timed(["ask", "Who should I email first when I start selling?", "--root", str(root)])
    out["ask"] = {"s": round(s_ask, 2), "calls": calls[n0:]}
    Path("bench.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
