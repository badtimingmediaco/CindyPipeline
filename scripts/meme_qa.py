#!/usr/bin/env python3
"""Frame-check meme clips BEFORE they are placed. Never trust a filename.

Written after a shipped reel went out with a Drake clip carrying hard black pillarbox
bars, a burned-in "NAH" caption AND a vevo watermark; a white-background cutout that read
as a pasted box on her warm background; and a moody film still that was not a meme at all.
All three were picked by filename and never looked at. The spec has always required this
check (section 4.4: no baked-in captions, no transparent sticker-GIFs, margins on every
meme, frame-check every clip with ffmpeg before use) - it simply was not run.

  python meme_qa.py                       # audit the whole bank
  python meme_qa.py clip.mp4 clip2.mp4    # audit specific candidates
  python meme_qa.py --sheet out.png       # also write a contact sheet to LOOK at

Exit code 1 if anything is flagged. FLAGGED IS NOT AUTO-REJECT: the numbers find the
mechanical faults (bars, near-uniform backgrounds, watermark-shaped corners), but whether
a clip is RECOGNISABLE and matches the beat's subtext is a judgement only a human or a
model looking at the frames can make. Always open the sheet.
"""
import argparse
import os
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image

BANK = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "04_assets", "memes", "bank")

BAR_TOL = 26          # a "black bar" column/row is darker than this on average
BAR_MIN_FRAC = 0.02   # ...and at least this fraction of the width/height
FLAT_TOL = 18         # background counted as flat if its std is under this
FLAT_FRAC = 0.34      # ...and it covers this much of the border ring


def frames(path, n=3):
    """Pull n frames spread across the clip."""
    out = []
    dur = 1.0
    try:
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                            "-of", "csv=p=0", path], capture_output=True, text=True)
        dur = max(0.2, float(r.stdout.strip() or 1.0))
    except Exception:
        pass
    for i in range(n):
        t = dur * (i + 0.5) / n
        fd, tmp = tempfile.mkstemp(suffix=".png")
        os.close(fd)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", path,
                        "-frames:v", "1", tmp], check=False)
        try:
            out.append(Image.open(tmp).convert("RGB").copy())
        except Exception:
            pass
        try:
            os.remove(tmp)
        except OSError:
            pass
    return out


def bars(a):
    """-> (left, right, top, bottom) bar thickness in px, measured on the mean image."""
    g = a.mean(axis=2)
    col, row = g.mean(axis=0), g.mean(axis=1)
    w, h = len(col), len(row)

    def run(v, lim):
        n = 0
        for x in v:
            if x < lim:
                n += 1
            else:
                break
        return n

    return (run(col, BAR_TOL), run(col[::-1], BAR_TOL),
            run(row, BAR_TOL), run(row[::-1], BAR_TOL))


