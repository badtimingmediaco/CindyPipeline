# -*- coding: utf-8 -*-
"""Cloning CapCut materials. Every trap CapCut sets around text templates lives here.

The rules encoded below were each learned by shipping the bug:

  * NEVER `apply-template`: it stamps one shared child into every copy, so the last graft
    wins everywhere and sixteen different stickers all read the same phrase.
  * Fresh ids at EVERY level - segment, template, child, and each extra_material_ref.
  * A text_template carries its OWN attach_info duration, independent of its segment. If
    that is shorter the text vanishes partway through while its box stays on the timeline:
    the recurring "ghost layer".
  * Style ranges are absolute character offsets. Clamping them to a LONGER replacement
    leaves the tail unstyled and CapCut renders it at a giant default size.
"""
import copy
import json
import os
import uuid

from . import measure

U = lambda: str(uuid.uuid4()).upper()


def new_track(name, ttype, segs):
    return {"attribute": 0, "flag": 0, "id": U(), "is_default_name": False,
            "name": name, "segments": segs, "type": ttype}


def lanes(items):
    """Pack segments into the fewest non-overlapping tracks.

    Two segments that overlap in time on ONE track are silently serialised by CapCut - a
    dashboard slid 2.10 -> 3.30 while its label stayed put, and nothing reported it.
    """
    key = lambda s: (s["target_timerange"]["start"],
                     s["target_timerange"]["start"] + s["target_timerange"]["duration"])
    out = []
    for s in sorted(items, key=lambda x: x["target_timerange"]["start"]):
        a, _ = key(s)
        for ln in out:
            if key(ln[-1])[1] <= a:
                ln.append(s)
                break
        else:
            out.append([s])
    return out


def set_text(mat, new):
    """Replace a text material's string AND make its style ranges cover it.

    CLAMPING is wrong when the new string is LONGER: replacing "into" (4 chars) with
    "catch" (5) left range [0,4], so the final "h" had no style and rendered at a giant
    default size splashed across the frame.
    """
    try:
        c = json.loads(mat["content"])
        c["text"] = new
        styles = c.get("styles") or []
        for st in styles:
            rng = st.get("range")
            if rng:
                rng[0] = max(0, min(rng[0], len(new)))
                rng[1] = max(rng[0], min(rng[1], len(new)))
        if styles:
            if styles[0].get("range"):
                styles[0]["range"][0] = 0
            if styles[-1].get("range"):
                styles[-1]["range"][1] = len(new)      # never leave a tail unstyled
        mat["content"] = json.dumps(c, ensure_ascii=False)
    except Exception:
        mat["content"] = new


def sync_attach(tpl, seg):
    """Make a text_template's INTERNAL duration match its segment. See the ghost layer."""
    dur = seg["target_timerange"]["duration"]
    n = 0
    for r in tpl.get("text_info_resources", []):
        ai = r.get("attach_info")
        if ai and (ai.get("duration") != dur or ai.get("start_time") != 0):
            ai["start_time"] = 0
            ai["duration"] = dur
            n += 1
    return n


def ghost_sweep(d):
    """Re-sync EVERY text_template against its segment, unconditionally, as the last
    structural act of a build.

    Not a repair for a known-bad case - a sweep. Segment durations are frame-quantised
    and attach values are not, so even a freshly cloned label drifts by a frame. On the
    Claude Reviewer build all 32 template segments were mismatched.
    """
    tt = {x["id"]: x for x in d["materials"].get("text_templates", [])}
    n = 0
    for tr in d["tracks"]:
        for s in tr["segments"]:
            tpl = tt.get(s["material_id"])
            if tpl:
                n += sync_attach(tpl, s)
    return n


