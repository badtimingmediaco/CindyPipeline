# -*- coding: utf-8 -*-
"""The overlay pass. ONE engine, driven by a spec - no per-video fork.

Version berry had two builders, build_reviewer.py and build_seo.py, sharing 490 identical
lines. Four of the most expensive fixes ever made lived in one and not the other, and
build_seo.py still carried the save() bug that destroyed a finished build. That is the
structural reason the same defects kept reappearing: a fix landed in a fork, and the next
video started from the other one.

There is now one engine. A new video is a spec file, not a copy of this module.
"""
import os

from . import capcutcli, draftio, layout as HL, materials, measure, paths, spec as specmod

FRAME = 1.0 / 30.0


def close_gaps(beats, max_gap=0.26):
    """Butt adjacent overlays together - no 1-5 frame slivers between assets.

    A two-frame hole between one meme ending and the next starting reads as a flicker.
    Only gaps small enough to have been unintentional are closed; a deliberate empty beat
    is left alone. Applied per layer so a meme is never stretched to meet an unrelated
    text label.
    """
    closed = 0
    for want_media in (True, False):
        grp = sorted([b for b in beats if ("asset" in b) == want_media],
                     key=lambda x: x["t"][0])
        for a, b in zip(grp, grp[1:]):
            gap = b["t"][0] - a["t"][1]
            if 0 < gap <= max_gap:
                a["t"] = [a["t"][0], b["t"][0]]
                closed += 1
    return closed


def _sfx_hits(beats, end, lead_ins):
    # lead_ins arrive from JSON as lists; hits below are tuples, and Python will not
    # order a list against a tuple. Normalise before anything sorts them.
    hits = [tuple(h) for h in lead_ins]
    for b in beats:
        if b.get("sfx"):
            hits.append((b["t"][0], b["sfx"]))
        for a in (b.get("annotate") or []):
            hits.append((a["t"][0], a.get("sfx", "pop motion.MP3")))
        if b["kind"] == "stack":
            for ln in (b.get("lines") or [])[1:]:
                hits.append((ln[0], b.get("sfx")))
    return [h for h in hits if h[1]]


TAIL_OK = {"magic reveal.MP3", "ascending whistles.MP3", "jingle of time.MP3",
           "success.MP3", "special effect.MP3", "kirarin glitter.MP3"}


def place_sfx(draft, beats, end, lead_ins):
    """Every hit capped at the NEXT hit, unless it is a reveal/riser/jingle.

    An uncapped typing effect ran 3.5s over the following beat. Capping only at the video
    end is not enough.
    """
    hits = _sfx_hits(beats, end, lead_ins)
    durs = {}
    for _, f in hits:
        if f not in durs:
            p = os.path.join(paths.SFXDIR, f)
            if not os.path.exists(p):
                raise SystemExit("INVENTED SFX FILENAME: %s" % f)
            durs[f] = capcutcli.probe_audio(p)
    ordered = sorted(hits)
    ends = []
    for i, (t0, f) in enumerate(ordered):
        nxt = ordered[i + 1][0] if i + 1 < len(ordered) else end
        dur = min(durs[f], end - t0)
        if f in TAIL_OK:
            dur = min(dur, max(0.30, nxt - t0 + 0.60))
        else:
            dur = min(dur, max(0.25, nxt - t0), 1.20)
        if dur <= 0.05:
            continue
        idx = next((i2 for i2, e in enumerate(ends) if e <= t0), None)
        if idx is None:
            ends.append(0.0)
            idx = len(ends) - 1
        ends[idx] = t0 + dur
        capcutcli.cli("add-audio", draft,
                      os.path.join(paths.SFXDIR, f).replace("\\", "/"),
                      "%s" % t0, "%.3f" % dur, "--track-name", "sfx%d" % (idx + 1))
    return len(ordered), len(ends)


def solve_annotation(card_png, ann, seg_scale, seg_y, allow_uncached=False):
    """-> (mark_key, scale, x, y) solved from the card's own pixels and the sticker's ink.

    In version berry these three numbers were float literals in the schedule, solved once
    against one revision of one card. Redraw the card and they point at nothing, silently.
    Here they are recomputed from the region manifest every build.
    """
    cx, cy, w_px = measure.card_region_target(card_png, ann["region"], seg_scale, seg_y,
                                              pad=ann.get("pad", 1.18),
                                              place=ann.get("place", "on"))
    rid = HL.ANNOTATE[ann["mark"]]
    art = measure.sticker_art(rid)
    if art is None:
        if not allow_uncached:
            raise SystemExit(
                "annotation %r has no artwork in CapCut's cache, so its placement cannot "
                "be checked before shipping. Open the draft in CapCut once while online "
                "to fetch it, or re-run with --allow-uncached to place it blind."
                % ann["mark"])
        return ann["mark"], ann.get("fallback_scale", 0.7), cx, cy
    sc, x, y = measure.place_sticker_on(art, cx, cy, w_px)
    return ann["mark"], sc, x, y


