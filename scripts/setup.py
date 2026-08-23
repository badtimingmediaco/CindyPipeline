#!/usr/bin/env python3
"""One-time machine setup. Builds the pipeline home, installs the kit, places
CZ_TEMPLATE into this machine's CapCut drafts folder, and relinks the template's
sample audio so nothing points at the machine it was authored on.

  python setup.py                          # default home: ~/Documents/CindyPipeline
  python setup.py --pipeline <dir>
  python setup.py --force                  # re-copy kit files that already exist

Idempotent and additive. It NEVER overwrites work the editor owns - their memes,
their learnings, their drafts - unless --force is given, and even then it leaves
01_intake / 05_output / _backups alone entirely.

Deliberately does NOT put the pipeline in OneDrive or any synced folder: sync locks
files mid-write and can fork a draft into a conflicted copy while CapCut has it open.
"""
import argparse
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
KIT = os.path.join(REPO, "kit")
HOME = os.path.expanduser("~")

sys.path.insert(0, HERE)
import doctor  # noqa: E402  - reuse its detection rather than re-implementing it

SKELETON = ["01_intake", "02_transcripts", "03_plans", "04_assets/graphics",
            "04_assets/logos", "04_assets/memes/bank", "04_assets/screenrecs",
            "04_assets/posters", "05_output", "_state/card_templates", "_backups",
            "_runs", "_sfx/Cindiezhu sfx"]

# (source under kit/, destination under the pipeline home)
KIT_MAP = [
    ("sfx",              "_sfx/Cindiezhu sfx"),
    ("memes/bank",       "04_assets/memes/bank"),
    ("logos",            "04_assets/logos"),
    ("graphics",         "04_assets/graphics"),
    ("state",            "_state"),
]
SCRIPTS = ["house_layout.py", "verify_build.py", "tenor_fetch.py", "post_session_fix.py",
           "enforce_track_order.py", "preview_composite.py", "doctor.py", "resolve_input.py"]

log = []


def say(msg):
    print(msg)
    log.append(msg)


SYNC_ROOTS = ("onedrive", "dropbox", "google drive", "googledrive", "icloud drive",
              "icloakdrive", "icloud~", "box sync", "pcloud", "sync.com")


def in_synced_folder(path):
    """Name the sync root if this path lives under one, else "".

    Match whole path COMPONENTS, not the raw string: a substring test fires on any
    path that merely happens to contain "onedrive" somewhere - a temp dir keyed by a
    session id, a folder called "onedrive-migration-notes" - and refuses a location
    that is perfectly fine.
    """
    for part in os.path.abspath(path).split(os.sep):
        p = part.lower()
        # Exact, or the business form "OneDrive - Company". A bare startswith would
        # also refuse an ordinary folder called "onedrive-migration-notes".
        if any(p == r or p.startswith(r + " ") for r in SYNC_ROOTS):
            return part
    return ""


def copy_tree(src, dst, force=False):
    """Copy files that are missing (or all of them with --force). Returns (new, kept)."""
    new = kept = 0
    for root, _dirs, files in os.walk(src):
        rel = os.path.relpath(root, src)
        out = os.path.join(dst, rel) if rel != "." else dst
        os.makedirs(out, exist_ok=True)
        for f in files:
            s, d = os.path.join(root, f), os.path.join(out, f)
            if os.path.exists(d) and not force:
                kept += 1
                continue
            shutil.copy2(s, d)
            new += 1
    return new, kept


