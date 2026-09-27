"""Render every text-footage shot the film uses (in parallel)."""
import subprocess, sys
F = "../certain-kind/footage/hd"
SHOTS = [("eyes4", 1.0, 3.9), ("eyes3", 3.0, 3.7), ("papers3", 2.0, 2.35), ("think0", 6.0, 3.8),
         ("stage2", 2.0, 2.0), ("flip3", 10.0, 1.9), ("write3", 2.0, 5.0)]
procs = [subprocess.Popen([sys.executable, "ascii.py", f"{F}/{c}.mp4", str(o), str(d), f"assets/shots/{i}-{c}.mp4", "--seed", str(i)])
         for i, (c, o, d) in enumerate(SHOTS)]
sys.exit(max(p.wait() for p in procs))
