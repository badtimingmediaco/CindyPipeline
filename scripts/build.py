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
import shutil
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
    ap.add_argument("--fresh", action="store_true",
                    help="clone CZ_TEMPLATE into the draft first (a build must start "
                         "from a fresh clone - the paper donor gets consumed otherwise)")
    ap.add_argument("--force", action="store_true",
                    help="build over a draft that has been edited since the engine made "
                         "it. This DESTROYS those edits and they are not recoverable.")
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
    if capcutcli.capcut_running():
        print("CapCut is RUNNING - quit it first.")
        return 2

    # PROVENANCE GATE. Every safeguard here used to guard the WRITE ("is CapCut closed?")
    # and none guarded the TARGET ("has this draft moved since I made it?"). On 2026-08-26
    # that cost the owner a full day of hand edits: nine rebuilds, each from a fresh
    # template clone, over a draft that had already been delivered. Closed is not the same
    # as untouched.
    ok, why = draftio.check_untouched(dd, sp["name"])
    if not ok and not a.force:
        print("\nREFUSING TO BUILD")
        print("  " + why.replace(chr(10), chr(10) + "  "))
        print("\n  Either build to a new draft name in the spec, or re-run with --force")
        print("  if you are certain those edits are expendable.")
        return 3
    if not ok:
        print("  ! --force: overwriting a draft that was edited after the engine built it")
    elif os.path.isdir(dd):
        print("provenance: %s" % why)

    if a.fresh or not os.path.isdir(dd):
        tpl = os.path.join(os.path.dirname(dd), "CZ_TEMPLATE")
        if not os.path.isdir(tpl):
            print("template not found: %s" % tpl)
            return 2
        if os.path.isdir(dd):
            shutil.rmtree(dd)
        shutil.copytree(tpl, dd)
        print("cloned CZ_TEMPLATE -> %s" % os.path.basename(dd))

    print("\ndraft: %s" % dd)
    if a.stage in ("all", "foundation"):
        print("\n-- foundation --")
        foundation.build(sp, dd)
    if a.stage in ("all", "overlays"):
        print("\n-- overlays --")
        overlays.build(sp, dd, allow_uncached=a.allow_uncached)
    # Provisional record. enforce_track_order is the LAST write and updates it again -
    # without that, the next build would see its own track-ordered output as "edited".
    draftio.record_build(dd, sp["name"])
    print("\nbuilt. Now run, in order (track order updates the provenance record):")
    print("  python _state/enforce_track_order.py %s" % dd)
    print("  python _state/verify_build.py %s" % dd)
    print("  python _state/visual_gate.py %s --out gate.png    # and LOOK at it" % dd)
    return 0


if __name__ == "__main__":
    sys.exit(main())
