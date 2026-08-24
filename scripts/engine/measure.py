# -*- coding: utf-8 -*-
"""SOLVE every number. Nothing here may be typed into a spec.

This module is the answer to "why do the same errors keep coming back after they were
fixed?". They came back because a value was solved ONCE, by hand, and then pasted into the
next build as a literal:

    L2_X = {"catch": 0.2973}                        # "solved from measured widths"
    annot=[("circle", 0.6890, 0.0851, 0.4099, ...)] # solved against a card that may change
    OPT_CHATGPT = optical.optical_scale(...)        # computed on line 63, never used

A literal is a measurement that has stopped tracking what it measures. Change the word,
redraw the card, swap the logo, and the number is silently wrong - and it looks perfectly
correct in JSON, so the verifier passes and the owner finds it in the render.

Every function here recomputes from the actual artefact, at build time, every build.
"""
import json
import os

from PIL import Image, ImageFont

CANVAS_W, CANVAS_H = 1080.0, 1920.0

# Render-px per (PIL-unit x font size), measured off her template.
K_PLAIN = 4.39
# A text_template's child carries this extra internal scale on top of K_PLAIN.
K_TPL = 2.44


# --------------------------------------------------------------------- text
def pil_units(font_path, text):
    """Widest line of `text` in PIL units (bbox at size 100, divided by 100)."""
    f = ImageFont.truetype(font_path, 100)
    return max((f.getbbox(l)[2] - f.getbbox(l)[0]) for l in text.split("\n")) / 100.0


def text_width_px(font_path, text, size, scale=1.0, template=False):
    """Rendered width in canvas pixels."""
    return pil_units(font_path, text) * size * K_PLAIN * (K_TPL if template else 1.0) * scale


def content_of(mat):
    return json.loads(mat["content"])


def style_font(mat):
    c = content_of(mat)
    st = (c.get("styles") or [{}])[0]
    return (st.get("font") or {}).get("path", ""), st.get("size", 15)


def fits_donor(child_mat, new_text):
    """Can `new_text` live in this torn-paper row without spilling?

    The paper graphic is authored for the donor string and does NOT grow. "Its Own
    Mistakes" measured 495.6px against the 369.7px "5 Sub Agents" occupies, overflowed,
    and threw a giant "akes" across the frame. THE_METHOD calls measuring this rule #1 -
    and in version berry the enforcement was a COMMENT in base.py, with no PIL import
    anywhere in the file. Now it runs.

    -> (ok, new_px, donor_px, ratio)
    """
    fp, size = style_font(child_mat)
    old = content_of(child_mat)["text"]
    if not fp or not os.path.exists(fp):
        raise RuntimeError("cannot measure: font missing at %r" % (fp,))
    o = text_width_px(fp, old, size, template=True)
    n = text_width_px(fp, new_text, size, template=True)
    return (n <= o + 1e-6), round(n, 1), round(o, 1), (round(n / o, 3) if o else 0.0)


def gap_after_x(prev_mat, prev_text, prev_x, prev_scale, prev_tpl,
                new_mat, new_text, new_scale, new_tpl, gap_px):
    """transform.x placing `new_text` a fixed gap after `prev_text`'s right edge.

    This is the rule for two title words sharing a line. The obvious alternative -
    inheriting the x of the word being replaced - is wrong because transform.x is a
    CENTRE: a longer replacement grows leftwards into the word before it, which is how
    "Claude" and "catch" once read as one smashed word. Preserving the old LEFT edge is
    also wrong, in the other direction: it reproduces the template's spacing for a word of
    a different length and pushes the replacement toward the frame edge.

    Solving from the neighbour's measured right edge is correct at any word length, and it
    is why the gap can be a house constant instead of a per-title hand-solve.
    """
    fp_p, size_p = style_font(prev_mat)
    fp_n, size_n = style_font(new_mat)
    wp = text_width_px(fp_p, prev_text, size_p, prev_scale, prev_tpl)
    wn = text_width_px(fp_n, new_text, size_n, new_scale, new_tpl)
    prev_right = CANVAS_W / 2.0 + prev_x * (CANVAS_W / 2.0) + wp / 2.0
    new_centre = prev_right + gap_px + wn / 2.0
    return round((new_centre - CANVAS_W / 2.0) / (CANVAS_W / 2.0), 4)


def left_aligned_x(child_mat, old_text, new_text, old_x, scale=1.0, template=True):
    """New transform.x that keeps the string's LEFT EDGE where the old one started.

    A title row inherits the x of the word it replaced. That x is a CENTRE, so a longer
    replacement grows leftwards and collides with the word before it - which is how
    "Claude" and "catch" ended up reading as one smashed word. Preserving the left edge
    preserves the gap, at any word length, without a hand-solved constant.
    """
    fp, size = style_font(child_mat)
    wo = text_width_px(fp, old_text, size, scale, template)
    wn = text_width_px(fp, new_text, size, scale, template)
    return round(old_x + ((wn - wo) / 2.0) / (CANVAS_W / 2.0), 4)


# -------------------------------------------------------------------- optical
def content_box(path):
    """Bounding box of the actually-visible pixels, ignoring transparent padding."""
    im = Image.open(path).convert("RGBA")
    alpha = im.split()[-1].point(lambda v: 255 if v > 16 else 0)
    return im.size, (alpha.getbbox() or (0, 0) + im.size)