def build(sp, draft, allow_uncached=False, verbose=True):
    """Build every overlay layer of `sp` into `draft`. Returns a summary dict."""
    say = (lambda *a: print(*a)) if verbose else (lambda *a: None)

    if capcutcli.capcut_running():
        raise SystemExit("CapCut is RUNNING. It never re-reads from disk while open and "
                         "its next autosave destroys this build. Quit CapCut and re-run.")

    specmod.require_valid(sp)
    beats = [dict(b) for b in sp["beats"]]
    for b in beats:
        if b.get("asset"):
            b["path"] = paths.resolve_asset(b["asset"])
        b.setdefault("band", HL.default_band(b["kind"]))
    nclosed = close_gaps(beats)
    say("closed %d sliver gap(s)" % nclosed)

    end = float(sp["end"])
    draftio.backup(draft, sp["name"] + "_pre_overlays")
    d = draftio.load(draft)
    say("stripped %d old overlay/sfx segments" % materials.strip_overlays(d))
    draftio.save(draft, d)

    # ---- 1. media. Lanes are assigned BEFORE add-video: two segments overlapping in
    #        time on one track are silently serialised by CapCut.
    media = [b for b in beats if b.get("path")]
    lane_end = []
    for b in sorted(media, key=lambda x: x["t"][0]):
        a, z = b["t"]
        idx = next((i for i, e in enumerate(lane_end) if e <= a + 1e-6), None)
        if idx is None:
            lane_end.append(z)
            idx = len(lane_end) - 1
        else:
            lane_end[idx] = z
        b["lane"] = idx
    for b in media:
        dur = b["t"][1] - b["t"][0]
        _, _, sdur = capcutcli.probe(b["path"])
        if sdur is not None and dur > sdur + 1e-3:
            say("  ! %s: window %.2fs > source %.2fs - trimmed"
                % (os.path.basename(b["path"]), dur, sdur))
            dur = sdur
            b["t"] = [b["t"][0], round(b["t"][0] + dur, 4)]
        r = capcutcli.cli("add-video", draft, b["path"].replace("\\", "/"),
                          "%s" % b["t"][0], "%.3f" % dur,
                          "--track-name", "gfx_%d" % b["lane"])
        if not r.get("ok"):
            say("  ! add-video failed", b["path"], r)
            continue
        b["seg_id"] = r["segment_id"]
        b["src_w"], b["src_h"] = r["width"], r["height"]
    placed = sum(1 for b in beats if b.get("seg_id"))
    say("placed %d/%d media segments across %d lane(s)"
        % (placed, len(media), len(lane_end)))
    say("snapshot hash sync: %d stale snapshot(s) refreshed"
        % capcutcli.sync_snapshots(draft))

    # ---- 2. SFX
    nhits, ntracks = place_sfx(draft, beats, end, sp.get("lead_in_sfx", []))
    say("placed %d SFX hits across %d tracks" % (nhits, ntracks))

    # ---- 3. structural pass: geometry solved, every text layer cloned
    d = draftio.load(draft)
    M = d["materials"]
    vids = {v["id"]: v for v in M.get("videos", [])}
    donor_cache = os.path.join(paths.STATE, sp["name"] + "_donor.json")
    (donor_seg, donor_tpl), shadow_mat = materials.find_donors(d, donor_cache)
    by_id = {s["id"]: s for t in d["tracks"] for s in t["segments"]}

    texts, widths, annots = [], [], []
    last_label_y = 0.36
    n_logos = sum(1 for b in beats if b["kind"] == "logo")

    def add_label(text, t_pair, y):
        seg, wpx = materials.clone_sticker(d, donor_seg, donor_tpl, text,
                                           t_pair[0], t_pair[1], 0.0, y)
        texts.append(seg)
        widths.append((text, wpx))

    for b in beats:
        t_in, t_out = b["t"]
        kind = b["kind"]

        if b.get("seg_id"):
            s = by_id.get(b["seg_id"])
            if s is None:
                say("  ! placed segment vanished:", b["path"])
                continue
            w, h = b["src_w"], b["src_h"]
            fit = min(1080.0 / w, 1920.0 / h)

            if kind == "logo":
                # Scale is SOLVED from the artwork's content box, not shared between
                # files: two logos at one scale rendered different sizes because one mark
                # filled 50.6% of its canvas and the other 100%.
                sc = measure.optical_scale(b["path"])
                x = HL.logo_slot(b.get("slot", "centre"), n_logos)
                s["clip"]["scale"] = {"x": sc, "y": sc}
                s["clip"]["transform"] = {"x": x, "y": HL.LOGO_Y}
                b["disp"] = (round(w * fit * sc), round(h * fit * sc))
            else:
                sc, cy, dh, ly = HL.media_geom(b["band"], w, h)
                s["clip"]["scale"] = {"x": sc, "y": sc}
                s["clip"]["transform"] = {"x": 0.0, "y": cy}
                last_label_y = ly
                b["disp"] = (round(w * fit * sc), round(dh))
                b["_geom"] = (sc, cy)
                if b.get("label"):
                    add_label(b["label"], b.get("label_t", [t_in, t_out]), ly)
            s["visible"] = True

            for ann in (b.get("annotate") or []):
                sc_g, cy_g = b.get("_geom", (1.0, 0.0))
                mark, asc, ax, ay = solve_annotation(b["path"], ann, sc_g, cy_g,
                                                     allow_uncached)
                annots.append(HL.place_sticker(d, mark, ann["t"][0], ann["t"][1],
                                               ax, ay, asc))

        elif kind == "text":
            add_label(b["text"], [t_in, t_out], HL.text_y(b["band"], last_label_y))

        elif kind == "stack":
            for i, (t0, line) in enumerate(b["lines"]):
                add_label(line, [t0, t_out], 0.80 - i * 0.18)

        elif kind == "logo_label":
            seg, wpx = materials.clone_shadow_label(
                d, shadow_mat, donor_seg, b["text"], t_in, t_out,
                HL.logo_slot(b.get("slot", "centre"), n_logos), HL.LOGO_LABEL_Y)
            texts.append(seg)
            widths.append((b["text"], wpx))

    # the sample paper sticker was only ever the style donor - it must not ship
    for t in d["tracks"]:
        t["segments"] = [s for s in t["segments"] if s["id"] != donor_seg["id"]]
    d["tracks"] = [t for t in d["tracks"] if t["segments"] or t["type"] == "video"]

    donor_keep = [donor_tpl, shadow_mat["id"]]
    tt_all = {x["id"]: x for x in M.get("text_templates", [])}
    if donor_tpl in tt_all:
        tir = tt_all[donor_tpl]["text_info_resources"][0]
        donor_keep += [tir["text_material_id"]] + list(tir.get("extra_material_refs", []))

    for i, ln in enumerate(materials.lanes(texts)):
        d["tracks"].append(materials.new_track("stickers%d" % (i + 1), "text", ln))
    for i, ln in enumerate(materials.lanes(annots)):
        d["tracks"].append(materials.new_track("annot%d" % (i + 1), "sticker", ln))
    if annots:
        say("placed %d annotation sticker(s), all solved from card regions" % len(annots))

    ghosts = materials.ghost_sweep(d)
    say("ghost sweep: %d attach_info re-synced" % ghosts)

    ngc = materials.gc_text_materials(d, donor_keep)
    nlane = 0
    for t in d["tracks"]:
        if (t.get("name") or "").startswith("gfx_"):
            nlane += 1
            t["name"] = "memes" if t["name"] == "gfx_0" else "memes" + t["name"][4:]

    auds = {a["id"]: a for a in M.get("audios", [])}
    v1_name = os.path.basename(sp.get("source", ""))
    nvol = 0
    for t in d["tracks"]:
        for s2 in t["segments"]:
            a = auds.get(s2["material_id"])
            if a and os.path.basename(a.get("path", "")).lower().startswith("success"):
                s2["volume"] = HL.SUCCESS_VOLUME
                nvol += 1
            v = vids.get(s2["material_id"])
            if v and v1_name and v1_name in (v.get("path") or ""):
                s2["volume"] = HL.V1_VOLUME
    draftio.save(draft, d)

    over = [(t, round(w)) for t, w in widths if w > 980]
    say("garbage-collected %d orphan text material(s)" % ngc)
    say("media on %d lane track(s) | %d text layers | widest row %.0fpx | over budget: %s"
        % (nlane, len(texts), max([w for _, w in widths] or [0]), over or "none"))
    say("volume pass: V1 = %s, success.MP3 x%d = %s"
        % (HL.V1_VOLUME, nvol, HL.SUCCESS_VOLUME))
    return {"media": placed, "texts": len(texts), "annots": len(annots),
            "ghosts": ghosts, "gaps_closed": nclosed, "over_budget": over}
