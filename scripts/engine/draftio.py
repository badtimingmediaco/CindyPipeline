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