def optical_scale(path, target_content_px=243.0):
    """Segment scale that makes the VISIBLE artwork `target_content_px` tall.

    Scale is not size. The ChatGPT mark fills 50.6% of its canvas and the Claude icon
    fills 100%, so at one shared scale they render at visibly different sizes - which
    shipped. 243px is the owner's measured logo height.
    """
    (w, h), (x0, y0, x1, y1) = content_box(path)
    fit = min(CANVAS_W / w, CANVAS_H / h)
    return round(target_content_px / ((y1 - y0) * fit), 4)


# ----------------------------------------------------------- card regions
def regions_path(card_png):
    return os.path.splitext(card_png)[0] + ".regions.json"


def load_regions(card_png):
    """Named pixel rectangles inside a card we drew ourselves.

    We DRAW these cards, so the coordinate of every element is known exactly at draw time.
    Version berry threw that knowledge away and re-derived anchors afterwards by eye. The
    card generator now emits a manifest, and an annotation names a region instead of
    carrying a float that silently rots the next time the card is redrawn.
    """
    p = regions_path(card_png)
    if not os.path.exists(p):
        return {}
    return json.load(open(p, encoding="utf-8"))


def card_anchor(card_png, px, py, seg_scale, seg_y):
    """Where a point INSIDE a card lands on the canvas, in half-canvas units."""
    w, h = Image.open(card_png).size
    fit = min(CANVAS_W / w, CANVAS_H / h)
    cx_px = CANVAS_W / 2.0 + (px - w / 2.0) * fit * seg_scale
    cy_px = (CANVAS_H / 2.0 - seg_y * (CANVAS_H / 2.0)) + (py - h / 2.0) * fit * seg_scale
    return (round((cx_px - CANVAS_W / 2.0) / (CANVAS_W / 2.0), 4),
            round((CANVAS_H / 2.0 - cy_px) / (CANVAS_H / 2.0), 4))


def card_region_target(card_png, region, seg_scale, seg_y, pad=1.18, place="on"):
    """-> (target_cx, target_cy, target_w_px) for a named region of a card.

    `pad` widens the mark past the text it rings, so a circle encircles the value rather
    than striking through it.

    `place` says where the mark sits relative to the region. A circle or a box goes "on"
    it; an underline goes "under" it, and centring an underline on the thing it underlines
    strikes it through instead. This is a NAME for the same reason bands are names - the
    alternative is a hand-tuned vertical offset that is right for one card and silently
    wrong for the next.
    """
    regs = load_regions(card_png)
    if region not in regs:
        raise KeyError("card %s has no region %r; known: %s"
                       % (os.path.basename(card_png), region, sorted(regs)))
    x0, y0, x1, y1 = regs[region]
    w, h = Image.open(card_png).size
    fit = min(CANVAS_W / w, CANVAS_H / h)
    py = (y0 + y1) / 2.0
    if place == "under":
        py = y1 + 0.4 * (y1 - y0)
    elif place == "over":
        py = y0 - 0.4 * (y1 - y0)
    cx, cy = card_anchor(card_png, (x0 + x1) / 2.0, py, seg_scale, seg_y)
    return cx, cy, (x1 - x0) * fit * seg_scale * pad


def ink_box(art):
    """Bounding box of a sticker's actual marks inside its own canvas."""
    return art.split()[-1].point(lambda v: 255 if v > 24 else 0).getbbox()


def place_sticker_on(art, target_cx, target_cy, target_w_px):
    """Solve (scale, x, y) so a sticker's INK lands on a target rect.

    Stickers cannot be positioned by treating their canvas as the mark: the red circle's
    ink centre sits at (0.457, 0.411) of its canvas, not (0.5, 0.5), so placing by canvas
    centre puts the mark somewhere other than where you aimed.
    """
    ink = ink_box(art)
    aw, ah = art.size
    fit = min(CANVAS_W / aw, CANVAS_H / ah)
    ink_w_frac = (ink[2] - ink[0]) / float(aw)
    scale = target_w_px / (aw * fit * ink_w_frac)
    dx = ((ink[0] + ink[2]) / 2.0 / aw - 0.5) * aw * fit * scale
    dy = ((ink[1] + ink[3]) / 2.0 / ah - 0.5) * ah * fit * scale
    cx_px = CANVAS_W / 2.0 + target_cx * (CANVAS_W / 2.0) - dx
    cy_px = CANVAS_H / 2.0 - target_cy * (CANVAS_H / 2.0) - dy
    return (round(scale, 4),
            round((cx_px - CANVAS_W / 2.0) / (CANVAS_W / 2.0), 4),
            round((CANVAS_H / 2.0 - cy_px) / (CANVAS_H / 2.0), 4))


ARTIST_CACHE = os.path.join(os.environ.get("LOCALAPPDATA", ""), "CapCut", "User Data",
                            "Cache", "artistEffect")


def sticker_art(resource_id):
    """The annotation sticker's real artwork, from CapCut's own cache.

    They are ANIMATED and several draw themselves in, so frame 0 is often completely
    empty - rendering frame 0 made a correctly-placed underline look like it was missing.
    Take the frame with the most ink: the sticker fully drawn.
    """
    base = os.path.join(ARTIST_CACHE, str(resource_id))
    if not os.path.isdir(base):
        return None
    for sub in os.listdir(base):
        p = os.path.join(base, sub, "final.gif")
        if not os.path.exists(p):
            continue
        try:
            im = Image.open(p)
            best, best_ink = None, -1
            for i in range(getattr(im, "n_frames", 1)):
                im.seek(i)
                f = im.convert("RGBA")
                bb = ink_box(f)
                area = 0 if bb is None else (bb[2] - bb[0]) * (bb[3] - bb[1])
                if area > best_ink:
                    best, best_ink = f, area
            return best
        except Exception:
            return None
    return None
