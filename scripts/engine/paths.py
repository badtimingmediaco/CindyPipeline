# -*- coding: utf-8 -*-
"""Where everything lives. Derived from this file's own location - never hardcoded.

build_reviewer.py opened with `PIPE = r"C:/Users/anayk/Documents/CindyPipeline"` (a hardcoded absolute), which is
why the plugin copy could never run: a teammate's checkout is somewhere else entirely.
"""
import os

ENGINE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.dirname(ENGINE)
PIPE = os.path.dirname(STATE)

ASSETS = os.path.join(PIPE, "04_assets")
BANK = os.path.join(ASSETS, "memes", "bank")
GFX = os.path.join(ASSETS, "graphics")
LOGOS = os.path.join(ASSETS, "logos")
SCREENRECS = os.path.join(ASSETS, "screenrecs")
SFXDIR = os.path.join(PIPE, "_sfx", "Cindiezhu sfx")
BACKUPS = os.path.join(PIPE, "_backups")
RUNS = os.path.join(PIPE, "_runs")

MEME_CATALOG = os.path.join(STATE, "meme_catalog.json")
SFX_MAP = os.path.join(STATE, "sfx_map.json")
STICKER_KIT = os.path.join(STATE, "sticker_kit.json")

# Asset roots a spec may name with the "<root>/file.png" shorthand, so no spec ever
# carries an absolute path.
ROOTS = {"bank": BANK, "gfx": GFX, "logos": LOGOS, "screenrecs": SCREENRECS,
         "sfx": SFXDIR}


def resolve_asset(ref):
    """'bank/foo.mp4' -> absolute path. An absolute path is passed through."""
    if os.path.isabs(ref):
        return ref
    ref = ref.replace("\\", "/")
    head, _, tail = ref.partition("/")
    if head in ROOTS:
        return os.path.join(ROOTS[head], *tail.split("/"))
    return os.path.join(PIPE, *ref.split("/"))
