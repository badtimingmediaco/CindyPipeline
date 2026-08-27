# -*- coding: utf-8 -*-
"""Reading and writing the draft. The four-copy law lives here and nowhere else.

CapCut keeps FOUR copies of a timeline:

    template-2.tmp                    <- canonical
    draft_content.json                <- root mirror
    Timelines/<uuid>/template-2.tmp   <- CapCut actually reads this one
    Timelines/<uuid>/draft_content.json

build_seo.py wrote only the root pair. CapCut read the stale Timelines copy, showed an
empty timeline, and saved that back over a finished verified build - every asset gone.
That bug existed in one fork and not the other because each fork had its own save().
There is now exactly one save().
"""
import datetime
import json
import os
import shutil

from . import paths


def canon(draft):
    p = os.path.join(draft, "template-2.tmp")
    return p if os.path.exists(p) else os.path.join(draft, "draft_content.json")


def timeline_copies(draft):
    """Every file that must end up byte-identical to the canonical."""
    out = [os.path.join(draft, "draft_content.json")]
    tl = os.path.join(draft, "Timelines")
    if os.path.isdir(tl):
        for sub in os.listdir(tl):
            sd = os.path.join(tl, sub)
            if os.path.isdir(sd):
                for name in ("template-2.tmp", "draft_content.json"):
                    if os.path.exists(os.path.join(sd, name)):
                        out.append(os.path.join(sd, name))
    return out


def load(draft):
    return json.load(open(canon(draft), encoding="utf-8"))


def save(draft, d):
    p = canon(draft)
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False)
    for t in timeline_copies(draft):
        shutil.copy2(p, t)
    return 1 + len(timeline_copies(draft))


def backup(draft, tag):
    os.makedirs(paths.BACKUPS, exist_ok=True)
    dst = os.path.join(paths.BACKUPS,
                       f"{tag}_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".tmp")
    shutil.copy2(canon(draft), dst)
    return dst


# ---------------------------------------------------------------- provenance
#
# 2026-08-26: nine rebuilds of CZ_AISandwich_20260825_v1, each one `rm -rf` plus a fresh
# template clone, destroyed a full day of the owner's hand edits. Every safeguard in this
# pipeline guarded the WRITE ("is CapCut closed?") and none guarded the TARGET ("has this
# draft moved since I made it?"). Closed is not the same as untouched, and a delivered
# draft is not scratch space.
#
# So the engine now records a fingerprint of what it produced, and refuses to build over a
# draft that no longer matches it.
import hashlib


def fingerprint(draft):
    """sha256 of the canonical timeline - what the draft actually contains right now."""
    return hashlib.sha256(open(canon(draft), "rb").read()).hexdigest()


LEDGER = os.path.join(paths.STATE, "build_provenance.json")


def _key(draft):
    """One canonical key per draft.

    Keyed by the raw string, "C:/CapCut Drafts/X" and "C:\\CapCut Drafts\\X" became two
    separate entries, so build.py's record and enforce_track_order's record landed in
    different slots and the guard cried "edited" on an untouched draft. A guard that
    false-alarms gets switched off, which would have defeated the whole point.
    """
    return os.path.normcase(os.path.abspath(draft)).replace("\\", "/")


def _ledger():
    if os.path.exists(LEDGER):
        try:
            return json.load(open(LEDGER, encoding="utf-8"))
        except Exception:
            return {}
    return {}


def record_build(draft, name=None, segments=None):
    """Remember what we handed over, so we can tell later if it was edited.

    Keyed by DRAFT PATH, not by spec name, so any script that writes to a draft can
    update it. That matters because `enforce_track_order.py` is the LAST write of a
    build - recording the fingerprint before it runs would store a hash the finished
    draft never has, and every later build would cry "edited" on its own output.
    """
    led = _ledger()
    k = _key(draft)
    rec = led.get(k, {})
    rec.update({"sha256": fingerprint(draft),
                "built_at": datetime.datetime.now().isoformat(timespec="seconds")})
    if name:
        rec["name"] = name
    if segments is not None:
        rec["segments"] = segments
    led[k] = rec
    json.dump(led, open(LEDGER, "w", encoding="utf-8"), indent=1, sort_keys=True)
    return rec["sha256"]


def check_untouched(draft, name=None):
    """-> (ok, message). False means the draft has been edited since we built it."""
    if not os.path.isdir(draft):
        return True, "draft does not exist yet"
    rec = _ledger().get(_key(draft))
    if not rec:
        return False, ("%s already exists but this pipeline has no record of building it, "
                       "so its contents are unknown." % os.path.basename(draft))
    now = fingerprint(draft)
    if now == rec.get("sha256"):
        return True, "unchanged since the engine built it at %s" % rec.get("built_at")
    return False, ("%s has been EDITED since the engine built it at %s."
                   " Recorded sha %s, current sha %s."
                   " Rebuilding destroys that work and it is NOT recoverable."
                   % (os.path.basename(draft), rec.get("built_at"),
                      (rec.get("sha256") or "?")[:16], now[:16]))
