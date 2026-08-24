#!/usr/bin/env python3
"""Tell the editor when a newer Reel Factory is available. Runs at session start.

Deliberately NOTIFIES rather than auto-updating. Running `claude plugin update` from
inside a live session would rewrite the plugin cache that the same session is reading
from, and the new version would not take effect until a restart anyway - so the editor
would be told nothing while their files changed underneath them. A one-line notice they
can act on is both safer and clearer.

Constraints this runs under: it fires on EVERY session start, so it must be fast, silent
when there is nothing to say, and incapable of blocking or erroring into the user's face.
Every failure path here exits 0 with no output.
"""
import json
import os
import sys
import time
import urllib.request

RAW = ("https://raw.githubusercontent.com/badtimingmediaco/CindyPipeline"
       "/main/.claude-plugin/plugin.json")
STAMP = os.path.join(os.path.expanduser("~"), ".claude", ".reel_factory_update_check")
EVERY = 24 * 3600          # one network call a day is plenty
INSTALL = ("irm https://raw.githubusercontent.com/badtimingmediaco/CindyPipeline"
           "/main/install.ps1 | iex")


def ver(s):
    """'4.10.2' -> (4,10,2) so 4.10 sorts above 4.9, which string compare gets wrong."""
    out = []
    for part in str(s).split("."):
        try:
            out.append(int(part))
        except ValueError:
            out.append(0)
    return tuple(out)


def local_version():
    here = os.path.dirname(os.path.abspath(__file__))
    p = os.path.join(os.path.dirname(here), ".claude-plugin", "plugin.json")
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)["version"]


def due():
    try:
        return (time.time() - os.path.getmtime(STAMP)) > EVERY
    except OSError:
        return True


def touch():
    try:
        os.makedirs(os.path.dirname(STAMP), exist_ok=True)
        open(STAMP, "w").write(str(time.time()))
    except OSError:
        pass


def main():
    if not due():
        return 0
    touch()                                  # stamp FIRST, so a hanging network call
    try:                                     # cannot make every session retry
        with urllib.request.urlopen(RAW, timeout=4) as r:
            remote = json.loads(r.read().decode("utf-8"))["version"]
        mine = local_version()
    except Exception:
        return 0                             # offline, blocked, malformed - say nothing
    if ver(remote) > ver(mine):
        print(f"Reel Factory {remote} is available (you have {mine}).")
        print(f"To update, run this in PowerShell:  {INSTALL}")
        print("Then restart Claude Code.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
