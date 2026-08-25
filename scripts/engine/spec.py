# -*- coding: utf-8 -*-
"""The per-video spec: what to say, when. Never where, how big, or what colour.

THE ONE RULE
------------
A spec may not contain geometry. No x, no y, no scale, no anchor, no pixel width. It
carries only the ~50 values that are genuinely a choice for this video - the clause
timings, which asset, and the copy - and names a BAND instead of a coordinate.

This is enforced, not requested: `validate()` hard-fails on a forbidden key. That
matters because the failure mode being fixed is not "someone typed a bad number", it is
"a number that was correctly solved once got pasted forward into a build where it was
wrong". If the number cannot live in the spec, it cannot be pasted forward. It has to be
re-solved from the artefact on every build, by measure.py.

Everything else the validator does is a check that used to exist only as a rule in a
markdown file that a build could silently skip:

  * every asset resolves on disk, before anything is written
  * every meme is in the curated catalog with use == "ok" - the catalog existed in
    version berry and NO script read it, so any filename that sounded right was accepted
  * every SFX name exists in the locked bank - never invent a filename
  * every annotation names a card REGION and a mark that is in the kit
  * beats are ordered, non-degenerate, and inside the video
"""
import json
import os

from . import paths

# A spec carrying any of these is rejected. The message names the band to use instead.
FORBIDDEN_KEYS = {
    "x": "position is decided by `band`, not by the spec",
    "y": "position is decided by `band`, not by the spec",
    "scale": "size is solved by measure.py from the asset itself",
    "target_w": "size is solved from the band's measured width law",
    "width_px": "size is solved from the band's measured width law",
    "transform": "position is decided by `band`",
    "cy": "position is decided by `band`",
    "label_y": "a label's row is derived from the asset it belongs to",
    "size": "type size comes from the donor material",
    "anchor": "anchoring is a property of the band",
    "top": "position is decided by `band`",
}

KINDS = {"meme", "card", "gfx", "text", "logo", "logo_label", "stack"}

# Bands are NAMES of measured placement laws in house_layout.py, not coordinates.
BANDS = {"top", "centre", "title", "label", "lower", "logo", "logo_header", "logo_label"}


class SpecError(Exception):
    pass


def _forbidden(obj, where, errs):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in FORBIDDEN_KEYS:
                errs.append("%s carries geometry key %r - %s" % (where, k, FORBIDDEN_KEYS[k]))
            _forbidden(v, where + "." + str(k), errs)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            _forbidden(v, "%s[%d]" % (where, i), errs)


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def validate(spec, strict_catalog=True):
    """-> list of error strings. Empty means the spec may be built."""
    errs = []
    for req in ("name", "draft", "end", "beats"):
        if req not in spec:
            errs.append("spec is missing required key %r" % req)
    if errs:
        return errs

    end = float(spec["end"])
    catalog = {}
    banned = {}
    if os.path.exists(paths.MEME_CATALOG):
        c = json.load(open(paths.MEME_CATALOG, encoding="utf-8"))
        catalog = c.get("clips", {})
        for key in ("banned_burned_text", "banned_cutout", "banned_wrong_mapping"):
            banned.update(c.get(key, {}))

    sfx_bank = set()
    if os.path.isdir(paths.SFXDIR):
        sfx_bank = {f for f in os.listdir(paths.SFXDIR)}

    from . import layout as HL          # late import: house_layout needs sys.path set up

    for i, b in enumerate(spec["beats"]):
        where = "beat[%d]" % i
        _forbidden(b, where, errs)

        kind = b.get("kind")
        if kind not in KINDS:
            errs.append("%s has unknown kind %r (expected one of %s)"
                        % (where, kind, sorted(KINDS)))
            continue

        t = b.get("t")
        if not (isinstance(t, list) and len(t) == 2):
            errs.append("%s has no [start, end]" % where)
            continue
        if not (0 <= t[0] < t[1] <= end + 1e-6):
            errs.append("%s window %s is degenerate or runs past end=%s" % (where, t, end))

        band = b.get("band")
        if band is not None and band not in BANDS:
            errs.append("%s names unknown band %r (known: %s)"
                        % (where, band, sorted(BANDS)))

        if kind in ("meme", "card", "gfx", "logo"):
            ref = b.get("asset")
            if not ref:
                errs.append("%s (%s) has no asset" % (where, kind))
            else:
                p = paths.resolve_asset(ref)
                if not os.path.exists(p):
                    errs.append("%s asset not on disk: %s" % (where, p))
                if kind == "meme":
                    stem = os.path.splitext(os.path.basename(p))[0]
                    if stem in banned:
                        errs.append("%s meme %r is BANNED: %s" % (where, stem, banned[stem]))
                    elif stem not in catalog:
                        if strict_catalog:
                            errs.append("%s meme %r is not in meme_catalog.json - it has "
                                        "never been looked at, so it cannot ship"
                                        % (where, stem))
                    elif catalog[stem].get("use") != "ok":
                        errs.append("%s meme %r is catalogued use=%r, not 'ok'"
                                    % (where, stem, catalog[stem].get("use")))

        if kind in ("text", "logo_label", "stack") and not (b.get("text") or b.get("lines")):
            errs.append("%s (%s) has no text" % (where, kind))

        sfx = b.get("sfx")
        if sfx and sfx_bank and sfx not in sfx_bank:
            errs.append("%s INVENTED SFX FILENAME %r - not in the locked bank"
                        % (where, sfx))

        for j, a in enumerate(b.get("annotate") or []):
            aw = "%s.annotate[%d]" % (where, j)
            if a.get("mark") not in HL.ANNOTATE:
                errs.append("%s mark %r is not in the sticker kit" % (aw, a.get("mark")))
            if not a.get("region"):
                errs.append("%s has no region - an annotation names a region of the card, "
                            "never a coordinate" % aw)
            at = a.get("t")
            if not (isinstance(at, list) and len(at) == 2 and at[0] < at[1]):
                errs.append("%s has no valid [start, end]" % aw)

    starts = [b["t"][0] for b in spec["beats"] if isinstance(b.get("t"), list)]
    if starts != sorted(starts):
        errs.append("beats are not in time order - sort them, so the file reads as the "
                    "video plays")
    return errs


def density(spec):
    """Beats per 80 seconds, and the segments those beats will become.

    Careful: the owner's reference figure of 242 per 80s counts SEGMENTS, not beats. One
    beat becomes a media segment plus maybe a label plus an SFX hit, so comparing 37 beats
    against 242 segments is comparing different units - which is how the last build talked
    itself into thinking it was four times sparser than it was. The real segment count is
    only knowable after the build, so verify_build.py reports it against the reference.
    """
    n = len(spec["beats"])
    est = 0
    for b in spec["beats"]:
        est += 1                                    # the media or text layer itself
        est += 1 if b.get("label") else 0
        est += 1 if b.get("sfx") else 0
        est += 2 * len(b.get("annotate") or [])     # sticker + its own SFX hit
    per80 = round(n * 80.0 / float(spec["end"]), 1)
    return per80, n, round(est * 80.0 / float(spec["end"]), 1), est


def require_valid(spec, strict_catalog=True):
    errs = validate(spec, strict_catalog)
    if errs:
        raise SpecError("spec rejected - %d problem(s):\n  - %s"
                        % (len(errs), "\n  - ".join(errs)))
    return spec