def relink_template_media(draft, media_dir):
    """CZ_TEMPLATE hard-references its two sample audio files by ABSOLUTE path on the
    machine it was authored on. Left alone, both links are dead on every other machine
    and CapCut shows the template with missing media.

    Rewrite just the directory prefix, in every file that carries it, in both slash
    conventions CapCut uses. Byte-targeted: nothing else in the JSON is touched.
    """
    names = os.listdir(media_dir) if os.path.isdir(media_dir) else []
    if not names:
        return 0, "no template_media/ in the kit - skipped"
    touched, hits = [], 0
    for root, _dirs, files in os.walk(draft):
        for f in files:
            if not (f.endswith(".json") or f.endswith(".tmp") or f.endswith(".bak")):
                continue
            p = os.path.join(root, f)
            try:
                raw = open(p, "r", encoding="utf-8", errors="ignore").read()
            except OSError:
                continue
            out = raw
            for name in names:
                # match "<anything>/<name>" and "<anything>\\<name>", replace the dir
                for sep, newdir in (("/", media_dir.replace("\\", "/")),
                                    ("\\\\", media_dir.replace("\\", "\\\\"))):
                    import re
                    pat = re.compile(r'((?:[A-Za-z]:)?(?:[^"]*?))' + re.escape(sep)
                                     + re.escape(name) + r'(?=")')
                    out = pat.sub(lambda m: newdir + sep + name, out)
            if out != raw:
                open(p, "w", encoding="utf-8", newline="").write(out)
                touched.append(os.path.relpath(p, draft))
                hits += 1
    return hits, ("relinked in: " + ", ".join(touched[:6]) + (" ..." if len(touched) > 6 else "")
                  if touched else "no absolute media paths found to relink")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pipeline", default=os.path.join(HOME, "Documents", "CindyPipeline"))
    ap.add_argument("--drafts", default="")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--skip-doctor", action="store_true")
    args = ap.parse_args()
    pipe = os.path.abspath(args.pipeline)

    print("\nREEL FACTORY - SETUP")
    print("=" * 68)

    synced = in_synced_folder(pipe)
    if synced:
        say(f"\n  REFUSING: {pipe} is inside a synced folder ({synced}).")
        say("  Sync locks files mid-write and can fork a draft into a conflicted copy.")
        say("  Pick a plain local path, e.g. ~/Documents/CindyPipeline")
        return 2

    # 1 - skeleton ----------------------------------------------------------
    say(f"\n1. Pipeline home: {pipe}")
    for sub in SKELETON:
        os.makedirs(os.path.join(pipe, *sub.split("/")), exist_ok=True)
    say(f"   {len(SKELETON)} folders ready")

    # 2 - kit ---------------------------------------------------------------
    say("\n2. Installing the kit")
    for src, dst in KIT_MAP:
        s = os.path.join(KIT, *src.split("/"))
        if not os.path.isdir(s):
            say(f"   [skip] kit/{src} not in this checkout")
            continue
        new, kept = copy_tree(s, os.path.join(pipe, *dst.split("/")), args.force)
        say(f"   {dst:28s} {new:3d} copied, {kept:3d} already present")

    for f in SCRIPTS:
        s = os.path.join(HERE, f)
        d = os.path.join(pipe, "_state", f)
        if os.path.exists(s) and (args.force or not os.path.exists(d)):
            shutil.copy2(s, d)
    say(f"   _state/ scripts             {len(SCRIPTS)} installed")

    # 3 - the template draft ------------------------------------------------
    say("\n3. CapCut template")
    if doctor.capcut_running():
        say("   REFUSING: CapCut is open. Close it and re-run - CapCut never re-reads")
        say("   from disk while open and its next autosave would destroy the copy.")
        return 2

    drafts, why = doctor.find_drafts_dir(args.drafts)
    if not drafts:
        say(f"   Could not find the CapCut drafts folder.\n   {why}")
        say("   Open CapCut once, create an empty project, then re-run setup.")
        return 2
    say(f"   drafts folder: {drafts}\n   ({why})")

    src_tpl = os.path.join(KIT, "template", "CZ_TEMPLATE")
    dst_tpl = os.path.join(drafts, "CZ_TEMPLATE")
    if os.path.isdir(dst_tpl) and not args.force:
        say("   CZ_TEMPLATE already present - left as is (--force to replace)")
    elif os.path.isdir(src_tpl):
        if os.path.isdir(dst_tpl):
            shutil.rmtree(dst_tpl)
        shutil.copytree(src_tpl, dst_tpl)
        say(f"   CZ_TEMPLATE placed ({sum(len(f) for _, _, f in os.walk(dst_tpl))} files)")
    else:
        say("   [skip] kit/template/CZ_TEMPLATE not in this checkout")

    if os.path.isdir(dst_tpl):
        media = os.path.join(pipe, "_state", "template_media")
        os.makedirs(media, exist_ok=True)
        kit_media = os.path.join(KIT, "template_media")
        if os.path.isdir(kit_media):
            copy_tree(kit_media, media, force=True)
        hits, ev = relink_template_media(dst_tpl, media)
        say(f"   sample audio relinked in {hits} file(s)\n   {ev}")

    # 4 - what only a human can do -----------------------------------------
    say("\n4. ONE manual step remains")
    say("   Open CZ_TEMPLATE in CapCut once, while online. CapCut then downloads the")
    say("   Markerist font, the torn-paper effect and the caption assets into its own")
    say("   local cache. Those live inside CapCut, not on disk, so no kit can ship")
    say("   them. Confirm inside: title lines styled, the sample paper sticker shows")
    say("   its text, the CTA card sits past the video end, captions styled. Save, close.")

    with open(os.path.join(pipe, "_state", "setup_log.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(log))

    if args.skip_doctor:
        print("\n" + "=" * 68 + "\nSetup done. Run doctor.py to verify.\n")
        return 0

    print("\n" + "=" * 68)
    sys.argv = [sys.argv[0], "--pipeline", pipe]
    return doctor.main()


if __name__ == "__main__":
    sys.exit(main())