def find_donors(d, donor_cache, donor_phrase="Make money", shadow_text="how to make"):
    """The sample paper sticker (style donor) + the title row carrying the drop shadow.

    The donor SEGMENT is deleted at the end of the first build (it is the template's own
    sample and must not ship), so it is cached to disk and reloaded on every later run.
    Its MATERIALS stay in the draft either way - nothing is ever pruned here, because
    pruning eats grafted template children.
    """
    M = d["materials"]
    tx = {t["id"]: t for t in M["texts"]}
    tt = {t["id"]: t for t in M.get("text_templates", [])}
    donor_tpl = None
    for tid, tpl in tt.items():
        ch = tx.get(tpl["text_info_resources"][0]["text_material_id"])
        try:
            if ch and donor_phrase in json.loads(ch["content"])["text"]:
                donor_tpl = tid
        except Exception:
            pass
    sticker = None
    for t in d["tracks"]:
        for s in t["segments"]:
            refs = [s["material_id"]] + list(s.get("extra_material_refs", []))
            if donor_tpl and donor_tpl in refs:
                sticker = (s, donor_tpl)
    if sticker is None and os.path.exists(donor_cache) and donor_tpl:
        sticker = (json.load(open(donor_cache, encoding="utf-8")), donor_tpl)
    elif sticker is not None:
        json.dump(sticker[0], open(donor_cache, "w", encoding="utf-8"), ensure_ascii=False)
    # The shadow donor is whichever title row carries the drop shadow, and it is found by
    # that PROPERTY, not by its words. Matching a hardcoded string ("how to make") tied the
    # engine to one video's title: the next reel retitled that row and the build died with
    # "donor missing: shadow=False". A donor is defined by what it HAS, not what it says.
    shadow = None
    if shadow_text:
        for _mid, m in tx.items():
            try:
                if json.loads(m["content"]).get("text") == shadow_text:
                    shadow = m
            except Exception:
                pass
    if shadow is None:
        child_ids = {t["text_info_resources"][0]["text_material_id"] for t in tt.values()}
        for _mid, m in tx.items():
            if m["id"] in child_ids or not m.get("has_shadow"):
                continue
            try:
                if json.loads(m["content"]).get("text", "").strip():
                    shadow = m
                    break
            except Exception:
                pass
    if sticker is None or shadow is None:
        raise SystemExit("donor missing: sticker=%s shadow=%s"
                         % (sticker is not None, shadow is not None))
    return sticker, shadow


def gc_text_materials(d, keep_ids):
    """Drop text materials no segment references any more.

    Walks the REAL reference chain - segment -> text_template -> text_info_resources[0]
    .text_material_id plus its extra refs - so a grafted child is never mistaken for an
    orphan the way `capcut prune` does. An earlier version collected the live donor
    template and the next run died.
    """
    M = d["materials"]
    tt = {t["id"]: t for t in M.get("text_templates", [])}
    live = set(keep_ids)
    for t in d["tracks"]:
        for s in t["segments"]:
            for r in [s["material_id"]] + list(s.get("extra_material_refs", [])):
                live.add(r)
    for tid in list(live):
        tpl = tt.get(tid)
        if tpl:
            for tir in tpl.get("text_info_resources", []):
                live.add(tir.get("text_material_id"))
                live.update(tir.get("extra_material_refs", []))
    dropped = 0
    for bucket in ("texts", "text_templates"):
        before = len(M.get(bucket, []))
        M[bucket] = [m for m in M.get(bucket, []) if m["id"] in live]
        dropped += before - len(M[bucket])
    return dropped


