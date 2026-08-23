#!/usr/bin/env python3
"""Approximate visual preview of a draft - composites overlays onto V1 frames.

WHY THIS EXISTS: `capcut render` only flattens the main video track and mixes
audio; it does NOT composite overlays. In the first social-media-research build
every scripted check in verify_build.py passed while the exported video had memes
buried across her face - because nothing ever LOOKED at a composited frame.

This is not a pixel-accurate renderer. It places video overlays exactly (position,
scale, fit-to-canvas) and draws text layers as labelled boxes at their true
bounding boxes, which is enough to catch geometry mistakes before export.

Usage: python preview_composite.py <draft_dir> <out.png> [t1 t2 t3 ...]
"""
import json, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont

CANVAS = (1080, 1920)


def load(draft):
    p = os.path.join(draft, "template-2.tmp")
    if not os.path.exists(p):
        p = os.path.join(draft, "draft_content.json")
    return json.load(open(p, encoding="utf-8"))


IMG_EXT = (".png", ".jpg", ".jpeg", ".webp", ".bmp")


def frame_at(path, t, tmp, tag):
    # stills have no timeline to seek into - ffmpeg -ss past frame 0 returns
    # nothing, which silently drops every PNG overlay from the sheet.
    if path.lower().endswith(IMG_EXT):
        return path
    out = os.path.join(tmp, f"{tag}.png")
    subprocess.run(["ffmpeg", "-v", "error", "-ss", str(max(t, 0)), "-i", path,
                    "-frames:v", "1", "-y", out], check=False)
    return out if os.path.exists(out) else None


def place(canvas_img, overlay_img, transform, scale, src_wh):
    w, h = src_wh
    fit = min(CANVAS[0] / w, CANVAS[1] / h)
    dw, dh = int(w * fit * scale), int(h * fit * scale)
    if dw <= 0 or dh <= 0:
        return
    ov = overlay_img.resize((dw, dh))
    cx = CANVAS[0] / 2 + transform.get("x", 0) * (CANVAS[0] / 2)
    cy = CANVAS[1] / 2 - transform.get("y", 0) * (CANVAS[1] / 2)   # +y is UP
    pos = (int(cx - dw / 2), int(cy - dh / 2))
    canvas_img.paste(ov, pos, ov if ov.mode == "RGBA" else None)


def text_box(draw, seg, tt, tx, label, color):
    """Draw a text layer's true bounding box + its text."""
    cl = seg.get("clip") or {}
    tr = cl.get("transform") or {"x": 0, "y": 0}
    sc = (cl.get("scale") or {"x": 1})["x"]
    hit = [r for r in [seg["material_id"]] + list(seg.get("extra_material_refs", [])) if r in tt]
    if hit:
        ai = tt[hit[0]]["text_info_resources"][0]["attach_info"]
        csc = (ai.get("clip") or {}).get("scale", {}).get("x", 1)
        w, h = ai["original_size_width"] * csc * sc, ai["original_size_height"] * csc * sc
    else:
        # PLAIN text: measure the material's real font with PIL and convert to render
        # px with the calibrated constant (K0 = 4.39 render-px per PIL-unit x size,
        # derived from the template's own paper layers). The old 700x200 guess drew
        # boxes 3x too wide and made the title look like it was colliding.
        w, h = 700 * sc, 200 * sc
        try:
            j = json.loads(tx[seg["material_id"]]["content"])
            st = j["styles"][0]
            fnt = ImageFont.truetype(st["font"]["path"], 100)
            size = st.get("size", 15)
            lines = j["text"].splitlines() or [j["text"]]
            pw = max(fnt.getbbox(l)[2] - fnt.getbbox(l)[0] for l in lines) / 100.0
            w = pw * size * 4.39 * sc
            h = 1.35 * size * 4.39 * sc * len(lines)
        except Exception:
            pass
    cx = CANVAS[0] / 2 + tr["x"] * (CANVAS[0] / 2)
    cy = CANVAS[1] / 2 - tr["y"] * (CANVAS[1] / 2)
    box = [cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2]
    draw.rectangle(box, outline=color, width=5)
    try:
        f = ImageFont.truetype("arial.ttf", 40)
    except Exception:
        f = ImageFont.load_default()
    draw.text((box[0] + 8, box[1] + 6), label[:34], fill=color, font=f)


