"""Compose the social-share card (site/img/og.jpg, .github/social-preview.png).

Needs the open-source font files (Playwrite US Trad, Fraunces Italic, Inter) from
https://github.com/google/fonts in FONT_DIR:
    FONT_DIR=/path/to/fonts python scripts/build_og.py
"""

from __future__ import annotations

import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FONT_DIR = Path(os.environ.get("FONT_DIR", "fonts"))
SURFACE, HEADING, PRIMARY, SECONDARY = "#faf6f2", "#432818", "#73574a", "#9c8479"


def font(name: str, size: int, **axes) -> ImageFont.FreeTypeFont:
    face = ImageFont.truetype(str(FONT_DIR / name), size)
    if axes:
        names = {"Weight": "wght", "Optical size": "opsz", "Optical Size": "opsz", "Softness": "SOFT", "Wonky": "WONK"}
        values = []
        for axis in face.get_variation_axes():
            label = axis["name"].decode() if isinstance(axis["name"], bytes) else axis["name"]
            values.append(axes.get(names.get(label, label), axis["default"]))
        face.set_variation_by_axes(values)
    return face


def polaroid(photo: Image.Image, width: int, border: int, angle: float) -> Image.Image:
    photo = photo.copy()
    photo.thumbnail((width, width))
    card = Image.new("RGBA", (photo.width + border * 2, photo.height + border * 2), "white")
    card.paste(photo, (border, border))
    card = card.rotate(angle, resample=Image.BICUBIC, expand=True)
    shadow = Image.new("RGBA", (card.width + 60, card.height + 60), (0, 0, 0, 0))
    mask = card.split()[3].point(lambda a: int(a * 0.28))
    shadow.paste((40, 25, 15, 255), (30, 38), mask)
    shadow = shadow.filter(ImageFilter.GaussianBlur(14))
    shadow.alpha_composite(card, (30, 26))
    return shadow


def card(size: tuple[int, int]) -> Image.Image:
    w, h = size
    s = w / 1200
    canvas = Image.new("RGBA", size, SURFACE)
    draw = ImageDraw.Draw(canvas)

    desk = Image.open(ROOT / "site/img/desk.jpg").convert("RGB")
    wiki = Image.open(ROOT / "site/img/wiki.jpg").convert("RGB")
    back = polaroid(wiki, int(300 * s), int(12 * s), -7)
    front = polaroid(desk, int(470 * s), int(16 * s), 3.5)
    canvas.alpha_composite(back, (int(700 * s), int(40 * s)))
    canvas.alpha_composite(front, (int(630 * s), int(150 * s)))

    x = int(80 * s)
    draw.text((x, int(150 * s)), "openwiki", font=font("playwrite.ttf", int(64 * s)), fill=HEADING)
    title = font("fraunces-italic.ttf", int(46 * s), wght=560, opsz=72, SOFT=0, WONK=0)
    for i, line in enumerate(["YouTube, blogs & notes,", "filed into a linked", "Markdown wiki."]):
        draw.text((x, int((285 + i * 54) * s)), line, font=title, fill=HEADING)
    small = font("inter.ttf", int(20 * s), wght=450, opsz=14)
    draw.text((x, int(470 * s)), "Open source  ·  Obsidian-ready  ·  Runs offline", font=small, fill=PRIMARY)
    draw.text((x, int(540 * s)), "github.com/ckryptickunal/OpenWiki", font=font("inter.ttf", int(17 * s), wght=450, opsz=14), fill=SECONDARY)
    return canvas.convert("RGB")


if __name__ == "__main__":
    card((1200, 630)).save(ROOT / "site/img/og.jpg", "JPEG", quality=88, optimize=True)
    card((1280, 672)).crop((0, 16, 1280, 656)).save(ROOT / ".github/social-preview.png", optimize=True)
    print("wrote site/img/og.jpg and .github/social-preview.png")
