#!/usr/bin/env python3
"""Enforce the CINDY_REEL_FACTORY track order and renumber track_render_index.

Section 7b check 2: this must be the LITERAL LAST WRITE of a session - zero CLI
writes after it, because any CLI write can reshuffle the track array. The only
permitted followers are the mirror sync (plain file copy) and read-only
lint/diagnose.

Order (bottom -> top):
  V1 talking head (0) -> adjust (1) -> memes -> logo icons -> logo labels ->
  screen-rec placeholders -> captions -> stickers -> title -> CTA
Audio tracks keep their relative order after the visual stack.

Usage: python enforce_track_order.py <draft_dir> [--dry-run]
"""
import json, os, sys, shutil, datetime

# track "name" -> rank. Unnamed/unknown visual tracks sort by their old index
# after the named ones but before title/CTA.
RANK = {
    "V1": 0,
    "adjust": 1,
    "memes": 10,
    "logo_icons": 20,
    "logo_labels": 21,
    "placeholders": 30,
    "captions": 40,
    "stickers": 50,
    "title": 60,
    "cta": 70,
}


def canonical_file(draft_dir):
    """Return (canonical_path, mirror_path). template-2.tmp wins on modern CapCut."""
    tmpl = os.path.join(draft_dir, "template-2.tmp")
    mirror = os.path.join(draft_dir, "draft_content.json")
    if os.path.exists(tmpl):
        return tmpl, mirror
    return mirror, None


def rank_of(track, old_index):
    name = (track.get("name") or "").strip()
    if name in RANK:
        return (RANK[name], old_index)
    # lanes are suffixed (stickers1, stickers2, sfx3...) - match the prefix so
    # split lanes stay together instead of falling through to the generic bucket
    for key, rank in RANK.items():
        if name.startswith(key):
            return (rank, old_index)
    ttype = track.get("type")
    if ttype == "video":
        # a video track with segments that is not V1 -> treat as overlay media
        return (10, old_index)
    if ttype == "adjust":
        return (1, old_index)
    if ttype == "audio":
        return (900, old_index)
    return (80, old_index)


def enforce(draft_dir, dry_run=False):
    canon, mirror = canonical_file(draft_dir)
    d = json.load(open(canon, encoding="utf-8"))
    tracks = d["tracks"]

    # 1. drop empty video tracks left over from the template (they hijack the
    #    "main video track" that the proxy renderer and CapCut both read).
    before = len(tracks)
    tracks = [t for t in tracks if not (t.get("type") == "video" and not t.get("segments"))]
    dropped = before - len(tracks)

    # 2. stable sort into house order
    tracks = [t for _, t in sorted(((rank_of(t, i), t) for i, t in enumerate(tracks)),
                                   key=lambda p: p[0])]
    d["tracks"] = tracks

    # 3. every segment's track_render_index == its track's array index
    fixed = 0
    for i, t in enumerate(tracks):
        for s in t.get("segments", []):
            if s.get("track_render_index") != i:
                s["track_render_index"] = i
                fixed += 1

    report = {
        "canonical": os.path.basename(canon),
        "empty_video_tracks_dropped": dropped,
        "render_index_fixed": fixed,
        "order": [(i, t.get("type"), t.get("name") or "", len(t.get("segments", [])))
                  for i, t in enumerate(tracks)],
    }
    if dry_run:
        report["dry_run"] = True
        return report

    # backup then write canonical, then mirror it with a plain copy
    bak = os.path.join(draft_dir, "_order_bak_" +
                       datetime.datetime.now().strftime("%H%M%S") + ".json")
    shutil.copy2(canon, bak)
    json.dump(d, open(canon, "w", encoding="utf-8"), ensure_ascii=False)
    if mirror:
        shutil.copy2(canon, mirror)
        report["mirrored"] = True
    return report


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    print(json.dumps(enforce(sys.argv[1], "--dry-run" in sys.argv), indent=1))
