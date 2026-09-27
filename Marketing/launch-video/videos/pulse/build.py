"""OpenWiki "Pulse": a 30-second cut on the Lyria instrumental.

Cuts land on the music's onsets (measured with librosa on assets/music.wav): the build
accelerates 0-7.67 s, the drop hits at 7.67 s, a 0.33 s silence at 23.67 s, the final hit at 24.0 s.
Footage: Pexels (free licence), graded to black and white by ffmpeg into assets/shots/.
Run: python3 build.py  (cuts the shots it is missing, then writes index.html)
"""
import os
import subprocess

FOOT = "../certain-kind/footage/hd"
END, HIT = 30.0, 24.0

# (start, end, clip, offset into the source) ; None clip = black
SHOTS = [
    (0.00, 1.00, "eyes4", 1.0), (1.00, 2.00, "eyes3", 3.0), (2.00, 3.34, "click3", 4.0),
    (3.34, 4.17, "scroll3", 3.0), (4.17, 4.67, "sticky4", 2.0), (4.67, 5.34, "papers3", 3.0),
    (5.34, 5.84, "think0", 8.0), (5.84, 6.34, "scroll5", 10.0), (6.34, 6.67, "papers4", 3.0),
    (6.67, 6.75, "eyes4", 5.0), (6.75, 6.83, "click3", 1.0), (6.83, 6.92, "papers3", 1.0), (6.92, 7.00, "think0", 3.0),
    (8.33, 9.00, "stage2", 2.0), (9.00, 9.67, "podcast0", 6.0), (9.67, 10.33, "flip3", 10.0),
    (10.33, 11.00, "flip1", 4.0), (11.00, 12.33, "write3", 2.0),
    (17.00, 18.00, "code5", 4.0), (18.00, 18.67, "type4", 6.0), (18.67, 20.33, "think4", 3.0),
    (20.33, 20.67, "city5", 2.0), (20.67, 21.00, "stage0", 3.0), (21.00, 21.33, "flip4", 3.0),
    (21.33, 21.67, "write4", 2.0), (21.67, 22.00, "eyes5", 5.0), (22.00, 22.33, "code2", 5.0),
    (22.33, 22.67, "podcast5", 4.0), (22.67, 23.00, "city4", 2.0),
    (23.00, 23.083, "eyes4", 7.0), (23.083, 23.167, "flip0", 3.0), (23.167, 23.25, "type5", 3.0), (23.25, 23.33, "think3", 3.0),
]
# (start, end, text, style) — "low": lower-left line, "slam": huge centre word, "mid": centre line
LINES = [
    (0.25, 1.95, "you watched it.", "low"), (2.05, 3.30, "you saved it.", "low"), (4.70, 7.00, "you lost it.", "low"),
    (7.67, 8.33, "OpenWiki.", "slam"),
    (8.40, 9.62, "every talk.", "low"), (10.00, 11.00, "every essay.", "low"), (11.33, 12.30, "every note.", "low"),
    (12.40, 13.95, "becomes a page.", "low"),
    (17.00, 18.62, "your AI reads it too.", "low"),
]
GRAPH_WORDS = [(15.00, "linked."), (16.00, "searchable."), (16.66, "yours.")]
KICKS = [2.0, 3.34, 4.17, 4.67, 5.34, 5.84, 7.67, 10.0, 11.33, 12.33, 15.0, 16.0, 17.0, 18.0, 20.33, 21.0, 23.0]
FLASHES = [7.67, 24.0]


def cut(i, clip, off, dur):
    out = f"assets/shots/{i:02d}-{clip}.mp4"
    if not os.path.exists(out):
        vf = ("scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=30,format=gray,"
              "eq=contrast=1.28:brightness=-0.035,vignette=PI/4.2,format=yuv420p")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(off), "-i", f"{FOOT}/{clip}.mp4", "-t", f"{dur + 0.12:.3f}",
                        "-an", "-vf", vf, "-c:v", "libx264", "-crf", "15", "-preset", "medium", out], check=True)
    return out


def main():
    os.makedirs("assets/shots", exist_ok=True)
    clips, script = [], []
    for i, (t0, t1, clip, off) in enumerate(SHOTS):
        src = cut(i, clip, off, t1 - t0)
        clips.append(f'        <video class="clip shot" id="v{i}" src="{src}" muted playsinline data-start="{t0}" '
                     f'data-duration="{round(t1 - t0, 3)}" data-track-index="{i % 2}"></video>')
        script.append(f'  drift(tl, "#v{i}", {t0}, {round(t1 - t0, 3)}, {1 if i % 2 else -1});')
    lines = []
    for k, (a, b, txt, style) in enumerate(LINES):
        lines.append(f'      <div class="line {style}" id="t{k}">{txt}</div>')
        script.append(f'  {"slam" if style == "slam" else "lineIn"}(tl, "#t{k}", {a}, {b});')
    words = " ".join(f'<span class="gw" id="gw{k}">{w}</span>' for k, (_, w) in enumerate(GRAPH_WORDS))
    for k, (a, _) in enumerate(GRAPH_WORDS):
        script.append(f'  wordIn(tl, "#gw{k}", {a});')
    for t in KICKS:
        script.append(f"  kick(tl, {t});")
    for t in FLASHES:
        script.append(f"  flash(tl, {t});")
    html = (TEMPLATE.replace("%CLIPS%", "\n".join(clips)).replace("%LINES%", "\n".join(lines))
            .replace("%WORDS%", words).replace("%SCRIPT%", "\n".join(script))
            .replace("%END%", str(END)).replace("%HIT%", str(HIT)))
    open("index.html", "w").write(html)
    print(f"wrote index.html: {len(SHOTS)} shots, {len(LINES)} lines")


TEMPLATE = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "src", "template.html")).read()

if __name__ == "__main__":
    main()
