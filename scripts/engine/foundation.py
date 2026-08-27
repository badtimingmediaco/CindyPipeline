# -*- coding: utf-8 -*-
"""The foundation pass: V1, the adjust layer, the title rows, the CTA.

Everything the overlay pass assumes is already in place. Deliberately does NOT touch her
VO, her face, the colour grade itself, or the sample paper sticker - that is the style
donor the overlay pass clones from.

What changed from version berry: the title-width rule now RUNS. It was THE_METHOD's rule
number one, and its entire enforcement in `_runs/claude_reviewer/base.py` was a comment
recording that someone had measured by hand once. There was no PIL import in the file.
A title that overflows its torn-paper graphic is the single most visible defect this
pipeline has ever shipped, and it was guarded by prose.
"""
import os

from . import capcutcli, draftio, layout as HL, materials, measure, paths

# A plain title row may be any width so long as it stays on frame, with the same 25px
# safety margin the visual gate uses - the width model is an estimate even after the
# stroke and shadow corrections, so bias toward failing.
FRAME_SAFE = 1030.0


def text_of(mat):
    try:
        return measure.content_of(mat)["text"]
    except Exception:
        return mat.get("content") or ""


def build(sp, draft, verbose=True):
    say = (lambda *a: print(*a)) if verbose else (lambda *a: None)

    if capcutcli.capcut_running():
        raise SystemExit("CapCut is RUNNING - quit it before building.")

    title = sp.get("title") or {}
    replace = title.get("replace") or {}
    title_end = float(title.get("end", 3.80))
    end = float(sp["end"])
    end_us = int(end * 1e6)
    cta = title.get("cta") or {}
    v1_path = paths.resolve_asset(sp["source"])
    if not os.path.exists(v1_path):
        raise SystemExit("source video not found: %s" % v1_path)

    # ---- 1. V1
    r = capcutcli.cli("add-video", draft, v1_path.replace("\\", "/"), "0", "%.3f" % end,
                      "--track-name", "V1")
    say("V1:", "ok" if r.get("ok") else r)

    # ---- 2. structural
    d = draftio.load(draft)
    M = d["materials"]
    texts = {t["id"]: t for t in M.get("texts", [])}
    tpls = {t["id"]: t for t in M.get("text_templates", [])}

    def tpl_child(mid):
        t = tpls.get(mid)
        return texts.get(t["text_info_resources"][0]["text_material_id"]) if t else None

    # ---- 2a. index the title rows FIRST. The width gate needs each row's SEGMENT, not
    # just its material, because the rendered width depends on the segment's scale.
    gap_after = title.get("gap_after") or {}
    rowinfo = {}
    for tr in d["tracks"]:
        for s in tr["segments"]:
            if s["target_timerange"]["start"] / 1e6 >= title_end + 0.1:
                continue
            mid = s["material_id"]
            mat = texts.get(mid) or tpl_child(mid)
            if mat is None:
                continue
            rowinfo[text_of(mat).strip()] = (mat, s, mid in tpls)

    # ---- 2b. WIDTH GATE. Measure every replacement BEFORE writing anything.
    #
    # Two different questions, needing two different measurements:
    #
    #   TORN-PAPER row - "does it still fit the graphic?" A RATIO against the donor
    #     string, which measure.fits_donor answers. The absolute figure it returns carries
    #     the template's internal 2.44x multiplier, harmless in a ratio because it appears
    #     on both sides and cancels.
    #
    #   PLAIN row      - "does it stay on frame?" An ABSOLUTE, which must be measured with
    #     the segment's own scale and WITHOUT the template multiplier. Using fits_donor's
    #     number here inflated every plain row 2.44x and rejected a title that really
    #     renders at 676px as "1457px, runs off frame". A gate that cries wolf gets
    #     switched off, so this distinction matters as much as the check does.
    problems = []
    for old, new in replace.items():
        info = rowinfo.get(old)
        if info is None:
            problems.append("title row %r not found in the template" % old)
            continue
        mat, seg, is_child = info
        sc = seg["clip"]["scale"]["x"]
        try:
            fp, size = measure.style_font(mat)
            if is_child:
                ok, npx, opx, ratio = measure.fits_donor(mat, new)
                flag = "ok" if ok else "OVERFLOW - the paper does not grow"
            else:
                npx = measure.rendered_width_px(fp, new, size, sc, False)
                opx = measure.rendered_width_px(fp, old, size, sc, False)
                ratio = npx / opx if opx else 0.0
                ok = npx <= FRAME_SAFE
                flag = "on frame" if ok else "OFF FRAME"
        except RuntimeError as e:
            problems.append("%r -> %r: %s" % (old, new, e))
            continue
        say("  width gate %-27r -> %-27r %7.1fpx  %s" % (old, new, npx, flag))
        if not ok and is_child:
            problems.append(
                "%r -> %r overflows its torn-paper row: %.1fpx of %.1fpx available "
                "(%.0f%%). Choose a shorter phrase - the graphic does not grow."
                % (old, new, npx, opx, ratio * 100))
        if not ok and not is_child:
            problems.append(
                "%r -> %r renders %.0fpx wide and will run off the 1080px frame "
                "(safe width %.0fpx)" % (old, new, npx, FRAME_SAFE))
    if problems:
        raise SystemExit("TITLE REJECTED before any write:\n  - " + "\n  - ".join(problems))

    stripped = retimed = retexted = moved = 0
    for tr in d["tracks"]:
        keep = []
        for s in tr["segments"]:
            mid = s["material_id"]
            mat = texts.get(mid) or tpl_child(mid)
            body = text_of(mat) if mat else ""
            rng = s["target_timerange"]
            a = rng["start"] / 1e6

            # leftover captions from the template's previous video
            if tr["type"] == "text" and len(tr["segments"]) > 20:
                stripped += 1
                continue

            if cta and body.strip().startswith(cta.get("match", "Comment")):
                rng["start"] = int(cta["t"][0] * 1e6)
                rng["duration"] = int((cta["t"][1] - cta["t"][0]) * 1e6)
                materials.set_text(mat, cta["text"])
                if mid in tpls:
                    materials.sync_attach(tpls[mid], s)
                retimed += 1
                retexted += 1
                keep.append(s)
                continue

            if a < title_end + 0.1 and (body.strip() in replace
                                        or body.strip() in (title.get("keep") or [])):
                rng["start"] = 0
                rng["duration"] = int(title_end * 1e6)
                retimed += 1
                if body.strip() in replace:
                    old = body.strip()
                    new = replace[old]
                    # A row that shares its line with another word is placed from that
                    # neighbour's measured right edge. transform.x is a CENTRE, so simply
                    # inheriting it makes a longer replacement grow leftwards into the word
                    # before it - which is how "Claude" and "catch" read as one smashed
                    # word. A row NOT named in gap_after is centred and stays centred.
                    if old in gap_after:
                        nb = gap_after[old]
                        if nb not in rowinfo:
                            raise SystemExit(
                                "title.gap_after names %r, which is not a title row "
                                "(rows found: %s)" % (nb, sorted(rowinfo)))
                        nmat, nseg, ntpl = rowinfo[nb]
                        nx, tgap = measure.gap_after_x(
                            nmat, nb, nseg["clip"]["transform"]["x"],
                            nseg["clip"]["scale"]["x"], ntpl,
                            mat, old, new, s["clip"]["transform"]["x"],
                            s["clip"]["scale"]["x"], (mid in tpls))
                        say("  word gap  %r after %r: preserving the template's %.1fpx"
                            % (new, nb, tgap))
                        if abs(nx - s["clip"]["transform"]["x"]) > 1e-4:
                            s["clip"]["transform"]["x"] = nx
                            moved += 1
                    elif old in (title.get("left_align") or []):
                        nx = measure.left_aligned_x(
                            mat, old, new, s["clip"]["transform"]["x"],
                            s["clip"]["scale"]["x"], template=(mid in tpls))
                        if abs(nx - s["clip"]["transform"]["x"]) > 1e-4:
                            s["clip"]["transform"]["x"] = nx
                            moved += 1
                    materials.set_text(mat, new)
                    retexted += 1
                if mid in tpls:
                    materials.sync_attach(tpls[mid], s)
                keep.append(s)
                continue

            if tr["type"] == "adjust":
                rng["start"] = 0
                rng["duration"] = end_us
                retimed += 1
                keep.append(s)
                continue

            if tr["type"] == "audio":     # the template's sample SFX
                continue

            keep.append(s)
        tr["segments"] = keep

    d["tracks"] = [t for t in d["tracks"] if t["segments"] or t["type"] == "video"]
    d["duration"] = end_us
    materials.ghost_sweep(d)
    draftio.save(draft, d)

    say("stripped %d stale caption segments" % stripped)
    say("retimed %d segments, retexted %d, left-edge corrected %d" % (retimed, retexted, moved))
    say("duration set to %ss" % end)
    return {"stripped": stripped, "retimed": retimed, "retexted": retexted, "moved": moved}
