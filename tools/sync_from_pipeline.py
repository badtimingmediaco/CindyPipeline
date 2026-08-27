#!/usr/bin/env python3
"""Report (and optionally fix) drift between a live pipeline and this plugin checkout.

    python tools/sync_from_pipeline.py                    # report only
    python tools/sync_from_pipeline.py --apply            # copy live -> plugin
    python tools/sync_from_pipeline.py --pipeline <dir>

The pipeline folder is where reels actually get built, so it is where fixes get made
first - mid-build, under time pressure, straight into `_state/`. The plugin is what
teammates receive. Nothing keeps the two in step, and nothing announces when they part.

By the 5.2.0 release the gap had reached six engine modules, five scripts and three
learning files: every teammate was building with a version of the engine that the machine
next to them had already outgrown, and no one could see it. Run this before every release.

Direction is deliberately one-way. `setup.py` already pushes plugin -> pipeline on every
install; this is the return leg, and it only ever reads the live folder.
"""
import argparse
import filecmp
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

# (live path relative to the pipeline home, plugin path relative to the repo root)
# Only reference content. Never a draft, never a build artefact, never paths.json.
PAIRS = [
    ("_state/engine",     "scripts/engine",            "*.py"),
    ("_state/learnings",  "kit/state/learnings",       "*.md"),
]
FILES = [
    ("_state/build.py",                "scripts/build.py"),
    ("_state/verify_build.py",         "scripts/verify_build.py"),
    ("_state/enforce_track_order.py",  "scripts/enforce_track_order.py"),
    ("_state/house_layout.py",         "scripts/house_layout.py"),
    ("_state/visual_gate.py",          "scripts/visual_gate.py"),
    ("_state/meme_qa.py",              "scripts/meme_qa.py"),
    ("_state/meme_sheet.py",           "scripts/meme_sheet.py"),
    ("_state/meme_catalog.json",       "scripts/meme_catalog.json"),
    ("_state/meme_catalog.json",       "kit/state/meme_catalog.json"),
    ("_state/sfx_map.json",            "kit/state/sfx_map.json"),
    ("_state/sticker_kit.json",        "kit/state/sticker_kit.json"),
    ("_state/master_reference.md",     "kit/state/master_reference.md"),
]
# Banks: new files ship, but a file the editor changed locally is NOT pulled back - their
# machine is not the source of truth for a shared asset.
BANKS = [
    ("04_assets/memes/bank", "kit/memes/bank"),
    ("04_assets/logos",      "kit/logos"),
    ("_sfx/Cindiezhu sfx",   "kit/sfx"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pipeline",
                    default=os.path.join(os.path.expanduser("~"), "Documents", "CindyPipeline"))
    ap.add_argument("--apply", action="store_true", help="actually copy; default is a report")
    a = ap.parse_args()
    pipe = os.path.abspath(a.pipeline)
    if not os.path.isdir(pipe):
        print("no pipeline at %s" % pipe)
        return 2

    todo = []

    def consider(src, dst, why):
        if not os.path.exists(src):
            return
        if not os.path.exists(dst):
            todo.append((src, dst, "NEW    " + why))
        elif not filecmp.cmp(src, dst, shallow=False):
            todo.append((src, dst, "DIFFERS " + why))

    for lrel, prel, pat in PAIRS:
        ld, pd = os.path.join(pipe, *lrel.split("/")), os.path.join(REPO, *prel.split("/"))
        ext = pat.lstrip("*")
        if not os.path.isdir(ld):
            continue
        for f in sorted(os.listdir(ld)):
            if f.endswith(ext):
                consider(os.path.join(ld, f), os.path.join(pd, f), "%s/%s" % (prel, f))

    for lrel, prel in FILES:
        consider(os.path.join(pipe, *lrel.split("/")),
                 os.path.join(REPO, *prel.split("/")), prel)

    # Banks are add-only: report a missing file, stay silent about a changed one.
    for lrel, prel in BANKS:
        ld, pd = os.path.join(pipe, *lrel.split("/")), os.path.join(REPO, *prel.split("/"))
        if not os.path.isdir(ld):
            continue
        for f in sorted(os.listdir(ld)):
            s, d = os.path.join(ld, f), os.path.join(pd, f)
            if os.path.isfile(s) and not os.path.exists(d):
                todo.append((s, d, "NEW     %s/%s" % (prel, f)))

    if not todo:
        print("in sync with %s - nothing to ship" % pipe)
        return 0

    print("%d file(s) differ between the live pipeline and this checkout:\n" % len(todo))
    for _s, _d, why in todo:
        print("  " + why)
    if not a.apply:
        print("\nreport only. Re-run with --apply to copy them in, then review the diff.")
        return 1
    for s, d, _why in todo:
        os.makedirs(os.path.dirname(d), exist_ok=True)
        shutil.copy2(s, d)
    print("\ncopied %d file(s). Now: git diff, bump the version, commit." % len(todo))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
