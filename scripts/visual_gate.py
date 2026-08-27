#!/usr/bin/env python3
"""THE VISUAL GATE. Render what the viewer will actually see, then check it.

Why this exists: `verify_build.py` reads JSON and every defect that ever shipped was in
PIXELS. A title whose text overflowed its torn-paper graphic and spilled a giant word
across the frame; two logos at the same scale rendering different sizes; annotation
stickers scribbled over the wrong part of a card; a meme with a burned-in caption. Every
one of those PASSED verification, because the JSON was correct.

This composites V1 + media + TEXT (real fonts, real sizes, real transforms) at full
1080x1920 for every moment an asset starts, runs automated pixel checks, and writes a
contact sheet that a human or model must LOOK at before the draft is handed over.

  python visual_gate.py <draft_dir> --out sheet.png

Exit 1 if any automated check fails. A clean exit is NOT permission to skip looking -
relevance, legibility and taste are not measurable here.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import measure          # noqa: E402

CW, CH = 1080, 1920
# Fail INSIDE the real frame edge. The width model is an estimate even after the stroke
# and paper corrections, so the gate is deliberately stricter than the canvas: a false
# alarm costs a look, a false pass costs a revision round.
MARGIN = 25
# ONE definition of each measurement constant and helper, imported - not a second copy.
# Two copies of a measured value is how they come to disagree: preview_composite.py had
# its own width constant, drew title boxes 3x too wide, and reported phantom collisions.
K_PLAIN = measure.K_PLAIN
K_TPL = measure.K_TPL


def load(draft):
    p = os.path.join(draft, "template-2.tmp")
    if not os.path.exists(p):
        p = os.path.join(draft, "draft_content.json")
    return json.load(open(p, encoding="utf-8"))


def frame_at(video, t):
    fd, tmp = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", video,
                    "-frames:v", "1", tmp], check=False)
    try:
        im = Image.open(tmp).convert("RGB").resize((CW, CH))
    except Exception:
        im = Image.new("RGB", (CW, CH), (40, 40, 40))
    try:
        os.remove(tmp)
    except OSError:
        pass
    return im


def text_items(d):
    """Every text layer with its resolved font, string, and rendered box."""
    M = d["materials"]
    tx = {t["id"]: t for t in M.get("texts", [])}
    tt = {t["id"]: t for t in M.get("text_templates", [])}
    out = []
    for tr in d["tracks"]:
        if tr["type"] != "text":
            continue
        for s in tr["segments"]:
            mid = s["material_id"]
            mat, is_tpl = tx.get(mid), False
            if mat is None and mid in tt:
                mat = tx.get(tt[mid]["text_info_resources"][0]["text_material_id"])
                is_tpl = True
            if mat is None:
                continue
            try:
                c = json.loads(mat["content"])
                body, st = c["text"], (c.get("styles") or [{}])[0]
            except Exception:
                continue
            size = st.get("size", 15)
            fpath = (st.get("font") or {}).get("path", "")
            sc = s["clip"]["scale"]["x"]
            tf = s["clip"]["transform"]
            a = s["target_timerange"]["start"] / 1e6
            b = a + s["target_timerange"]["duration"] / 1e6
            k = K_PLAIN * (K_TPL if is_tpl else 1.0)
            wpx = hpx = 0
            if fpath and os.path.exists(fpath):
                f = ImageFont.truetype(fpath, 100)
                lines = body.split("\n")
                bb = [f.getbbox(l) for l in lines]
                hpx = sum((x[3] - x[1]) for x in bb) / 100.0 * size * k * sc * 1.25
                # What the VIEWER sees, not what the glyphs measure. See measure.py:
                # the stroke, the shadow and the paper graphic are all real width.
                if is_tpl:
                    ai = tt[mid]["text_info_resources"][0].get("attach_info") or {}
                    wpx = measure.paper_label_width_px(ai, sc)
                    if not wpx:
                        wpx = measure.rendered_width_px(fpath, body, size, sc, True)
                else:
                    wpx = measure.rendered_width_px(fpath, body, size, sc, False)
            out.append(dict(track=tr.get("name") or "", t=(a, b), text=body, tpl=is_tpl,
                            font=fpath, size=size, scale=sc, x=tf["x"], y=tf["y"],
                            w=wpx, h=hpx))
    return out


sticker_art = measure.sticker_art
ink_box = measure.ink_box


def sticker_items(d):
    mats = {m["id"]: m for m in d["materials"].get("stickers", [])}
    out = []
    for tr in d["tracks"]:
        if tr["type"] != "sticker":
            continue
        for s in tr["segments"]:
            m = mats.get(s["material_id"])
            if not m:
                continue
            a = s["target_timerange"]["start"] / 1e6
            b = a + s["target_timerange"]["duration"] / 1e6
            out.append(dict(t=(a, b), rid=m.get("resource_id"),
                            scale=s["clip"]["scale"]["x"],
                            x=s["clip"]["transform"]["x"], y=s["clip"]["transform"]["y"]))
    return out


def draw_text(img, it):
    """Draw the string at its real size and position, plus its box."""
    d = ImageDraw.Draw(img)
    cx = CW / 2 + it["x"] * CW / 2
    cy = CH / 2 - it["y"] * CH / 2
    x0, y0 = cx - it["w"] / 2, cy - it["h"] / 2
    if it["font"] and os.path.exists(it["font"]) and it["w"] > 0:
        px = max(8, int(it["h"] / max(1, len(it["text"].split("\n"))) * 0.78))
        try:
            f = ImageFont.truetype(it["font"], px)
            d.multiline_text((cx, cy), it["text"], font=f, fill=(255, 255, 255),
                             anchor="mm", align="center",
                             stroke_width=max(2, px // 14), stroke_fill=(0, 0, 0))
        except Exception:
            pass
    d.rectangle([x0, y0, x0 + it["w"], y0 + it["h"]], outline=(255, 90, 60), width=3)
    return (x0, y0, x0 + it["w"], y0 + it["h"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("draft")
    ap.add_argument("--out", default="gate.png")
    ap.add_argument("--cols", type=int, default=5)
    ap.add_argument("--every", type=int, default=0,
                    help="render every N frames instead of only asset starts; "
                         "--every 15 is a frame every half second")
    ap.add_argument("--tile", type=int, default=330)
    a = ap.parse_args()

    d = load(a.draft)
    vids = {v["id"]: v for v in d["materials"].get("videos", [])}
    v1 = None
    media = []
    for tr in d["tracks"]:
        if tr["type"] != "video":
            continue
        for s in tr["segments"]:
            m = vids.get(s["material_id"])
            if not m:
                continue
            aa = s["target_timerange"]["start"] / 1e6
            bb = aa + s["target_timerange"]["duration"] / 1e6
            if (tr.get("name") or "") == "V1":
                v1 = m.get("path")
            else:
                media.append((aa, bb, m, s))
    texts = text_items(d)
    stickers = sticker_items(d)

    if a.every:
        # Round 5: rendering only the moments an asset STARTS missed every defect that
        # appeared mid-asset. This walks the whole video on a fixed stride instead.
        step = a.every / 30.0
        dur = (d.get("duration") or 0) / 1e6 or 60.0
        n = int(dur / step) + 1
        moments = [round(i * step, 2) for i in range(n)]
    else:
        moments = sorted({round(x[0], 2) for x in [i["t"] for i in texts]}
                         | {round(m[0], 2) for m in media}
                         | {round(s2["t"][0], 2) for s2 in stickers})
    fails = []

    tiles = []
    # Sample HALF A FRAME INTO each moment, not exactly on it.
    #
    # Moments are rounded to 2dp, so an asset starting at 5.033 was probed at 5.03 - three
    # milliseconds BEFORE it exists. The gate was rendering the frame preceding several
    # assets and reporting them clean without ever having drawn them. The same rounding
    # made two assets appear together at a butt-join, because floating point put one
    # segment's end at 25.700000000000003.
    probe = lambda t: t + 1.0 / 60.0

    for t in moments:
        img = frame_at(v1, t + 0.05) if v1 else Image.new("RGB", (CW, CH), (40, 40, 40))
        for (aa, bb, m, s) in media:
            if not (aa <= probe(t) < bb):
                continue
            p = m.get("path")
            if not p or not os.path.exists(p):
                continue
            src = p
            if p.lower().endswith((".mp4", ".mov")):
                off = min(max(0.0, probe(t) - aa), max(0.0, bb - aa - 0.05))
                fd, tmp = tempfile.mkstemp(suffix=".png")
                os.close(fd)
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{off:.2f}",
                                "-i", p, "-frames:v", "1", tmp], check=False)
                src = tmp
            try:
                ov = Image.open(src).convert("RGBA")
            except Exception:
                continue
            w, h = m["width"], m["height"]
            fit = min(CW / w, CH / h)
            sc = s["clip"]["scale"]["x"]
            dw, dh = max(1, int(w * fit * sc)), max(1, int(h * fit * sc))
            ov = ov.resize((dw, dh))
            px = int(CW / 2 + s["clip"]["transform"]["x"] * CW / 2 - dw / 2)
            py = int(CH / 2 - s["clip"]["transform"]["y"] * CH / 2 - dh / 2)
            img.paste(ov, (px, py), ov)
            if src != p:
                try:
                    os.remove(src)
                except OSError:
                    pass

        for st in stickers:
            if not (st["t"][0] <= probe(t) < st["t"][1]):
                continue
            art = sticker_art(st["rid"])
            if art is None:
                fails.append(f"t={t:5.2f} sticker {st['rid']} has no cached artwork - "
                             f"cannot be checked visually")
                continue
            w, h = art.size
            fit = min(CW / w, CH / h)
            dw = max(1, int(w * fit * st["scale"]))
            dh = max(1, int(h * fit * st["scale"]))
            px = int(CW / 2 + st["x"] * CW / 2 - dw / 2)
            py = int(CH / 2 - st["y"] * CH / 2 - dh / 2)
            img.paste(art.resize((dw, dh)), (px, py), art.resize((dw, dh)))

        boxes = []
        for it in texts:
            if not (it["t"][0] <= probe(t) < it["t"][1]):
                continue
            box = draw_text(img, it)
            boxes.append((it, box))
            if box[0] < MARGIN or box[2] > CW - MARGIN:
                fails.append(f"t={t:5.2f} OFF-FRAME horizontally: {it['text']!r} "
                             f"spans {box[0]:.0f}..{box[2]:.0f} of {CW} "
                             f"(safe area {MARGIN}..{CW - MARGIN})")
            if box[1] < 0 or box[3] > CH:
                fails.append(f"t={t:5.2f} OFF-FRAME vertically: {it['text']!r}")
        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                (ia, ba), (ib, bbx) = boxes[i], boxes[j]
                ox = min(ba[2], bbx[2]) - max(ba[0], bbx[0])
                oy = min(ba[3], bbx[3]) - max(ba[1], bbx[1])
                if ox > 12 and oy > 12:
                    fails.append(f"t={t:5.2f} TEXT OVERLAP: {ia['text']!r} x {ib['text']!r} "
                                 f"({ox:.0f}x{oy:.0f}px)")
        img.thumbnail((a.tile, a.tile * 1920 // 1080))
        tiles.append((t, img))

    cols = a.cols
    W, H = tiles[0][1].width + 8, tiles[0][1].height + 26
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * W, rows * H), (22, 22, 22))
    dr = ImageDraw.Draw(sheet)
    for i, (t, im) in enumerate(tiles):
        x, y = (i % cols) * W, (i // cols) * H
        sheet.paste(im, (x + 4, y + 22))
        dr.text((x + 6, y + 6), f"t={t}", fill=(255, 205, 165))
    sheet.save(a.out)

    print(f"\nVISUAL GATE - {len(moments)} moments rendered -> {a.out}")
    print("=" * 68)
    seen = set()
    for f in fails:
        if f not in seen:
            seen.add(f)
            print("  [FAIL] " + f)
    print("=" * 68)
    print(f"{len(seen)} pixel failure(s). LOOK AT THE SHEET - relevance and legibility "
          f"are not checkable here.")
    return 1 if seen else 0


if __name__ == "__main__":
    sys.exit(main())