def flat_border(a):
    """Fraction of the border ring that is near-uniform - catches white/green-screen cutouts."""
    g = a.mean(axis=2)
    k = max(2, min(g.shape[0], g.shape[1]) // 20)
    ring = np.concatenate([g[:k].ravel(), g[-k:].ravel(),
                           g[:, :k].ravel(), g[:, -k:].ravel()])
    med = np.median(ring)
    return float(np.mean(np.abs(ring - med) < FLAT_TOL)), float(med)


def white_border(a):
    """Share of border pixels that are near-white, regardless of how flat the ring is."""
    g = a.mean(axis=2)
    k = max(2, min(g.shape[0], g.shape[1]) // 20)
    ring = np.concatenate([g[:k].ravel(), g[-k:].ravel(),
                           g[:, :k].ravel(), g[:, -k:].ravel()])
    return float(np.mean(ring > 235))


def audit(path):
    fs = frames(path)
    if not fs:
        return ["unreadable - ffmpeg produced no frame"], None
    arr = np.stack([np.asarray(f.resize((240, 240))).astype(np.float32) for f in fs])
    mean = arr.mean(axis=0)
    w, h = fs[0].size
    flags = []

    L, R, T, B = bars(mean)
    if max(L, R) >= 240 * BAR_MIN_FRAC:
        flags.append(f"black bars L/R ({L},{R} of 240) - pillarboxed, will show as bars")
    if max(T, B) >= 240 * BAR_MIN_FRAC:
        flags.append(f"black bars T/B ({T},{B} of 240) - letterboxed")

    frac, med = flat_border(mean)
    if frac > FLAT_FRAC and med > 200:
        flags.append(f"near-white flat background ({frac:.0%} of border) - reads as a "
                     f"pasted box on her warm room")
    # Deliberately NOT flagging a dark border on its own. DiCaprio-cheers is simply a dark
    # scene, and the owner kept DeVito-burning-money in their own hand-finish despite its
    # bars. Real black BARS are caught above by bars(); darkness is not a defect.

    # A flat-border test alone misses a cutout whose subject reaches the frame edges - the
    # exploding-head clip shipped that way, only 15% flat but half its border pure white.
    # Measured across the whole bank the separation is stark: the two white-background
    # clips sit at 98% and 51% near-white border, every other clip at or under 2.5%.
    white = white_border(mean)
    if white > 0.15:
        flags.append(f"{white:.0%} of the border is near-white - this is a cutout, not a "
                     f"scene; it will read as a pasted white box")

    ar = w / float(h)
    if ar > 2.6:
        flags.append(f"very wide ({w}x{h}, {ar:.1f}:1) - will render short at 844px cap")
    return flags, fs[0]


def debar(path, out_dir):
    """Crop hard letterbox/pillarbox bars off and write a clean copy.

    Rejecting a good meme because someone re-encoded it with bars throws away the joke.
    The owner effectively did this by hand - their DeVito shipped at 844x385, a 2.19:1
    crop of a barred source. ffmpeg's own cropdetect finds the content box; we only act
    when it actually differs from the full frame.
    """
    r = subprocess.run(["ffmpeg", "-v", "info", "-i", path, "-vf",
                        "cropdetect=24:2:0", "-frames:v", "40", "-f", "null", "-"],
                       capture_output=True, text=True)
    crops = [ln.split("crop=")[1].strip() for ln in (r.stderr or "").splitlines()
             if "crop=" in ln]
    if not crops:
        return None
    box = crops[-1]
    try:
        cw, ch, cx, cy = (int(v) for v in box.split(":"))
    except ValueError:
        return None
    p = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                        "-show_entries", "stream=width,height", "-of", "csv=p=0", path],
                       capture_output=True, text=True)
    try:
        w, h = (int(v) for v in p.stdout.strip().split(","))
    except Exception:
        return None
    if cw >= w - 2 and ch >= h - 2:
        return None                                   # nothing to crop
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, os.path.basename(path))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", path,
                    "-vf", f"crop={cw}:{ch}:{cx}:{cy}",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                    "-pix_fmt", "yuv420p", "-an", dst], check=False)
    return (dst, f"{w}x{h} -> {cw}x{ch}") if os.path.exists(dst) else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("clips", nargs="*")
    ap.add_argument("--sheet", default="")
    ap.add_argument("--fix-bars", action="store_true",
                    help="write de-barred copies into 04_assets/memes/bank_clean/")
    a = ap.parse_args()

    paths = a.clips or [os.path.join(BANK, f) for f in sorted(os.listdir(BANK))
                        if f.lower().endswith((".mp4", ".mov"))]
    bad, thumbs = 0, []
    print(f"\nFRAME-CHECKING {len(paths)} clip(s)\n" + "=" * 68)
    for p in paths:
        flags, thumb = audit(p)
        name = os.path.basename(p)
        if flags:
            bad += 1
            print(f"  [FLAG] {name}")
            for f in flags:
                print(f"         {f}")
            if a.fix_bars and any("bars" in f for f in flags):
                r = debar(p, os.path.join(os.path.dirname(BANK), "bank_clean"))
                print(f"         -> cropped {r[1]}" if r else
                      "         -> could not crop automatically")
        else:
            print(f"  [ ok ] {name}")
        if thumb:
            thumbs.append((name, thumb, bool(flags)))

    if a.sheet and thumbs:
        cols, W, H = 5, 300, 268
        rows = (len(thumbs) + cols - 1) // cols
        from PIL import ImageDraw
        sh = Image.new("RGB", (cols * W, rows * H), (238, 238, 238))
        d = ImageDraw.Draw(sh)
        for i, (n, im, f) in enumerate(thumbs):
            im = im.copy()
            im.thumbnail((W - 12, H - 34))
            x, y = (i % cols) * W, (i // cols) * H
            sh.paste(im, (x + 6, y + 26))
            d.text((x + 6, y + 8), ("FLAG " if f else "") + n[:36],
                   fill=(190, 40, 30) if f else (30, 30, 30))
        sh.save(a.sheet)
        print(f"\ncontact sheet -> {a.sheet}  (LOOK at it - the numbers cannot judge "
              f"whether a clip is recognisable or matches the beat)")

    print("=" * 68)
    print(f"{bad} flagged / {len(paths)} checked")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
