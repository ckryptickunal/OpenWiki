"""Generate the website's photos with Gemini (Nano Banana Pro).

All images share one LOOK so the set reads as a single roll of film. Run:
    GEMINI_API_KEY=... python scripts/generate_images.py [name ...]
Outputs site/img/<name>.jpg (1500px wide, JPEG q82).
"""

from __future__ import annotations

import io
import os
import sys
from pathlib import Path

from google import genai
from google.genai import types
from PIL import Image

MODEL = "gemini-3-pro-image"
OUT = Path(__file__).resolve().parents[1] / "site" / "img"

LOOK = (
    "Candid 35mm film photograph, Kodak Portra 400, soft warm window light from the left, "
    "gentle film grain, slightly faded blacks, muted palette of cream, oat, walnut brown and "
    "a little dusty terracotta, shallow depth of field, calm and quiet, shot from a slightly "
    "high angle on a worn light-oak desk. No people, no faces, no readable text, no letters, "
    "no logos, no brand names, no watermarks, no screens showing interfaces."
)

SHOTS = {
    "youtube": "A small vintage cream-coloured portable CRT television on the desk, its screen glowing with a soft blurred image of a lecture hall, two unlabelled cassette tapes and a pair of wired headphones beside it.",
    "essays": "A neat stack of printed essay pages held with a brass binder clip, a sharpened pencil and a folded pair of reading glasses resting on top, a cup of black coffee at the edge of frame.",
    "notes": "An open hardcover notebook with dense handwritten notes rendered as illegible soft scribbles, a fountain pen lying across the page, a few loose index cards tucked in the back.",
    "wiki": "An open wooden library card-catalogue drawer full of index cards, several cards pulled up and connected to each other with thin red thread and small brass pins, like a hand-made web of ideas.",
    "providers": "A small beige vintage computer terminal with a dark screen showing only a soft green glow, a brass desk key on a leather tag and a coiled keyboard cable, cosy and minimal.",
    "obsidian": "A polished black obsidian stone resting on natural linen cloth next to a small stack of index cards tied with twine, the stone catching a soft highlight from the window.",
    "desk": "A wide overview of a tidy research desk: a cream vintage portable television, a stack of printed essays, an open handwritten notebook and a wooden card-catalogue drawer with cards linked by red thread, warm afternoon light.",
}


def generate(name: str, client: genai.Client) -> Path:
    prompt = f"{SHOTS[name]} {LOOK}"
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=types.ImageConfig(aspect_ratio="3:2"),
        ),
    )
    for part in response.candidates[0].content.parts:
        if part.inline_data and part.inline_data.data:
            image = Image.open(io.BytesIO(part.inline_data.data)).convert("RGB")
            image.thumbnail((1500, 1500))
            path = OUT / f"{name}.jpg"
            image.save(path, "JPEG", quality=82, optimize=True, progressive=True)
            return path
    raise RuntimeError(f"No image returned for {name}")


def main(names: list[str]) -> None:
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    OUT.mkdir(parents=True, exist_ok=True)
    for name in names or list(SHOTS):
        print(generate(name, client), flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
