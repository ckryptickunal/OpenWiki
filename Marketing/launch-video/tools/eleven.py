"""ElevenLabs helper for the marketing films: narration, songs and sound effects.

Reads ELEVENLABS_API_KEY from the repo's .env.local (git-ignored) or the environment; never prints it.

  python3 eleven.py check                                   # is the key set and valid? lists a few voices
  python3 eleven.py voices                                  # all voices on the account (id, name, labels)
  python3 eleven.py tts   OUT.mp3 VOICE_ID "text" [--model eleven_v3] [--speed 1.0] [--stability 0.5]
  python3 eleven.py music OUT.mp3 "prompt" --seconds 30 [--instrumental] [--model music_v2_5]
  python3 eleven.py sfx   OUT.mp3 "description" --seconds 2
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

API = "https://api.elevenlabs.io"


def key() -> str:
    k = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not k:
        env = Path(__file__).resolve().parents[3] / ".env.local"
        if env.exists():
            for line in env.read_text().splitlines():
                if line.startswith("ELEVENLABS_API_KEY="):
                    k = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not k:
        sys.exit("ELEVENLABS_API_KEY is empty: paste it into .env.local (repo root) after ELEVENLABS_API_KEY=")
    return k


def call(method: str, path: str, body: dict | None = None) -> bytes:
    req = urllib.request.Request(API + path, method=method, data=json.dumps(body).encode() if body else None,
                                 headers={"xi-api-key": key(), "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        sys.exit(f"ElevenLabs {e.code}: {e.read().decode(errors='replace')[:500]}")


def save(out: str, data: bytes) -> None:
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_bytes(data)
    print(f"wrote {out} ({len(data):,} bytes)")


def main() -> None:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check")
    sub.add_parser("voices")
    t = sub.add_parser("tts")
    t.add_argument("out"); t.add_argument("voice"); t.add_argument("text")
    t.add_argument("--model", default="eleven_v3"); t.add_argument("--speed", type=float, default=1.0)
    t.add_argument("--stability", type=float, default=0.5)
    m = sub.add_parser("music")
    m.add_argument("out"); m.add_argument("prompt"); m.add_argument("--seconds", type=float, default=30)
    m.add_argument("--instrumental", action="store_true"); m.add_argument("--model", default="music_v2_5")
    s = sub.add_parser("sfx")
    s.add_argument("out"); s.add_argument("text"); s.add_argument("--seconds", type=float, default=2)
    a = p.parse_args()

    if a.cmd in ("check", "voices"):
        voices = json.loads(call("GET", "/v2/voices?page_size=100")).get("voices", [])
        if a.cmd == "check":
            print(f"key OK: {len(voices)} voices available, e.g. " + ", ".join(v["name"] for v in voices[:6]))
        else:
            for v in voices:
                print(v["voice_id"], v["name"], json.dumps(v.get("labels", {})))
    elif a.cmd == "tts":
        save(a.out, call("POST", f"/v1/text-to-speech/{a.voice}?output_format=mp3_44100_192", {
            "text": a.text, "model_id": a.model,
            "voice_settings": {"stability": a.stability, "similarity_boost": 0.75, "speed": a.speed}}))
    elif a.cmd == "music":
        save(a.out, call("POST", "/v1/music", {
            "prompt": a.prompt, "music_length_ms": int(a.seconds * 1000),
            "force_instrumental": a.instrumental, "model_id": a.model}))
    elif a.cmd == "sfx":
        save(a.out, call("POST", "/v1/sound-generation", {"text": a.text, "duration_seconds": a.seconds}))


if __name__ == "__main__":
    main()
