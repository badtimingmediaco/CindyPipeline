# -*- coding: utf-8 -*-
"""BANDS - the bridge between a spec's band NAME and house_layout's measured laws.

house_layout.py stays the single source of truth for every measured constant; this module
does not restate any of them. What it adds is the lookup that lets a spec say

    "band": "top"

instead of

    y=0.7156, scale=0.4419

which is the whole point: a name cannot rot when the asset changes, and a number can.
"""
import os
import sys

_STATE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _STATE not in sys.path:
    sys.path.insert(0, _STATE)

import house_layout as HL          # noqa: E402  the measured laws, unmodified

ANNOTATE = HL.ANNOTATE
place_sticker = HL.place_sticker

# Marks whose ARTWORK IS NOT THE MARK. `place_sticker_on()` fits a sticker's whole ink box
# to the target, which is correct only when the ink is the mark. `circle` draws a small
# flat ellipse with four arrows pointing at it from above: the ink is 0.579 x 0.471 of the
# canvas but the ellipse alone is roughly the bottom half of that, so fitting the ink to
# "9.4 / 10" rendered an ellipse far too small, sitting low. It shipped twice.
#
# `circle_sign` is a plain hand-drawn oval (ink 0.814 x 0.646, no decoration) and is the
# correct mark for encircling a value.
DECORATED_MARKS = {
    "circle": "ellipse plus four arrows above it - the ink is not the mark. "
              "Use circle_sign to encircle a value.",
    "highlight_box": "box plus a curved arrow entering from the top left.",
}
V1_VOLUME = HL.V1_VOLUME
SUCCESS_VOLUME = HL.SUCCESS_VOLUME


def __getattr__(name):
    """Anything not defined here comes straight from house_layout.

    Re-exporting constants by hand is how two copies of a measured value come to exist,
    and then to disagree. There is one copy: house_layout's.
    """
    try:
        return getattr(HL, name)
    except AttributeError:
        raise AttributeError("neither engine.layout nor house_layout defines %r" % name)

# A 2-up logo row. house_layout's LOGO_X is the owner-measured 3-up row; this pair is what
# the accepted Claude Reviewer build shipped at, kept so blueberry reproduces it exactly.
# Provenance is different from the 3-up row - this is "shipped and accepted", not
# "measured off her hand-finish" - and it is labelled that way on purpose.
LOGO_X_2UP = (-0.26, 0.26)

# The house text row for a full-width line with no asset under it.
LOWER_TEXT_Y = 0.66

# Gap between two title words sharing one visual line ("Claude  catch").
#
# Provenance: 34px is what the owner accepted on the Claude Reviewer title. It is not a
# derived quantity - one space of that font at that size is 14.6px, and the template's own
# "Claude into" gap is 85px, because "into" is a shorter word and the designer centred a
# different composition. Left-aligning to the old word's edge reproduces the template's
# 85px and pushes the second word toward the frame edge; one space is too tight to read as
# separate words.
#
# So it lives here, with the other measured house constants, and a spec names the
# RELATIONSHIP ("catch" sits after "Claude") rather than the number.
TITLE_WORD_GAP_PX = 34.0

# Anything on screen during the opening title lives in the lower third so it clears the
# title rows. Midpoint of house_layout's measured TITLE_BAND.
TITLE_BAND_Y = round(sum(HL.TITLE_BAND) / 2.0, 4)

# The title band is sized by WIDTH, not height. A top-band meme is height-driven at 430px
# because it owns the frame; a title-band clip shares the frame with three title rows, so
# height-driving it made the hook clip 33% larger than the version that shipped. 430px
# wide is what the accepted build used.
TITLE_BAND_W = 430.0


def media_geom(band, w, h):
    """-> (scale, centre_y, displayed_h_px, label_y) for an asset in `band`."""
    if band == "centre":
        return HL.card_geom(w, h)
    if band == "title":
        fit = min(1080.0 / w, 1920.0 / h)
        sc = round(min(TITLE_BAND_W / (w * fit), HL.MAX_H / (h * fit)), 4)
        dh = h * fit * sc
        return sc, TITLE_BAND_Y, dh, TITLE_BAND_Y - (dh / 2) / 960.0 + HL.LABEL_STRADDLE
    return HL.meme_geom(w, h)


def default_band(kind):
    return {"meme": "top", "card": "centre", "gfx": "title",
            "text": "lower", "logo": "logo", "logo_label": "logo_label"}.get(kind, "top")


def logo_slot(slot, n_logos=2):
    if slot == "centre":
        return 0.0
    xs = LOGO_X_2UP if n_logos <= 2 else (HL.LOGO_X[0], HL.LOGO_X[2])
    return xs[0] if slot == "left" else xs[1]


def text_y(band, last_label_y):
    """A text beat's row. 'label' means the row belonging to the asset just placed."""
    if band == "label":
        return last_label_y
    if band == "logo_header":
        return HL.LOGO_HEADER_Y
    if band == "logo_label":
        return HL.LOGO_LABEL_Y
    if band == "title":
        return TITLE_BAND_Y
    return LOWER_TEXT_Y
