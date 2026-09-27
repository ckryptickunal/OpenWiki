"""Blurred, darkened footage that runs behind the spec cards, so the film never leaves the people."""
import subprocess
from concurrent.futures import ThreadPoolExecutor

# name, source clip, in-point (s), length (s)
BACKDROPS = [("bg_speed", "train", 5.0, 3.6), ("bg_graph", "board2", 0.5, 3.1), ("bg_search", "coder", 8.0, 2.8),
             ("bg_ask", "lamp", 2.0, 2.9), ("bg_cost", "lamp2", 12.0, 4.1), ("bg_zero", "reader", 6.0, 3.9)]
VF = ("scale=480:270,gblur=sigma=9,scale=1920:1080:flags=bicubic,fps=30,"
      "eq=brightness=-0.06:contrast=0.9:saturation=0.8,colorchannelmixer=rr=0.34:gg=0.32:bb=0.30,format=yuv420p")


def cut(b):
    name, src, t, d = b
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", f"footage/hd/{src}.mp4", "-t", str(d), "-an", "-vf", VF,
                    "-c:v", "libx264", "-crf", "18", "-preset", "medium", f"assets/shots/{name}.mp4"], check=True)
    return name


if __name__ == "__main__":
    with ThreadPoolExecutor(6) as ex:
        print(list(ex.map(cut, BACKDROPS)))
