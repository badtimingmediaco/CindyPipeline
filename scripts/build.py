# -*- coding: utf-8 -*-
"""Build a reel from a spec.

    python _state/build.py <spec.json>                  # foundation + overlays
    python _state/build.py <spec.json> --check           # validate only, write nothing
    python _state/build.py <spec.json> --stage overlays  # just the overlay pass

The spec carries the ~50 values that are a choice for this video. Everything else - every
coordinate, every scale, every anchor - is solved from the artefacts by the engine, on
every build. See _state/engine/spec.py for why that is enforced rather than encouraged.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine import capcutcli, draftio, foundation, overlays, paths, spec as specmod


def draft_dir(sp):
    ref = sp["draft"]
    if os.path.isabs(ref):
        return ref
    cfg = os.path.join(paths.STATE, "paths.json")
    root = None
    if os.path.exists(cfg):
        root = json.load(open(cfg, encoding="utf-8")).get("capcut_drafts_dir")
    if not root:
        root = os.path.join(os.environ.get("LOCALAPPDATA", ""), "CapCut Drafts")
    return os.path.join(root, ref)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--stage", default="all",
                    choices=["all", "foundation", "overlays"])
    ap.add_argument("--check", action="store_true",
                    help="validate the spec and report density, then stop")
    ap.add_argument("--allow-uncached", action="store_true",
                    help="place an annotation whose artwork CapCut has not cached; it "
                         "cannot be visually checked, so this is never the default")
    ap.add_argument("--reference", type=float, default=242.0,
                    help="beats-per-80s of the reference reel to compare density against")
    a = ap.parse_args(argv)

    sp = specmod.load(a.spec)
    errs = specmod.validate(sp)
    per80, n, est80, est = specmod.density(sp)
    print("spec: %s | %d beats (%.1f per 80s) | %.2fs" % (sp["name"], n, per80, sp["end"]))
    print("      ~%d segments expected (%.1f per 80s) against a reference of %.0f"
          % (est, est80, a.reference))
    if est80 < a.reference * 0.5:
        print("      ! under half the reference reel - walk the transcript clause by "
              "clause before shipping")
    if errs:
        print("\nSPEC REJECTED - %d problem(s):" % len(errs))
        for e in errs:
            print("  - " + e)
        return 2
    print("spec validates: assets on disk, memes catalogued, SFX in the bank, no geometry")
    if a.check:
        return 0

    dd = draft_dir(sp)
    if not os.path.isdir(dd):
        print("draft not found: %s" % dd)
        return 2
    if capcutcli.capcut_running():
        print("CapCut is RUNNING - quit it first.")
        return 2

    print("\ndraft: %s" % dd)
    if a.stage in ("all", "foundation"):
        print("\n-- foundation --")
        foundation.build(sp, dd)
    if a.stage in ("all", "overlays"):
        print("\n-- overlays --")
        overlays.build(sp, dd, allow_uncached=a.allow_uncached)
    print("\nbuilt. Now run, in order:")
    print("  python _state/enforce_track_order.py %s" % dd)
    print("  python _state/verify_build.py %s" % dd)
    print("  python _state/visual_gate.py %s --out gate.png    # and LOOK at it" % dd)
    return 0


if __name__ == "__main__":
    sys.exit(main())
