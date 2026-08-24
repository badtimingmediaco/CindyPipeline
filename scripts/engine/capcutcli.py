# -*- coding: utf-8 -*-
"""The CapCut CLI, ffprobe, and the snapshot-freshness law."""
import hashlib
import json
import os
import shutil
import subprocess

from . import draftio, paths


def cli(*args):
    r = subprocess.run(["capcut", *args], capture_output=True, text=True, shell=True)
    try:
        return json.loads(r.stdout)
    except Exception:
        return {"ok": False, "raw": (r.stdout + r.stderr)[:300]}


def capcut_running():
    """CapCut must be CLOSED for every external write - it never re-reads from disk while
    open, and its next autosave destroys the build."""
    try:
        r = subprocess.run(["tasklist"], capture_output=True, text=True)
        return "capcut" in r.stdout.lower()
    except Exception:
        return False


def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                        "-show_entries", "stream=width,height", "-show_entries",
                        "format=duration", "-of", "json", path],
                       capture_output=True, text=True)
    j = json.loads(r.stdout or "{}")
    st = (j.get("streams") or [{}])[0]
    try:
        dur = float(j["format"]["duration"])
    except Exception:
        dur = None                      # stills have no duration
    return int(st.get("width", 0)), int(st.get("height", 0)), dur


def probe_audio(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", path], capture_output=True, text=True)
    return float(r.stdout.strip() or 1.0)


def sync_snapshots(draft, roots=None):
    """add-video does NOT overwrite an existing snapshot of the same filename, so a
    regenerated PNG silently keeps the OLD art. Hash every snapshot against its source."""
    roots = roots or (paths.GFX, paths.BANK, paths.LOGOS)
    d = draftio.load(draft)
    srcs = {}
    for v in d["materials"].get("videos", []):
        p = v.get("path") or ""
        if os.sep + "assets" + os.sep in p or "/assets/" in p:
            srcs[os.path.basename(p)] = p
    fixed = 0
    for root in roots:
        if not os.path.isdir(root):
            continue
        for fn in os.listdir(root):
            snap = srcs.get(fn)
            if not snap or not os.path.exists(snap):
                continue
            a = hashlib.sha256(open(os.path.join(root, fn), "rb").read()).hexdigest()
            b = hashlib.sha256(open(snap, "rb").read()).hexdigest()
            if a != b:
                shutil.copy2(os.path.join(root, fn), snap)
                fixed += 1
    return fixed
