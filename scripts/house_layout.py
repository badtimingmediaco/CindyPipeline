# -*- coding: utf-8 -*-
"""HOUSE LAYOUT - the placement laws, measured from the owner's own hand-finished edits.

Import this from every build script. Every constant here was READ OFF a draft the owner
finished by hand (2026-08-20 Claude SEO round 2 unless noted); nothing is estimated.

Units: clip.transform values are fractions of HALF the canvas (+/-1 = frame edge, +y = UP).
Canvas 1080x1920. So 1 half-unit = 540px horizontally, 960px vertically.

THE THREE GRAMMARS
------------------
1. TOP BAND - memes, gifs, small illustrative cards.
   Centred, top edge at ~8.4% of frame, paper label STRADDLING the bottom edge.
   `meme_geom()`.
2. CENTRE BAND - dense UI: real screenshots, screen recordings, prompt/result cards, the
   fix list. Centred at y ~ +0.04 and ~1015px wide (the house screen-rec card), with the
   paper label ABOVE the top edge. `card_geom()`.
3. TITLE-CARD BAND - anything on screen during the opening title lives in the LOWER third
   (y -0.18 ... -0.48), small, may bleed off the left frame edge, annotated with the red
   marker stickers. `TITLE_BAND`. The old "Claude -> arrow -> card at y +0.12" motif drawn
   across her face was rejected.
"""
import copy, json, os, uuid

U = lambda: str(uuid.uuid4()).upper()
PIPE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STICKER_KIT = os.path.join(PIPE, "_state", "sticker_kit.json")

# ----------------------------------------------------------------- 1. TOP BAND
MEME_TOP = 0.832          # top edge at 8.4% of frame height (owner-measured)
LABEL_STRADDLE = 0.023    # label centre sits this far above the meme's bottom edge
CAP_W = 844.0             # hard width cap
MAX_H = 475.0             # hard height cap - their ceiling, NOT their default
DEFAULT_H = 430.0         # their typical displayed height (measured 385/388/424/430/475/484)
WIDE_ASPECT = 2.0         # a very wide clip needs the full width to stay legible


def meme_geom(w, h, target_h=DEFAULT_H):
    """-> (scale, centre_y, displayed_h_px, label_y) for a TOP-BAND meme/small card.

    Sizes to `target_h` (default 430px, the owner's typical), never exceeding the 844x475
    caps and never enlarging past 1:1 of the source. A very wide clip (aspect >= 2) is
    width-driven instead, because height-fitting would leave it unreadably small - that is
    how their DeVito clip ended up at the full 844 (640x292 -> 844x385).
    """
    fit = min(1080.0 / w, 1920.0 / h)
    aspect = w / float(h)
    by_h = target_h / (h * fit)
    by_w = CAP_W / (w * fit)
    sc = by_w if aspect >= WIDE_ASPECT else min(by_h, by_w)
    sc = min(sc, MAX_H / (h * fit), CAP_W / (w * fit))
    dh = h * fit * sc
    cy = MEME_TOP - (dh / 2) / 960.0
    label_y = cy - (dh / 2) / 960.0 + LABEL_STRADDLE
    return round(sc, 4), round(cy, 4), dh, round(label_y, 4)


# -------------------------------------------------------------- 2. CENTRE BAND
CARD_Y = 0.04             # legacy centre anchor (measured 0.00/0.022/0.04/0.058)
CARD_TOP = 0.31           # cards are TOP-anchored: their measured top edges were 0.28 /
                          # 0.293 / 0.369. Centre-anchoring makes a short card sit lower
                          # than a tall one, so a run of step cards jitters up and down.
CARD_W = 1015.0           # the house screen-rec card width (measured 943-1103, mean ~1015)
CARD_LABEL_GAP = 0.085    # label centre sits this far ABOVE the card's top edge


CARD_MAX_H = 700.0        # a portrait crop sized purely by width runs off the frame


def card_geom(w, h, target_w=CARD_W, y=None, max_h=CARD_MAX_H, top=CARD_TOP):
    """-> (scale, centre_y, displayed_h_px, label_y) for a CENTRED dense-UI card.

    Use for anything the viewer must actually READ: real screenshots, screen recordings,
    dashboards, the prioritised fix list. The label goes ABOVE the card, not straddling it.
    """
    fit = min(1080.0 / w, 1920.0 / h)
    sc = min(target_w / (w * fit), 1080.0 / (w * fit), max_h / (h * fit))
    dh = h * fit * sc
    cy = top - (dh / 2) / 960.0 if y is None else y
    label_y = cy + (dh / 2) / 960.0 + CARD_LABEL_GAP
    return round(sc, 4), round(cy, 4), dh, round(label_y, 4)


