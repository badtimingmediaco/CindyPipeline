#!/usr/bin/env python3
"""Stage 0 - Doctor. Verify this machine can run the pipeline, and resolve every path.

Prints one PASS/FAIL/WARN line per check with the evidence that decided it, then
writes _state/paths.json. A summary claim is not evidence - every check prints what
it actually found, so a human can disagree with it.

  python doctor.py                      # check, write paths.json
  python doctor.py --pipeline <dir>     # check a specific pipeline home
  python doctor.py --json               # machine-readable, for the setup command

Windows-first by design (the editors are all on Windows); the POSIX branches exist so
the script does not crash on a Mac, not because macOS is supported yet.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

WIN = sys.platform == "win32"
HOME = os.path.expanduser("~")
LOCALAPPDATA = os.environ.get("LOCALAPPDATA") or os.path.join(HOME, "AppData", "Local")

RESULTS = []
FAILS = []
WARNS = []


def check(name, ok, evidence="", fatal=True):
    """ok True -> PASS, False -> FAIL (or WARN when fatal=False)."""
    tag = "PASS" if ok else ("FAIL" if fatal else "WARN")
    print(f"  [{tag}] {name}")
    for line in str(evidence).splitlines():
        if line.strip():
            print(f"         {line}")
    RESULTS.append({"name": name, "ok": bool(ok), "fatal": fatal, "evidence": str(evidence)})
    if not ok:
        (FAILS if fatal else WARNS).append(name)
    return ok


def run(cmd, timeout=20):
    """Run a command, return (rc, combined output). Never raises.

    On Windows an npm-installed CLI is a .CMD shim; since 3.11 Python refuses to exec
    those from a bare name in a list, so resolve argv[0] through PATH first.
    """
    if WIN and isinstance(cmd, list) and cmd:
        cmd = [shutil.which(cmd[0]) or cmd[0]] + list(cmd[1:])
    try:
        p = subprocess.run(cmd, shell=isinstance(cmd, str), capture_output=True,
                           text=True, timeout=timeout,
                           creationflags=(0x08000000 if WIN else 0))
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except subprocess.TimeoutExpired:
        return 1, f"timed out after {timeout}s"
    except Exception as e:
        return 1, str(e)


def which(cmd):
    return shutil.which(cmd) or ""


def py_module(mod):
    """Import in a subprocess so a broken native dependency cannot kill the doctor.

    Generous timeout on purpose: faster_whisper pulls in ctranslate2's DLLs and a COLD
    first import can take far longer than the ~4s it costs once the OS has cached them.
    A 20s budget reports "not installed" for a module that is installed and fine.
    """
    rc, out = run([sys.executable, "-c", f"import {mod}"], timeout=120)
    return rc == 0, out.strip().splitlines()[-1] if rc and out.strip() else ""


# --------------------------------------------------------------------------- CapCut

def environment_verdict():
    """Can this machine host the pipeline at all? -> (ok, explanation).

    The pipeline drives CapCut *desktop*, which ships only for Windows and macOS, and it
    writes into a local drafts folder that CapCut then opens. A Linux box - in practice a
    cloud/web Claude Code session - cannot do that, and no amount of installing helps.
    Checked FIRST so nobody unpacks a 30MB kit into a container that disappears.
    """
    if sys.platform.startswith("linux"):
        cloud = (os.path.exists("/.dockerenv") or HOME in ("/root", "/home/user")
                 or os.environ.get("CLAUDE_CODE_REMOTE"))
        return False, (
            "Linux" + (" (looks like a cloud/web session)" if cloud else "") + ".\n"
            "CapCut desktop does not exist for Linux, so the pipeline cannot run here.\n"
            "Run this in Claude Code ON THE COMPUTER WHERE YOU EDIT - the Windows machine\n"
            "with CapCut installed. Everything else about the kit is fine; it is CapCut\n"
            "that has to be local, because the build writes into its drafts folder and\n"
            "you open the result in the app afterwards.")
    if sys.platform == "darwin":
        return True, "macOS - CapCut exists here, but this kit is Windows-tested only."
    if not WIN:
        return False, f"{sys.platform} - unsupported."
    return True, "Windows"


def capcut_installed():
    """Is CapCut on this machine? -> (yes, evidence).

    One hard-coded exe path is not enough. CapCut has no registry uninstall entry, and its
    exe may sit at the root of %LOCALAPPDATA%\\CapCut, inside a VERSION subfolder
    (9.3.0.3970\\CapCut.exe), under Program Files, or as a Store app. A single-path check
    told an editor with a working CapCut that it was not installed - while the same run had
    already found their drafts folder, which only CapCut could have created.

    Strongest evidence first: the config file CapCut writes on first run.
    """
    gs = os.path.join(LOCALAPPDATA, "CapCut", "User Data", "Config", "globalSetting")
    if os.path.exists(gs):
        return True, f"CapCut has run on this machine (its config exists: {gs})"

    roots = [os.path.join(LOCALAPPDATA, "CapCut"),
             os.path.join(LOCALAPPDATA, "Programs", "CapCut"),
             os.path.join(os.environ.get("PROGRAMFILES", r"C:\Program Files"), "CapCut"),
             os.path.join(os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)"), "CapCut")]
    for root in roots:
        if not os.path.isdir(root):
            continue
        direct = os.path.join(root, "CapCut.exe")
        if os.path.exists(direct):
            return True, direct
        try:                       # version subfolders: 9.3.0.3970\CapCut.exe
            for name in sorted(os.listdir(root), reverse=True):
                cand = os.path.join(root, name, "CapCut.exe")
                if os.path.exists(cand):
                    return True, cand
        except OSError:
            pass

    if os.path.isdir(os.path.join(LOCALAPPDATA, "CapCut")):
        return True, (f"{os.path.join(LOCALAPPDATA, 'CapCut')} exists but no CapCut.exe was "
                      "found in it - probably a Store install or an unusual layout")
    return False, "no CapCut install found in any known location"


def capcut_running():
    """The single most important guardrail: CapCut must be closed during any write.
    It never re-reads from disk while open and its next autosave destroys the build."""
    if WIN:
        rc, out = run('tasklist /FI "IMAGENAME eq CapCut.exe" /NH')
        return "capcut.exe" in out.lower()
    rc, out = run(["pgrep", "-ix", "CapCut"])   # never -f: would self-match a path arg
    return bool(out.strip())


def drafts_dir_from_settings():
    """CapCut records its ACTIVE drafts folder here, including a custom one the user
    chose in the UI. This is the only authoritative source - the ~20 other files that
    contain the path are prerender/preset caches that go stale."""
    if not WIN:
        return "", ""
    gs = os.path.join(LOCALAPPDATA, "CapCut", "User Data", "Config", "globalSetting")
    try:
        raw = open(gs, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return "", f"not readable: {gs}"
    m = re.search(r"currentCustomDraftPath=(.+)", raw)
    if not m:
        return "", f"no currentCustomDraftPath in {gs}"
    path = m.group(1).strip().split("\x00")[0].replace("\\\\", "\\")
    return (path, f"globalSetting -> {path}") if os.path.isdir(path) else \
           ("", f"globalSetting names a missing dir: {path}")


def default_drafts_dirs():
    if WIN:
        return [os.path.join(LOCALAPPDATA, "CapCut Drafts"),
                os.path.join(LOCALAPPDATA, "CapCut", "User Data", "Projects", "com.lveditor.draft")]
    if sys.platform == "darwin":
        return [os.path.join(HOME, "Movies", "CapCut", "User Data",
                             "Projects", "com.lveditor.draft")]
    # Linux has no CapCut at all. Returning the macOS path here made the failure read
    # "looked in /root/Movies/CapCut/..." - which implies we think this is a Mac and sends
    # the reader hunting for a missing folder instead of the real cause, that CapCut cannot
    # exist on this machine. environment_verdict() should have stopped us long before here.
    return []


def looks_like_drafts_dir(d):
    """A drafts dir holds draft FOLDERS, each with a timeline file."""
    try:
        for name in os.listdir(d)[:400]:
            sub = os.path.join(d, name)
            if os.path.isdir(sub) and (os.path.exists(os.path.join(sub, "template-2.tmp"))
                                       or os.path.exists(os.path.join(sub, "draft_content.json"))):
                return True
    except OSError:
        pass
    return False


def find_drafts_dir(hint=""):
    """settings -> defaults -> shallow scan. Returns (path, how_we_found_it)."""
    tried = []
    if hint and os.path.isdir(hint):
        return hint, f"supplied: {hint}"
    d, why = drafts_dir_from_settings()
    tried.append(why)
    if d:
        return d, why
    for c in default_drafts_dirs():
        if os.path.isdir(c) and looks_like_drafts_dir(c):
            return c, f"default location: {c}"
        tried.append(f"not a drafts dir: {c}")
    for base in (os.path.join(HOME, "Documents"), os.path.join(HOME, "Desktop"), HOME):
        try:
            for name in os.listdir(base):
                c = os.path.join(base, name)
                if "capcut" in name.lower() and os.path.isdir(c) and looks_like_drafts_dir(c):
                    return c, f"found by scan: {c}"
        except OSError:
            continue
    return "", "\n".join(tried)


def canonical_timeline(draft):
    """Modern CapCut: template-2.tmp is canonical, draft_content.json is a mirror.
    Older builds invert that. Never assume - ask capcut diagnose, per machine and
    again after every CapCut update.

    Returns (canonical_filename, diverged, evidence).
    """
    rc, out = run(["capcut", "diagnose", draft], timeout=60)
    try:
        m = re.search(r"\{.*\}", out, re.S)
        d = json.loads(m.group(0))
        canon = d.get("canonical") or ""
        ev = (f"canonical={canon}  version={d.get('version')}  "
              f"modern_storage={d.get('modern_storage')}  diverged={d.get('diverged')}")
        if d.get("editor_running"):
            ev += f"\nCapCut reports itself running: {d['editor_running']}"
        return canon, bool(d.get("diverged")), ev
    except Exception:
        pass
    for f in ("template-2.tmp", "draft_content.json"):
        if os.path.exists(os.path.join(draft, f)):
            return f, False, f"diagnose gave no parseable verdict; first present: {f}"
    return "", False, out.strip()[:300]


# ---------------------------------------------------------------------------- fonts

def installed_fonts():
    """Every font this user can actually use: HKLM (system) + HKCU (per-user), plus a
    filename sweep of both font dirs. The per-user location is the one a plain
    C:\\Windows\\Fonts check misses - and it is where these two usually land."""
    names, files = set(), set()
    if WIN:
        try:
            import winreg
            key = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"
            for root in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
                try:
                    with winreg.OpenKey(root, key) as k:
                        for i in range(winreg.QueryInfoKey(k)[1]):
                            n, v, _ = winreg.EnumValue(k, i)
                            names.add(n)
                            files.add(os.path.basename(str(v)).lower())
                except OSError:
                    continue
        except ImportError:
            pass
    for d in (os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts"),
              os.path.join(LOCALAPPDATA, "Microsoft", "Windows", "Fonts")):
        try:
            files.update(f.lower() for f in os.listdir(d))
        except OSError:
            continue
    return names, files


def has_font(needle, names, files):
    n = needle.lower()
    hit = [x for x in names if n in x.lower()]
    if hit:
        return True, hit[0]
    compact = n.replace(" ", "")
    hit = [f for f in files if compact in f.replace(" ", "").replace("-", "").replace("_", "")]
    return (True, hit[0]) if hit else (False, "")


# ----------------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pipeline", default=os.path.join(HOME, "Documents", "CindyPipeline"))
    ap.add_argument("--drafts", default="")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    pipe = os.path.abspath(args.pipeline)
    paths = {"pipeline_home": pipe}

    print("\nSTAGE 0 - DOCTOR")
    print("=" * 68)

    # -- can this machine host the pipeline at all? -------------------------
    env_ok, env_why = environment_verdict()
    print("\nEnvironment")
    check("This machine can run the pipeline", env_ok, env_why, fatal=not env_ok or True)
    if not env_ok:
        print("\n" + "=" * 68)
        print("NOT READY - wrong kind of machine. Nothing below would help.")
        print("=" * 68 + "\n")
        if args.json:
            print(json.dumps({"ready": False, "fails": ["environment"],
                              "environment": env_why}, indent=2))
        return 1

    # -- toolchain ----------------------------------------------------------
    print("\nToolchain")
    check("Python 3.9+", sys.version_info >= (3, 9), sys.version.split()[0] + f"  ({sys.executable})")
    for label, mod, fix in (("faster-whisper", "faster_whisper", "pip install faster-whisper"),
                            ("Pillow", "PIL", "pip install pillow")):
        ok, err = py_module(mod)
        check(label, ok, "importable" if ok else f"{fix}\n{err}")
    ff = which("ffmpeg")
    check("ffmpeg", bool(ff), ff or "winget install Gyan.FFmpeg  (then reopen the terminal)")
    fp = which("ffprobe")
    check("ffprobe", bool(fp), fp or "ships with ffmpeg - if this fails alone, PATH is partial")
    node = which("node")
    check("Node.js", bool(node), node or "https://nodejs.org")
    rc, out = run(["capcut", "--version"])
    ver = out.strip().splitlines()[0] if out.strip() else ""
    check("capcut-cli", bool(re.search(r"\d+\.\d+", ver)), ver or "npm i -g capcut-cli")

    # -- CapCut itself ------------------------------------------------------
    print("\nCapCut")
    cc_ok, cc_why = capcut_installed()
    running = capcut_running()
    drafts, why = find_drafts_dir(args.drafts)

    # Order matters: a resolved drafts folder is itself proof CapCut is installed, since
    # nothing else creates one. Never report "CapCut is not installed" in the same run that
    # found their drafts folder - that contradiction is what makes an editor distrust the
    # whole report.
    if drafts and not cc_ok:
        cc_ok, cc_why = True, f"drafts folder exists, so CapCut created it: {drafts}"
    check("CapCut desktop installed", cc_ok or not WIN, cc_why if WIN else "(non-Windows)")

    check("CapCut is CLOSED (required for every write)", not running,
          "running - close it before any build" if running else "closed")

    check("CapCut drafts folder", bool(drafts), why)
    paths["capcut_drafts_dir"] = drafts or None

    tpl = os.path.join(drafts, "CZ_TEMPLATE") if drafts else ""
    tpl_ok = bool(tpl and os.path.isdir(tpl))
    check("CZ_TEMPLATE placed in drafts folder", tpl_ok,
          tpl if tpl_ok else "run /reel-setup to place it")
    paths["cz_template_draft"] = tpl if tpl_ok else None

    if tpl_ok:
        canon, diverged, ev = canonical_timeline(tpl)
        check("Canonical timeline file identified", bool(canon), ev)
        check("Template timeline not diverged from its mirror", not diverged,
              "canonical and draft_content.json agree" if not diverged
              else "diverged - the mirror is stale; re-copy canonical over it")
        paths["canonical_timeline"] = canon or None

    # -- fonts --------------------------------------------------------------
    # Markerist is NOT checked: it lives only inside CapCut's effect cache and
    # arrives via the template, never as a filesystem font.
    print("\nFonts")
    names, files = installed_fonts()
    paths["fonts"] = {}
    for label, needle in (("Poppins", "poppins"), ("MADE Awelier", "awelier")):
        ok, found = has_font(needle, names, files)
        check(f"{label} installed", ok,
              f"registered as: {found}" if ok else f"not found among {len(names)} registered fonts")
        paths["fonts"][needle] = found if ok else None
    paths["fonts"]["markerist"] = "capcut-internal - arrives via template cache, no check"

    # -- the kit ------------------------------------------------------------
    print("\nPipeline home")
    check("Pipeline folder exists", os.path.isdir(pipe), pipe)
    for sub in ("01_intake", "02_transcripts", "03_plans", "04_assets", "05_output",
                "_state", "_backups", "_sfx"):
        p = os.path.join(pipe, sub)
        check(f"  {sub}/", os.path.isdir(p), "" if os.path.isdir(p) else "missing - /reel-setup creates it")

    sfx_map_p = os.path.join(pipe, "_state", "sfx_map.json")
    bank = os.path.join(pipe, "_sfx", "Cindiezhu sfx")
    if os.path.exists(sfx_map_p) and os.path.isdir(bank):
        mapped = {e["file"] for e in json.load(open(sfx_map_p, encoding="utf-8"))}
        ondisk = set(os.listdir(bank))
        missing, extra = sorted(mapped - ondisk), sorted(ondisk - mapped)
        check("SFX bank matches sfx_map.json exactly", not missing and not extra,
              f"{len(mapped)} mapped / {len(ondisk)} on disk"
              + (f"\nin map, not on disk: {missing}" if missing else "")
              + (f"\non disk, not in map: {extra}" if extra else ""))
        paths["sfx_bank"] = bank
        paths["sfx_map"] = sfx_map_p
    else:
        check("SFX bank matches sfx_map.json exactly", False,
              f"map: {os.path.exists(sfx_map_p)}  bank: {os.path.isdir(bank)}")

    # Not fatal: a build still runs, it just pauses partway through Stage 1 to download
    # several hundred MB - which is exactly the ambush this warning exists to prevent.
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import warm_models
        have = warm_models.cached_models()
        cached = warm_models.DEFAULT_MODEL in have
        check(f"Whisper model '{warm_models.DEFAULT_MODEL}' downloaded", cached,
              f"cached: {', '.join(have)}" if cached
              else ("not cached - your first build will pause to download it.\n"
                    "Fetch it now with: python _state/warm_models.py"), fatal=False)
    except Exception as e:
        check("Whisper model downloaded", False, f"could not check: {e}", fatal=False)

    memes = os.path.join(pipe, "04_assets", "memes", "bank")
    n = len(os.listdir(memes)) if os.path.isdir(memes) else 0
    check("Meme bank present", n > 0, f"{n} clips in {memes}", fatal=False)
    paths["meme_bank"] = memes if n else None

    for f in ("house_layout.py", "verify_build.py", "tenor_fetch.py",
              "post_session_fix.py", "enforce_track_order.py"):
        p = os.path.join(pipe, "_state", f)
        check(f"  _state/{f}", os.path.exists(p), "" if os.path.exists(p) else "missing")

    for f in ("paper_donor_child.json", "tpl_paper.json", "sticker_kit.json"):
        p = os.path.join(pipe, "_state", f)
        check(f"  _state/{f}", os.path.exists(p), "" if os.path.exists(p) else "missing")

    # -- verdict ------------------------------------------------------------
    if not FAILS:
        os.makedirs(os.path.join(pipe, "_state"), exist_ok=True)
        paths["resolved_at"] = __import__("datetime").datetime.now().astimezone().isoformat()
        target = os.path.join(pipe, "_state", "paths.json")
        # MERGE, never clobber. paths.json accumulates hand-written notes that record
        # things no probe can rediscover - why this machine's drafts dir is custom, why
        # a given folder is the canonical home. An overwriting doctor silently destroys
        # them, and the next person re-learns the hard way.
        merged = {}
        if os.path.exists(target):
            try:
                merged = json.load(open(target, encoding="utf-8"))
            except Exception:
                merged = {}
        merged.update(paths)
        with open(target, "w", encoding="utf-8") as fh:
            json.dump(merged, fh, indent=2)

    print("\n" + "=" * 68)
    if FAILS:
        print(f"NOT READY - {len(FAILS)} failure(s): {', '.join(FAILS)}")
    else:
        print("READY" + (f" - {len(WARNS)} warning(s): {', '.join(WARNS)}" if WARNS else ""))
        print(f"paths.json written to {os.path.join(pipe, '_state', 'paths.json')}")
    print("=" * 68 + "\n")

    if args.json:
        print(json.dumps({"ready": not FAILS, "fails": FAILS, "warns": WARNS,
                          "paths": paths, "checks": RESULTS}, indent=2))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
