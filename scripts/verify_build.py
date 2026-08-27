#!/usr/bin/env python3
"""Section 7b failproof post-session verification - scripted assertions with printed
evidence. Run after EVERY CapCut open and every write session.

A reviewer must RUN this and read the printed evidence; a summary claim is not
evidence (a past reviewer printed "all ids unique - PASS" while every copy shared
one child, because it read the wrong field).

Usage: python verify_build.py <draft_dir> [--plan <plan.md>]
"""
import json, os, sys, subprocess, collections

LONGLIVED_S = 4.0      # a card held longer than this is worth a look
FAILS = []
def check(name, ok, evidence=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    if evidence:
        for line in str(evidence).splitlines():
            print(f"         {line}")
    if not ok:
        FAILS.append(name)
    return ok


def load(draft):
    p = os.path.join(draft, "template-2.tmp")
    if not os.path.exists(p):
        p = os.path.join(draft, "draft_content.json")
    return json.load(open(p, encoding="utf-8")), p


def bbox(seg, mat_dims):
    """Return (x0,x1,y0,y1) in half-canvas units for a visual segment."""
    cl = seg.get("clip") or {}
    tr = cl.get("transform") or {"x": 0, "y": 0}
    sc = (cl.get("scale") or {"x": 1, "y": 1})["x"]
    w, h = mat_dims
    if not w or not h:
        return None
    fit = min(1080.0 / w, 1920.0 / h)
    dw, dh = w * fit * sc, h * fit * sc
    hx, hy = (dw / 2) / 540.0, (dh / 2) / 960.0
    return (tr["x"] - hx, tr["x"] + hx, tr["y"] - hy, tr["y"] + hy)


def overlaps_time(a, b):
    return a[0] < b[1] and b[0] < a[1]


def main(draft):
    d, canon = load(draft)
    M = d["materials"]
    tx = {t["id"]: t for t in M["texts"]}
    tt = {t["id"]: t for t in M.get("text_templates", [])}
    vids = {v["id"]: v for v in M.get("videos", [])}
    auds = {a["id"]: a for a in M.get("audios", [])}
    tracks = d["tracks"]

    print(f"\n=== VERIFY {os.path.basename(draft)} (canonical: {os.path.basename(canon)}) ===\n")

    # ---- 1. paper texts resolve + zero duplicate ids -----------------------
    print("1. Paper/template texts - resolve + uniqueness")
    rows = []
    for ti, t in enumerate(tracks):
        for s in t["segments"]:
            hit = [r for r in [s["material_id"]] + list(s.get("extra_material_refs", [])) if r in tt]
            if not hit:
                continue
            m = tt[hit[0]]
            tir = m["text_info_resources"][0]
            cid = tir.get("text_material_id")
            txt = None
            if cid in tx:
                try:
                    txt = json.loads(tx[cid]["content"])["text"]
                except Exception:
                    txt = "<UNPARSEABLE>"
            rows.append((ti, s["id"], hit[0], tir["id"], cid, txt))
    ev = "\n".join(f"{r[0]:>3} seg={r[1][:8]} tir={r[3][:8]} child={(r[4] or '')[:8]} {r[5]!r}" for r in rows)
    check("every template child resolves and parses",
          all(r[5] not in (None, "<UNPARSEABLE>") for r in rows), ev)
    for label, idx in (("text_info_resources[0].id", 3), ("text_material_id", 4)):
        vals = [r[idx] for r in rows]
        dups = {k: v for k, v in collections.Counter(vals).items() if v > 1}
        check(f"no duplicate {label}", not dups,
              f"{len(vals)} total / {len(set(vals))} unique" + (f" DUPS={dups}" if dups else ""))
    # Repeated WORDING is fine and sometimes intended (e.g. "/research" said twice);
    # the bug this guards against is copies SHARING ONE CHILD, which the id checks
    # above already catch. Report repeats as information only.
    texts = [r[5] for r in rows]
    reps = {t: c for t, c in collections.Counter(texts).items() if c > 1}
    print(f"  [INFO] repeated wording (fine - ids are unique): {reps if reps else 'none'}")

    # ---- 2. track order + render index ------------------------------------
    print("\n2. Track order + track_render_index")
    order = [(i, t["type"], t.get("name", ""), len(t["segments"])) for i, t in enumerate(tracks)]
    check("V1 talking head at array index 0",
          tracks[0]["type"] == "video" and tracks[0].get("name") == "V1",
          "\n".join(f"{i}: {ty:6} {nm:12} {n:>3} segs" for i, ty, nm, n in order))
    check("adjust layer at array index 1", tracks[1]["type"] == "adjust")
    v1dur = tracks[0]["segments"][0]["target_timerange"]["duration"]
    adur = tracks[1]["segments"][0]["target_timerange"]["duration"]
    check("adjust duration == V1 duration", adur == v1dur, f"V1={v1dur} adjust={adur}")
    bad = [(i, s["id"][:8], s.get("track_render_index"))
           for i, t in enumerate(tracks) for s in t["segments"]
           if s.get("track_render_index") != i]
    check("every track_render_index == array index", not bad, f"offenders: {bad[:10]}")

    # ---- 5. SFX pairing + volumes -----------------------------------------
    print("\n5. SFX pairing + volume overrides")
    sfx = []
    for t in tracks:
        if t["type"] != "audio":
            continue
        for s in t["segments"]:
            a = auds.get(s["material_id"])
            sfx.append((s["target_timerange"]["start"] / 1e6,
                        os.path.basename(a.get("path", "")) if a else "?", s.get("volume", 1.0)))
    visual_starts = []
    for t in tracks:
        if t["type"] in ("audio", "adjust") or t.get("name") == "captions":
            continue
        for s in t["segments"]:
            visual_starts.append((s["target_timerange"]["start"] / 1e6, t.get("name", t["type"])))
    unpaired = [v for v in visual_starts if not any(abs(v[0] - x[0]) <= 0.15 for x in sfx)]
    check("every visual start has an SFX hit within +/-0.15s", not unpaired,
          f"{len(visual_starts)} visual starts, {len(sfx)} sfx; unpaired={unpaired[:8]}")
    succ = [(t, v) for t, f, v in sfx if f.lower().startswith("success")]
    check("every success.MP3 at 0.224 (-13 dB)",
          all(abs(v - 0.224) < 0.01 for _, v in succ), f"{succ}")
    # 2.512 (+8 dB) is the FLOOR, not the target. The owner has raised it by hand on every
    # build we have measured - 2.9688 on Claude SEO, 3.63 on GoHighLevel - so house_layout
    # carries 2.97 as the value to ship. Anything at or above the floor passes; below it
    # is the real defect, because a quiet VO is what actually gets noticed.
    v1vol = tracks[0]["segments"][0].get("volume")
    _FLOOR = 2.512
    check(f"V1 volume >= {_FLOOR} (+8 dB floor)", (v1vol or 0) >= _FLOOR - 0.01,
          f"volume={v1vol} (house_layout ships 2.97)")
    first = sorted(sfx)[0] if sfx else None
    check("first SFX is magic reveal at 0:00",
          bool(first) and first[0] == 0.0 and "magic reveal" in first[1].lower(), f"{first}")

    # ---- 6. collision sweep ------------------------------------------------
    print("\n6. Collision sweep (no two visual assets overlap in BOTH space and time)")
    assets = []
    for t in tracks:
        nm = t.get("name", "")
        # V1 and the adjust layer are the BACKGROUND, not collision participants;
        # captions are spec-locked to their own band.
        if t["type"] in ("audio", "adjust") or nm in ("captions", "V1"):
            continue
        for s in t["segments"]:
            w = h = None
            if s["material_id"] in vids:
                v = vids[s["material_id"]]
                w, h = v.get("width"), v.get("height")
            else:
                hit = [r for r in [s["material_id"]] + list(s.get("extra_material_refs", []))
                       if r in tt]
                if hit:
                    ai = tt[hit[0]]["text_info_resources"][0]["attach_info"]
                    csc = (ai.get("clip") or {}).get("scale", {}).get("x", 1)
                    w = ai["original_size_width"] * csc
                    h = ai["original_size_height"] * csc
                    cl = s.get("clip") or {}
                    sc = (cl.get("scale") or {"x": 1})["x"]
                    tr = (cl.get("transform") or {"x": 0, "y": 0})
                    hx, hy = (w * sc / 2) / 540.0, (h * sc / 2) / 960.0
                    assets.append((nm, s["id"][:8],
                                   (s["target_timerange"]["start"] / 1e6,
                                    (s["target_timerange"]["start"] + s["target_timerange"]["duration"]) / 1e6),
                                   (tr["x"] - hx, tr["x"] + hx, tr["y"] - hy, tr["y"] + hy)))
                    continue
            bb = bbox(s, (w, h))
            if bb:
                assets.append((nm, s["id"][:8],
                               (s["target_timerange"]["start"] / 1e6,
                                (s["target_timerange"]["start"] + s["target_timerange"]["duration"]) / 1e6),
                               bb))
    clashes = []
    for i in range(len(assets)):
        for j in range(i + 1, len(assets)):
            a, b = assets[i], assets[j]
            if not overlaps_time(a[2], b[2]):
                continue
            ax0, ax1, ay0, ay1 = a[3]
            bx0, bx1, by0, by1 = b[3]
            # SANCTIONED PAIR (owner's layout law): a meme and its own label
            # deliberately overlap - the label straddles the meme's bottom edge.
            # Recognise it by: one meme + one sticker sharing the same window.
            norm = lambda n: ("sticker" if n.startswith("stickers")
                              else "memes" if n.startswith("memes") else n)
            kinds = {norm(a[0]), norm(b[0])}
            same_window = (abs(a[2][0] - b[2][0]) < 0.05 and abs(a[2][1] - b[2][1]) < 0.05)
            if kinds == {"memes", "sticker"}:
                # the owner's pairing law: the label is CENTRED and straddles the meme's
                # bottom edge. Sanction it either when the two share one window (a meme
                # and its own label) or when the sticker sits exactly on that straddle
                # line (a card carrying several labels in sequence).
                meme, stick = (a, b) if norm(a[0]) == "memes" else (b, a)
                straddle = meme[3][2] + 0.023          # meme bottom + the law's offset
                centred = abs((stick[3][0] + stick[3][1]) / 2) < 0.02
                on_line = abs((stick[3][2] + stick[3][3]) / 2 - straddle) < 0.035
                if same_window or (centred and on_line):
                    continue
            # Touching is not colliding. The owner's own measured layout puts a centre
            # card's label bottom exactly ON the card's top edge (CARD_LABEL_GAP is the
            # label's half-height), and the logo row's paper header the same way, so the
            # boxes share a boundary by ~0.001-0.006 half-units - 1 to 6 pixels. Flagging
            # that as a clash reports the owner's own layout as broken. Require a real
            # overlap of >EPS on BOTH axes before calling it one.
            EPS = 0.012                                  # ~11px vertically, ~6px across
            ox = min(ax1, bx1) - max(ax0, bx0)
            oy = min(ay1, by1) - max(ay0, by0)
            if ox > EPS and oy > EPS:
                clashes.append(f"{a[0]}/{a[1]} {a[2]} {tuple(round(v,3) for v in a[3])}  X  "
                               f"{b[0]}/{b[1]} {b[2]} {tuple(round(v,3) for v in b[3])}")
    check("zero spatial intersections among time-overlapping assets", not clashes,
          "\n".join(clashes[:12]) if clashes else f"{len(assets)} visual assets compared")
    # a logo is any placed image whose source file is an *_appicon.png, wherever it lives
    logo_ids = {s["id"][:8] for t in tracks for s in t["segments"]
                if "appicon" in (vids.get(s["material_id"], {}).get("path") or "").lower()}
    logo_windows = [a[2] for a in assets if a[1] in logo_ids or a[0] == "logo_icons"]
    # Section 2 logo exclusivity exists to stop a MEME rendering under a logo. The
    # owner's connected-visual motif (logo -> arrow -> output card, each in its own
    # third of the frame) is a deliberate exception they asked for and approved, and
    # check 6 above already proves those boxes do not touch. So an intruder is a
    # FULL-WIDTH overlay (a pairing-law meme/card) sharing a logo's window - not a
    # narrow motif companion.
    intruders = [a for a in assets if a[0].startswith(("memes", "placeholders"))
                 and a[1] not in logo_ids
                 and (a[3][1] - a[3][0]) > 1.0
                 and any(overlaps_time(a[2], lw) for lw in logo_windows)]
    check("no meme/placeholder visible during any logo window", not intruders,
          f"logo windows={logo_windows} intruders={[(i[0],i[1]) for i in intruders]}")

    # ---- 7. fonts + uniform_scale -----------------------------------------
    print("\n7. Font resource ids + keyframed segments")
    ALLOWED = {"7525275079106776337": "Markerist", "7462241028796337414": "Awelier",
               "7482756842486009094": "caption font", "7442588993952158224": "CTA Awelier-Black"}
    seen = collections.Counter()
    for m in M["texts"]:
        try:
            j = json.loads(m["content"])
        except Exception:
            continue
        for st in j.get("styles", []):
            fid = str((st.get("font") or {}).get("id") or "")
            if fid:
                seen[fid] += 1
    unknown = {k: v for k, v in seen.items() if k not in ALLOWED}
    check("only expected font resource ids present", not unknown,
          "\n".join(f"{k} ({ALLOWED.get(k,'UNKNOWN')}) x{v}" for k, v in seen.items()))
    kf_bad = []
    for t in tracks:
        for s in t["segments"]:
            if s.get("common_keyframes"):
                if not (s.get("uniform_scale") or {}).get("on"):
                    kf_bad.append(s["id"][:8])
                for blk in s["common_keyframes"]:
                    if blk.get("property_type") != "KFTypeScaleX" or "property" in blk:
                        kf_bad.append(s["id"][:8] + ":schema")
                    for k in blk["keyframe_list"]:
                        if "string_value" not in k or "graphID" not in k:
                            kf_bad.append(s["id"][:8] + ":kf")
    check("every keyframed segment has uniform_scale.on and the exact schema",
          not kf_bad, f"offenders={sorted(set(kf_bad))[:10]}")

    # ---- 8b. render truth --------------------------------------------------
    print("\n8b. Render truth - visible + on-canvas")
    invis = [(t.get("name", t["type"]), s["id"][:8]) for t in tracks for s in t["segments"]
             if t["type"] not in ("audio",) and s.get("visible") is False]
    check("every placed segment has visible == true", not invis, f"hidden={invis[:10]}")
    off = []
    for t in tracks:
        for s in t["segments"]:
            tr = (s.get("clip") or {}).get("transform")
            if tr and (abs(tr["x"]) > 1 or abs(tr["y"]) > 1):
                off.append((t.get("name", t["type"]), s["id"][:8], tr))
    check("every transform on-canvas (|x|,|y| <= 1)", not off, f"offscreen={off[:10]}")
    labels = [s["target_timerange"]["start"] for t in tracks if t.get("name") == "logo_labels"
              for s in t["segments"]]
    icons = [s["target_timerange"]["start"] for t in tracks if t.get("name") == "logo_icons"
             for s in t["segments"]]
    check("every logo window contains its name-label segment",
          all(any(abs(i - l) < 100000 for l in labels) for i in icons),
          f"icons={icons} labels={labels}")

    # ---- 9. lint + diagnose ------------------------------------------------
    # ---- 8c. BLUEBERRY: assert what the engine fixes ------------------------
    # Each of these guards a defect that was fixed once, in one builder, and came back in
    # the other. The engine now prevents them; this proves it, every run.
    print("\n8c. structural invariants (blueberry)")

    tt_all = {x["id"]: x for x in d["materials"].get("text_templates", [])}
    ghosts = []
    for tr in d["tracks"]:
        for s in tr["segments"]:
            tpl = tt_all.get(s["material_id"])
            if not tpl:
                continue
            dur = s["target_timerange"]["duration"]
            for r in tpl.get("text_info_resources", []):
                ai = r.get("attach_info") or {}
                if ai and (ai.get("duration") != dur or ai.get("start_time") != 0):
                    body = ""
                    try:
                        tx = {t["id"]: t for t in d["materials"]["texts"]}
                        body = json.loads(tx[r["text_material_id"]]["content"])["text"]
                    except Exception:
                        pass
                    ghosts.append((body[:24], ai.get("duration"), dur))
    check("no ghost layers: every text_template attach_info matches its segment",
          not ghosts,
          f"{len(ghosts)} mismatched: {ghosts[:6]}" if ghosts else
          f"{sum(1 for t in d['tracks'] for s in t['segments'] if s['material_id'] in tt_all)}"
          " template segments checked")

    unstyled = []
    for m in d["materials"].get("texts", []):
        try:
            c = json.loads(m["content"])
        except Exception:
            continue
        body, styles = c.get("text", ""), (c.get("styles") or [])
        if not styles or not body:
            continue
        rngs = [st.get("range") for st in styles if st.get("range")]
        if not rngs:
            continue
        if rngs[0][0] != 0 or rngs[-1][1] != len(body):
            unstyled.append((body[:24], rngs[0][0], rngs[-1][1], len(body)))
    check("every text style range covers its whole string",
          not unstyled,
          f"{len(unstyled)} with an unstyled head or tail (renders at giant default "
          f"size): {unstyled[:6]}" if unstyled else
          f"{len(d['materials'].get('texts', []))} text materials checked")

    import hashlib
    def _h(p):
        return hashlib.sha256(open(p, "rb").read()).hexdigest()[:12]
    copies = [os.path.join(draft, "draft_content.json")]
    tl = os.path.join(draft, "Timelines")
    if os.path.isdir(tl):
        for sub in os.listdir(tl):
            sd = os.path.join(tl, sub)
            if os.path.isdir(sd):
                for name in ("template-2.tmp", "draft_content.json"):
                    if os.path.exists(os.path.join(sd, name)):
                        copies.append(os.path.join(sd, name))
    ch = _h(canon)
    diverged = [(os.path.relpath(p, draft), _h(p)) for p in copies if _h(p) != ch]
    check("every timeline copy identical to the canonical",
          not diverged,
          f"canonical={ch} DIVERGED={diverged}" if diverged else
          f"canonical={ch}, {len(copies)} mirror(s) match "
          f"({', '.join(os.path.relpath(p, draft) for p in copies)})")

    # A card alive for a long time while other layers change over it is the pacing smell
    # the owner called out: the subagent card held for 9.3s carrying four bullet lines
    # while four labels fired across it. A card is a unit of ATTENTION, not of information.
    # Informational, not a failure - a comparison card is legitimately long-lived.
    vids_all = {v["id"]: v for v in d["materials"].get("videos", [])}
    longlived = []
    for tr in d["tracks"]:
        if tr["type"] != "video" or (tr.get("name") or "") == "V1":
            continue
        for s2 in tr["segments"]:
            secs = s2["target_timerange"]["duration"] / 1e6
            if secs > LONGLIVED_S:
                m = vids_all.get(s2["material_id"]) or {}
                longlived.append((os.path.basename(m.get("path", "?")), round(secs, 1)))
    if longlived:
        print(f"  [INFO] long-lived assets (> {LONGLIVED_S}s) - check nothing is changing "
              f"over them: {sorted(longlived, key=lambda x: -x[1])}")
    else:
        print(f"  [INFO] no overlay held longer than {LONGLIVED_S}s")

    # ---- the centre band belongs to her screen recordings ---------------------
    # Measured 2026-08-26: she moved all four subagent cards out of the centre to top edge
    # 0.6771, and said why - "I will be placing screen recordings in the centre". A card
    # hanging below the ceiling is not a build failure (a tall card physically cannot clear
    # it, and she left the 465px+ ones where they were) but it IS a split candidate.
    import sys as _sys, os as _os
    _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
    import house_layout as _HL
    intruders = []
    for tr in d["tracks"]:
        if tr["type"] != "video" or (tr.get("name") or "") == "V1":
            continue
        for s2 in tr["segments"]:
            m = vids_all.get(s2["material_id"]) or {}
            path = m.get("path") or ""
            if not path.lower().endswith(".png"):
                continue                      # drawn cards only, not her footage
            w, h = m.get("width") or 0, m.get("height") or 0
            if not w or not h:
                continue
            fit = min(1080.0 / w, 1920.0 / h)
            sc = (s2["clip"].get("scale") or {"x": 1})["x"]
            dh = h * fit * sc
            bottom = (s2["clip"]["transform"]["y"]) - (dh / 2) / 960.0
            if bottom < _HL.SCREENREC_CEILING:
                intruders.append((_os.path.basename(path), round(bottom, 3),
                                  round(dh)))
    if intruders:
        print(f"  [INFO] {len(intruders)} drawn card(s) hang below the reserved centre "
              f"(ceiling {_HL.SCREENREC_CEILING}) - a screen recording cannot be dropped "
              f"under them. Split candidates: {sorted(set(intruders))[:6]}")
    else:
        print(f"  [INFO] every drawn card clears the reserved centre band")

    # (The 22-char label warning that used to live here was removed on 2026-08-26.
    # It measured the wrong thing: she keeps a 36-character line when it is PLAIN
    # text at size 10, and shortens a 20-character one when it is a paper label.
    # Fit is the constraint, not length, and the engine now fits labels itself.)

    segs_total = sum(len(t["segments"]) for t in d["tracks"])
    dur_s = (d.get("duration") or 0) / 1e6
    if dur_s:
        per80 = segs_total * 80.0 / dur_s
        print(f"  [INFO] density: {segs_total} segments / {dur_s:.1f}s = {per80:.0f} per "
              f"80s (owner reference reel: 242)")

    print("\n9. capcut lint + diagnose")
    r = subprocess.run(["capcut", "lint", draft], capture_output=True, text=True, shell=True)
    try:
        lj = json.loads(r.stdout)
        errs = lj.get("errors", []) if isinstance(lj, dict) else []
    except Exception:
        errs = ["<unparseable lint output>"] if r.returncode == 2 else []
    check("capcut lint = 0 errors", not errs, f"exit={r.returncode} errors={str(errs)[:300]}")
    r = subprocess.run(["capcut", "diagnose", draft], capture_output=True, text=True, shell=True)
    dj = json.loads(r.stdout)
    check("diagnose diverged == false", dj["diverged"] is False,
          f"canonical={dj['canonical']} diverged={dj['diverged']}")

    print("\n" + "=" * 64)
    if FAILS:
        print(f"RESULT: {len(FAILS)} FAILURE(S): " + "; ".join(FAILS))
    else:
        print("RESULT: ALL CHECKS PASS - zero failures")
    print("=" * 64)
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
