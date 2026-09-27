"""Render a video clip as text: every cell of a 160 x 54 grid is a character from the real wiki
page OpenWiki wrote (research/demo-0.3.0/source-page-dylan-field.md), lit by the footage's brightness.
Warm palette: dark ember -> amber -> paper. A soft glow is added by ffmpeg afterwards.

  python3 ascii.py SRC OFFSET DURATION OUT.mp4 [--seed N]
"""
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, CW, CH = 1920, 1080, 12, 20
COLS, ROWS = W // CW, H // CH  # 160 x 54
FONT = "../../assets/fonts/JetBrainsMono.ttf"
PAGE = "../../research/demo-0.3.0/source-page-dylan-field.md"


def glyph_masks(chars):
    font = ImageFont.truetype(FONT, 17)
    masks = {}
    for ch in set(chars):
        im = Image.new("L", (CW, CH), 0)
        ImageDraw.Draw(im).text((CW / 2, CH / 2 + 1), ch, font=font, fill=255, anchor="mm")
        masks[ch] = np.asarray(im, np.float32) / 255
    return masks


def text_grid(seed):
    body = open(PAGE).read().split("---", 2)[-1]
    import re
    body = re.sub(r"\(https?://[^)]*\)", "", body)                    # drop link targets
    body = re.sub(r"https?://\S+", "", body)
    body = re.sub(r"\[\[[^|\]]*\|([^\]]*)\]\]", r"\1", body)        # [[path|Name]] -> Name
    body = re.sub(r"`[^`]*`", "", body)
    words = " ".join(line.strip("#>-* ") for line in body.splitlines() if line.strip() and not line.startswith("- Video ID"))
    words = re.sub(r"\s+", " ", words)
    words = "".join(c if 32 <= ord(c) < 127 else " " for c in words)
    need = COLS * ROWS
    s = (words + " · ") * (need // len(words) + 2)
    start = (seed * 997) % len(words)
    return s[start:start + need]


def palette(v):
    """0..1 brightness -> RGB: ember #3a2410 -> amber #f5c451 -> paper #faf6f2."""
    ember, amber, paper = np.array([58, 36, 16]), np.array([245, 196, 81]), np.array([250, 246, 242])
    v = v[..., None]
    lo = ember + (amber - ember) * np.clip(v / 0.7, 0, 1)
    return np.where(v < 0.7, lo, amber + (paper - amber) * np.clip((v - 0.7) / 0.3, 0, 1)) / 255


def main():
    src, off, dur, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
    seed = int(sys.argv[sys.argv.index("--seed") + 1]) if "--seed" in sys.argv else 0
    chars = text_grid(seed)
    masks = glyph_masks(chars)
    M = np.stack([masks[c] for c in chars]).reshape(ROWS, COLS, CH, CW)
    # one pipe of 480 x 270 grey frames: averaged down to the 160 x 54 grid for the glyphs, and
    # upscaled into a soft amber under-image so the picture reads through the letters
    rd = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", str(off), "-i", src, "-t", str(dur),
                           "-vf", "fps=30,scale=480:270:flags=area,gblur=sigma=1.2,format=gray", "-f", "rawvideo", "-"],
                          stdout=subprocess.PIPE)
    amber = np.array([245, 196, 81], np.float32) / 255
    wr = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
                           "-filter_complex", "[0]format=gbrp,split[a][b];[b]gblur=sigma=7[g];[a][g]blend=all_mode=screen:all_opacity=0.55,format=yuv420p",
                           "-c:v", "libx264", "-crf", "16", "-preset", "medium", out], stdin=subprocess.PIPE)
    n = 0
    while True:
        buf = rd.stdout.read(480 * 270)
        if len(buf) < 480 * 270:
            break
        big = np.frombuffer(buf, np.uint8).reshape(270, 480).astype(np.float32) / 255
        lo, hi = np.percentile(big, 4), np.percentile(big, 99.5)
        big = np.clip((big - lo) / max(hi - lo, 0.05), 0, 1)   # auto levels per frame
        v = big[:ROWS * 5:5, :COLS * 3:3] if False else big.reshape(54, 5, 160, 3).mean(axis=(1, 3))
        v = np.clip((v - 0.1) / 0.85, 0, 1) ** 0.85
        col = palette(v)                                      # ROWS, COLS, 3
        img = M[..., None] * v[..., None, None, None] * col[:, :, None, None, :]
        img = img.transpose(0, 2, 1, 3, 4).reshape(H, W, 3)
        bg = np.array([21, 16, 12], np.float32) / 255
        under = np.repeat(np.repeat(big, 4, axis=0), 4, axis=1)[..., None] ** 1.6 * amber * 0.30
        frame = np.clip(bg + under + img * (1 - bg), 0, 1)
        wr.stdin.write((frame * 255).astype(np.uint8).tobytes())
        n += 1
    wr.stdin.close(); wr.wait(); rd.wait()
    print(f"{out}: {n} frames")


if __name__ == "__main__":
    main()
