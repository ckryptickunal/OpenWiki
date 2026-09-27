"""Cut and grade the commercial's footage shots from footage/hd (Pexels, free licence; see footage/clips.txt)."""
import subprocess
from concurrent.futures import ThreadPoolExecutor

# name, source clip, in-point (s), length (s)
SHOTS = [
    ("paint", "paint", 0.5, 2.1), ("code", "code", 1.0, 2.1), ("train", "train", 2.0, 2.3), ("coder", "coder", 0.5, 2.3),
    ("solder", "solder", 4.0, 2.1), ("sketch", "sketch", 1.5, 0.5), ("producer", "producer", 0.5, 0.5), ("board", "board", 9.0, 0.5),
    ("sculpt", "sculpt", 5.0, 0.5), ("print", "print", 4.0, 0.5), ("window", "window", 4.0, 2.7),
    ("artist", "artist", 3.0, 1.1), ("womancode", "womancode", 2.0, 1.1), ("engineer", "engineer", 7.0, 1.1), ("geek", "geek", 12.0, 1.1),
    ("sculpt2", "sculpt2", 1.5, 1.1), ("reader", "reader", 3.0, 1.4),
    ("m_film", "film", 6.0, 0.6), ("m_arch", "arch", 5.0, 0.6), ("m_keys", "keys", 2.0, 0.6), ("m_producer2", "producer2", 4.0, 0.6),
    ("m_board2", "board2", 3.0, 0.6), ("m_print2", "print2", 5.0, 0.6), ("m_lamp", "lamp", 15.0, 0.6), ("m_lamp2", "lamp2", 7.0, 0.6),
    ("m_scope2", "scope2", 2.0, 0.6), ("m_robot2", "robot2", 7.0, 0.6), ("m_scope", "scope", 2.0, 0.8),
]
GRADE = ("scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=30,"
         "eq=contrast=1.07:saturation=0.88:gamma=0.97,"
         "curves=master='0/0.02 0.25/0.21 0.5/0.5 0.75/0.79 1/0.98',format=yuv420p")


def cut(s):
    name, src, t, d = s
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", f"footage/hd/{src}.mp4", "-t", str(d), "-an",
                    "-vf", GRADE, "-c:v", "libx264", "-crf", "15", "-preset", "medium", f"assets/shots/{name}.mp4"], check=True)
    return name


if __name__ == "__main__":
    import os
    os.makedirs("assets/shots", exist_ok=True)
    with ThreadPoolExecutor(6) as ex:
        print(list(ex.map(cut, SHOTS)))