def build(draft, out_png, times):
    d = load(draft)
    M = d["materials"]
    vids = {v["id"]: v for v in M.get("videos", [])}
    tx = {t["id"]: t for t in M["texts"]}
    tt = {t["id"]: t for t in M.get("text_templates", [])}
    tracks = d["tracks"]
    v1 = tracks[0]["segments"][0]
    v1path = vids[v1["material_id"]]["path"]
    if not os.path.exists(v1path):
        cand = os.path.join(draft, "assets", "video", os.path.basename(v1path))
        if os.path.exists(cand):
            v1path = cand

    tmp = tempfile.mkdtemp()
    panels = []
    for t in times:
        base_p = frame_at(v1path, t, tmp, f"v1_{t}")
        canvas = Image.open(base_p).convert("RGB").resize(CANVAS) if base_p else Image.new("RGB", CANVAS, "black")
        draw = ImageDraw.Draw(canvas)
        for tr_i, track in enumerate(tracks):
            nm = track.get("name", "")
            if track["type"] == "audio" or nm in ("V1",) or track["type"] == "adjust":
                continue
            for s in track["segments"]:
                st = s["target_timerange"]["start"] / 1e6
                en = st + s["target_timerange"]["duration"] / 1e6
                if not (st <= t < en):
                    continue
                cl = s.get("clip") or {}
                sc = (cl.get("scale") or {"x": 1})["x"]
                trf = cl.get("transform") or {"x": 0, "y": 0}
                if s["material_id"] in vids:
                    v = vids[s["material_id"]]
                    p = v["path"]
                    if not os.path.exists(p):
                        c2 = os.path.join(draft, "assets", "video", os.path.basename(p))
                        p = c2 if os.path.exists(c2) else None
                    if not p:
                        continue
                    local_t = (t - st) + s.get("source_timerange", {}).get("start", 0) / 1e6
                    fp = frame_at(p, local_t, tmp, f"ov_{tr_i}_{t}")
                    if fp:
                        try:
                            ov = Image.open(fp)
                            if ov.mode in ("RGBA", "LA", "P"):
                                ov = ov.convert("RGBA")      # keep PNG transparency
                            else:
                                ov = ov.convert("RGB")
                            place(canvas, ov, trf, sc, (v["width"], v["height"]))
                        except Exception:
                            pass
                else:
                    label = nm or "text"
                    col = {"captions": "#39d0ff", "placeholders": "#ffd23f"}.get(nm, "#ff5cf0")
                    hit = [r for r in [s["material_id"]] + list(s.get("extra_material_refs", []))
                           if r in tt]
                    if hit:
                        cid = tt[hit[0]]["text_info_resources"][0]["text_material_id"]
                        if cid in tx:
                            try:
                                label = json.loads(tx[cid]["content"])["text"].replace("\n", " ")
                            except Exception:
                                pass
                    else:
                        for r in [s["material_id"]] + list(s.get("extra_material_refs", [])):
                            if r in tx:
                                try:
                                    label = json.loads(tx[r]["content"])["text"].replace("\n", " ")
                                except Exception:
                                    pass
                    text_box(draw, s, tt, tx, label, col)
        canvas.thumbnail((330, 590))
        panels.append((t, canvas))

    cols = min(5, len(panels))
    rows = (len(panels) + cols - 1) // cols
    CW, CH = 340, 620
    sheet = Image.new("RGB", (CW * cols, CH * rows), "white")
    sd = ImageDraw.Draw(sheet)
    for i, (t, im) in enumerate(panels):
        x, y = (i % cols) * CW, (i // cols) * CH
        sheet.paste(im, (x + 5, y + 24))
        sd.text((x + 8, y + 8), f"t={t}s", fill="black")
    sheet.save(out_png)
    return out_png


if __name__ == "__main__":
    draft, out = sys.argv[1], sys.argv[2]
    times = [float(x) for x in sys.argv[3:]] or [1.5, 7.5, 11.5, 14.5, 23.5, 31.0, 34.0, 42.5, 45.5]
    print(build(draft, out, times))