# ------------------------------------------------------------------- 3. LOGOS
# Measured from their ChatGPT / Perplexity / Google row. NOT the +0.12 motif band.
LOGO_Y = 0.493            # icon centre
LOGO_LABEL_Y = 0.317      # plain white text label, directly under the icon
LOGO_SCALE = 0.225        # an 800px tile renders ~243px
LOGO_X = (-0.518, 0.0, 0.518)      # 3-up row; 2-up uses the outer pair
LOGO_HEADER_Y = 0.700     # a paper lead-in above the row, e.g. 'Checks whether:'
# Icons enter ONE AT A TIME, each on its own spoken name, and accumulate until the beat ends.

# --------------------------------------------------------------- 4. TITLE BAND
TITLE_BAND = (-0.18, -0.48)   # anything on screen during the title card lives here
TITLE_END_DEFAULT = 3.80      # their hold (was 3.20 in my build)

# ------------------------------------------------------------------ 5. LEVELS
V1_VOLUME = 2.97          # +9.5 dB. 2.512 (+8 dB) is the FLOOR; they raise it every time.
SUCCESS_VOLUME = 0.224    # -13 dB on every success.MP3


# ---------------------------------------------------------- 6. CUT-TRIM POLICY
def trim_at_cut(t_in, t_out, cuts, carries_explanation=False):
    """Section 5: an overlay ends at the first Descript cut inside its window.

    OWNER OVERRIDE (2026-08-20): the rule stands, EXCEPT when the same asset is still
    doing explanatory work for the phrase after the cut - then let it run through. Obeying
    the rule blindly cost ~0.8s of screen time on three beats of the Claude SEO build,
    because the start got pushed past the cut instead of the asset spanning it.
    """
    if carries_explanation:
        return t_in, t_out
    inside = [c for c in cuts if t_in + 0.1 < c < t_out]
    return (t_in, round(min(inside), 4)) if inside else (t_in, t_out)


# ------------------------------------------------- 7. RED-MARKER ANNOTATION KIT
# Harvested from 26 of the owner's drafts -> _state/sticker_kit.json (43 stickers).
# These are CapCut's own artistEffect stickers; they render from the local CapCut cache,
# and on a new machine CapCut re-fetches them by resource_id (needs one online open).
ANNOTATE = {
    "circle":        "7470375665200549181",   # red circle highlight   (x22 - their favourite)
    "circle_sign":   "7464600252067106109",   # red circle, thinner
    "highlight_box": "7561712008945487157",   # box around a region
    "dashed_box":    "7503562334389013813",   # dashed rectangle frame
    "box_red":       "7476368984087055669",
    "arrow_hand":    "7540930568146455869",   # hand-drawn arrow, points at a thing
    "arrow":         "7476737710573538613",   # straight arrow, for list rows
    "arrow_marker":  "7473056601671241013",   # arrow with a red line marker
    "arrow_line":    "7567234604453629237",   # curved red line arrow
    "underline":     "7476369487638318389",   # red underline under a value
    "cursor_hand":   "7606748857111694600",   # pointing-hand cursor
    "cross_x":       "7476487068781268277",   # red X - "don't do this"
    "check_green":   "7528726073790549301",   # green tick - "do this"
}


def place_sticker(d, key_or_rid, t_in, t_out, x, y, scale=0.7, kit_path=STICKER_KIT):
    """Clone one annotation sticker into draft dict `d` and return the new segment.

    Deep-clones a REAL rendering sticker segment + its material with fresh ids - never
    hand-assembled (section 7a: hand-built segments pass lint and render as nothing).
    Caller appends the segment to a track and enforces track order afterwards.
    """
    kit = json.load(open(kit_path, encoding="utf-8"))
    rid = ANNOTATE.get(key_or_rid, key_or_rid)
    entry = kit.get(str(rid))
    if entry is None:
        raise KeyError(f"sticker {key_or_rid!r} not in the kit - run harvest_stickers.py")
    mat = copy.deepcopy(entry["material"])
    mat["id"] = U()
    d["materials"].setdefault("stickers", []).append(mat)
    seg = copy.deepcopy(entry["donor_segment"])
    seg["id"] = U()
    seg["material_id"] = mat["id"]
    seg["extra_material_refs"] = []
    seg["target_timerange"] = {"start": int(t_in * 1e6), "duration": int((t_out - t_in) * 1e6)}
    seg["source_timerange"] = None
    seg["clip"]["transform"] = {"x": x, "y": y}
    seg["clip"]["scale"] = {"x": scale, "y": scale}
    seg["visible"] = True
    seg["common_keyframes"] = []
    seg["keyframe_refs"] = []
    return seg