def clone_sticker(d, donor_seg, donor_tpl_id, text, t_in, t_out, x, y, scale=0.37):
    """Deep-clone the paper donor with fresh ids at every level. -> (segment, width_px)"""
    M = d["materials"]
    bucket_of = {}
    for bname, arr in M.items():
        if isinstance(arr, list):
            for it in arr:
                if isinstance(it, dict) and "id" in it:
                    bucket_of[it["id"]] = bname

    def clone_mat(mid):
        b = bucket_of.get(mid)
        if not b:
            return None
        src = next(x2 for x2 in M[b] if x2.get("id") == mid)
        new = copy.deepcopy(src)
        new["id"] = U()
        M[b].append(new)
        bucket_of[new["id"]] = b
        return new

    tx = {t["id"]: t for t in M["texts"]}
    tt = {t["id"]: t for t in M["text_templates"]}
    seg = copy.deepcopy(donor_seg)
    seg["id"] = U()
    ntpl = clone_mat(donor_tpl_id)
    donor_child = tt[donor_tpl_id]["text_info_resources"][0]["text_material_id"]
    nchild = clone_mat(donor_child)
    tir = ntpl["text_info_resources"][0]
    tir["id"] = U()
    tir["text_material_id"] = nchild["id"]
    tir["extra_material_refs"] = [(clone_mat(r) or {}).get("id", r)
                                  for r in tir.get("extra_material_refs", [])]
    cj = json.loads(nchild["content"])
    old = cj["text"]
    fp = cj["styles"][0]["font"]["path"]
    wo, wn = measure.pil_units(fp, old), measure.pil_units(fp, text)
    set_text(nchild, text)
    tir["attach_info"]["original_size_width"] *= (wn / wo if wo else 1)
    tir["attach_info"]["start_time"] = 0
    tir["attach_info"]["duration"] = int((t_out - t_in) * 1e6)
    for k in ("origin_word_info", "current_word_info"):
        ntpl[k] = {"text": text, "start_time": 0, "end_time": 0,
                   "words": [], "keyword_ranges": []}
    seg["material_id"] = ntpl["id"]
    seg["extra_material_refs"] = [(clone_mat(r) or {}).get("id", r)
                                  for r in donor_seg.get("extra_material_refs", [])]
    seg["target_timerange"] = {"start": int(t_in * 1e6),
                               "duration": int((t_out - t_in) * 1e6)}
    seg["source_timerange"] = {"start": 0, "duration": int((t_out - t_in) * 1e6)}
    seg["clip"]["transform"] = {"x": x, "y": y}
    seg["clip"]["scale"] = {"x": scale, "y": scale}
    seg["visible"] = True
    seg.setdefault("uniform_scale", {})["on"] = True
    seg["common_keyframes"] = []
    ai = tir["attach_info"]
    w_px = ai["original_size_width"] * (ai.get("clip") or {}).get("scale", {}).get("x", 1) * scale
    return seg, w_px


def clone_shadow_label(d, shadow_mat, donor_seg, text, t_in, t_out, x, y,
                       size=12, scale=1.0):
    """Plain label carrying the TITLE's exact drop shadow. -> (segment, width_px)"""
    M = d["materials"]
    new = copy.deepcopy(shadow_mat)
    new["id"] = U()
    j = json.loads(new["content"])
    j["text"] = text
    for st in j["styles"]:
        st["range"] = [0, len(text)]
        st["size"] = size
    new["content"] = json.dumps(j, ensure_ascii=False)
    M["texts"].append(new)
    seg = copy.deepcopy(donor_seg)
    seg["id"] = U()
    seg["material_id"] = new["id"]
    seg["extra_material_refs"] = []
    seg["target_timerange"] = {"start": int(t_in * 1e6),
                               "duration": int((t_out - t_in) * 1e6)}
    seg["source_timerange"] = {"start": 0, "duration": int((t_out - t_in) * 1e6)}
    seg["clip"]["transform"] = {"x": x, "y": y}
    seg["clip"]["scale"] = {"x": scale, "y": scale}
    seg["visible"] = True
    seg.setdefault("uniform_scale", {})["on"] = True
    seg["common_keyframes"] = []
    w_px = measure.text_width_px(j["styles"][0]["font"]["path"], text, size, scale)
    return seg, w_px


def strip_overlays(d):
    """Idempotent: remove everything a build owns, so a rebuild never doubles up.

    Every video track except V1 goes - an overlay parked on an UNNAMED track survives a
    name-based strip and comes back as a duplicate arrow.
    """
    drop = lambda t: (t.get("name", "") or "").startswith(
        ("memes", "stickers", "logo_", "gfx", "sfx", "arrow", "text_", "annot"))
    kept, removed = [], 0
    for t in d["tracks"]:
        if t["type"] == "audio":
            removed += len(t["segments"])
            continue
        if t["type"] == "video" and t.get("name") != "V1":
            removed += len(t["segments"])
            continue
        if drop(t):
            removed += len(t["segments"])
            continue
        kept.append(t)
    d["tracks"] = kept
    return removed
