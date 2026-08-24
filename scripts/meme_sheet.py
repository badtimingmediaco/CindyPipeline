#!/usr/bin/env python3
"""Render every bank clip as 3 frames on one sheet, so the bank can be curated by EYE.

A burned-caption detector was attempted and did not work - it scored a clip with no text
above a clip with a full caption, because it was measuring cartoon linework. Rather than
ship a check that lies, the bank is small enough (37 clips) to look at once and record the
verdict permanently in `_state/meme_catalog.json`.

  python meme_sheet.py --out sheet.png --batch 0     # first half
  python meme_sheet.py --out sheet.png --batch 1     # second half
"""
import argparse
import os
import subprocess
import tempfile

from PIL import Image, ImageDraw

BANK = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "04_assets", "memes", "bank")
COLS = 3          # frames per clip
TW, TH = 300, 200


def frames(path, n=COLS):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", path], capture_output=True, text=True)
    try:
        dur = max(0.2, float(r.stdout.strip()))
    except Exception:
        dur = 1.0
    out = []
    for i in range(n):
        fd, tmp = tempfile.mkstemp(suffix=".png")
        os.close(fd)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{dur*(i+0.5)/n:.2f}",
                        "-i", path, "-frames:v", "1", tmp], check=False)
        try:
            im = Image.open(tmp).convert("RGB")
            im.thumbnail((TW, TH))
            out.append(im)
        except Exception:
            pass
        try:
            os.remove(tmp)
        except OSError:
            pass
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--batch", type=int, default=-1)
    ap.add_argument("--per-batch", type=int, default=19)
    a = ap.parse_args()

    names = sorted(f for f in os.listdir(BANK) if f.endswith(".mp4"))
    if a.batch >= 0:
        names = names[a.batch * a.per_batch:(a.batch + 1) * a.per_batch]

    rowh = TH + 26
    sheet = Image.new("RGB", (COLS * (TW + 6) + 6, len(names) * rowh + 6), (242, 242, 242))
    d = ImageDraw.Draw(sheet)
    for r, n in enumerate(names):
        y = 6 + r * rowh
        d.text((8, y), n[:-4], fill=(15, 15, 15))
        for c, im in enumerate(frames(os.path.join(BANK, n))):
            sheet.paste(im, (6 + c * (TW + 6), y + 18))
    sheet.save(a.out)
    print(f"{len(names)} clips -> {a.out}  {sheet.size}")


if __name__ == "__main__":
    main()
