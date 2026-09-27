"""Check a rendered video by decoding it. Adapted from product-film (MIT, Rieranthony).

    uv run --with numpy --with imageio-ffmpeg python3 scripts/verify.py out/v1/launch.mp4 \
        --duration 20 --bg 10,10,10 [--poster out/v1/poster.jpg] [--loop] [--probe 9.4:944,800]

- duration matches (to the frame)
- the file has an audio stream (skip with --silent)
- frame 0 matches the poster (when --poster is given): the thumbnail is the settled frame
- otherwise frame 0 at the corner decodes to the background (within 6: x264 chroma costs ~5 on saturated colors; the range bug is 13+): catches the
  limited/full color range bug that turns #0a0a0a into #171717
- --loop: the last frame equals frame 0 (only for a landing-page loop)
- each probe (seconds:x,y) prints its decoded color
Exits non-zero when a check fails.
"""

import argparse
import re
import subprocess
import sys

import imageio_ffmpeg
import numpy as np

FF = imageio_ffmpeg.get_ffmpeg_exe()


def info(path):
    return subprocess.run([FF, "-hide_banner", "-i", path], capture_output=True, text=True).stderr


def frame(path, index, width, height):
    raw = subprocess.run(
        [FF, "-v", "error", "-i", path, "-vf", f"select=eq(n\\,{index})", "-frames:v", "1",
         "-s", f"{width}x{height}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        capture_output=True,
    ).stdout
    return np.frombuffer(raw, np.uint8).reshape(height, width, 3).astype(int)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("video")
    parser.add_argument("--duration", type=float, required=True)
    parser.add_argument("--bg", default=None, help="r,g,b of the background at frame 0's corner")
    parser.add_argument("--poster")
    parser.add_argument("--loop", action="store_true")
    parser.add_argument("--silent", action="store_true")
    parser.add_argument("--probe", action="append", default=[])
    args = parser.parse_args()

    meta = info(args.video)
    h, m, s = meta.split("Duration: ")[1].split(",")[0].split(":")
    dur = int(h) * 3600 + int(m) * 60 + float(s)
    video_line = next(l for l in meta.splitlines() if "Video:" in l)
    width, height = (int(v) for v in re.search(r" (\d{2,5})x(\d{2,5})", video_line).groups())
    fps = float(re.search(r"([\d.]+) fps", video_line).group(1))
    failed = False

    def report(ok, text):
        nonlocal failed
        failed |= not ok
        print(("ok   " if ok else "FAIL ") + text)

    report(abs(dur - args.duration) < 1.5 / fps, f"duration {dur:.3f}s (target {args.duration:g}s)")
    if not args.silent:
        report("Audio:" in meta, "audio stream present")
    first = frame(args.video, 0, width, height)
    if args.poster:
        poster = frame(args.poster, 0, width, height)
        diff = np.abs(first - poster).mean()
        report(diff < 6, f"frame 0 matches poster (mean diff {diff:.1f})")
    if args.bg:
        bg = np.array([int(v) for v in args.bg.split(",")])
        corner = first[8, 8]
        report(bool(np.all(np.abs(corner - bg) <= 6)), f"frame 0 corner {corner.tolist()} vs bg {bg.tolist()} (off = color range bug)")
    if args.loop:
        end = frame(args.video, round(args.duration * fps) - 1, width, height)
        diff = np.abs(first - end).max(axis=2)
        report(int((diff > 3).sum()) < 0.001 * width * height, f"loop seam: {int((diff > 3).sum())}px differ")
    for probe in args.probe:
        when, point = probe.split(":")
        x, y = (int(v) for v in point.split(","))
        print(f"     probe {probe}: {frame(args.video, round(float(when) * fps), width, height)[y, x].tolist()}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
