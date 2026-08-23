#!/usr/bin/env python3
"""Turn whatever the editor typed into the actual file in 01_intake.

"run it claude seo" / "run it CLAUDE-SEO.mp4" / "run it clade seo" all have to land on
`Claude SEO.mp4`. Editors type from memory, and being wrong about which file to spend
an hour building is far worse than asking.

  python resolve_input.py "claude seo"              # -> the match, or a ranked list
  python resolve_input.py ""                        # -> the only/newest candidate
  python resolve_input.py "claude seo" --json

Exit codes: 0 confident match, 3 ambiguous (caller must ask), 4 nothing found.
"""
import argparse
import difflib
import json
import os
import re
import sys

VIDEO_EXT = {".mp4", ".mov", ".m4v", ".mkv", ".avi", ".webm"}
# Confident enough to just run with it. Below this we ask rather than guess.
STRONG = 0.72
# If the runner-up is this close to the winner, the answer is genuinely ambiguous.
TOO_CLOSE = 0.08


def norm(s):
    """Fold everything an editor might vary: case, separators, extension, articles."""
    s = os.path.splitext(s)[0].lower()
    s = re.sub(r"[_\-.]+", " ", s)
    s = re.sub(r"[^a-z0-9 ]+", "", s)
    s = re.sub(r"\b(the|a|an|final|v\d+|d\d+|copy)\b", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def score(query, name):
    q, n = norm(query), norm(name)
    if not q:
        return 0.0
    if q == n:
        return 1.0
    base = difflib.SequenceMatcher(None, q, n).ratio()
    # Substring and token-subset matches are what people actually type: "seo" for
    # "Claude SEO.mp4", "social research" for "social media research.mp4".
    if q in n or n in q:
        base = max(base, 0.90)
    qt, nt = set(q.split()), set(n.split())
    if qt and qt <= nt:
        base = max(base, 0.86)
    elif qt & nt:
        base = max(base, 0.55 + 0.35 * len(qt & nt) / max(len(qt | nt), 1))
    return base


def candidates(intake):
    out = []
    try:
        for f in os.listdir(intake):
            p = os.path.join(intake, f)
            if os.path.isfile(p) and os.path.splitext(f)[1].lower() in VIDEO_EXT:
                out.append({"file": f, "path": p, "size": os.path.getsize(p),
                            "mtime": os.path.getmtime(p)})
    except OSError:
        pass
    return sorted(out, key=lambda c: -c["mtime"])


def resolve(intake, query):
    cands = candidates(intake)
    if not cands:
        return {"status": "empty", "candidates": []}

    if not (query or "").strip():
        # No name given. One file is unambiguous; several is not - newest is a guess,
        # and guessing which video to spend an hour on is not worth the saved question.
        if len(cands) == 1:
            return {"status": "ok", "match": cands[0], "why": "the only file in 01_intake",
                    "candidates": cands}
        return {"status": "ambiguous", "why": f"{len(cands)} files in 01_intake, no name given",
                "candidates": cands}

    for c in cands:
        c["score"] = round(score(query, c["file"]), 4)
    ranked = sorted(cands, key=lambda c: (-c["score"], -c["mtime"]))
    best = ranked[0]
    runner = ranked[1] if len(ranked) > 1 else None

    if best["score"] < STRONG:
        return {"status": "weak", "why": f"best match scored {best['score']:.2f}, below {STRONG}",
                "candidates": ranked}
    if runner and best["score"] - runner["score"] < TOO_CLOSE:
        return {"status": "ambiguous",
                "why": f"{best['file']} ({best['score']:.2f}) and {runner['file']} "
                       f"({runner['score']:.2f}) are too close to call",
                "candidates": ranked}
    return {"status": "ok", "match": best, "why": f"scored {best['score']:.2f}",
            "candidates": ranked}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query", nargs="?", default="")
    ap.add_argument("--intake", default="")
    ap.add_argument("--pipeline", default=os.path.join(os.path.expanduser("~"),
                                                       "Documents", "CindyPipeline"))
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    intake = a.intake or os.path.join(a.pipeline, "01_intake")

    r = resolve(intake, a.query)
    if a.json:
        print(json.dumps(r, indent=2))
        return {"ok": 0, "ambiguous": 3, "weak": 3, "empty": 4}[r["status"]]

    if r["status"] == "empty":
        print(f"No video files in {intake}")
        return 4
    if r["status"] == "ok":
        m = r["match"]
        print(f"MATCH  {m['file']}")
        print(f"       {m['path']}")
        print(f"       {m['size']/1e6:.1f} MB - {r['why']}")
        return 0
    print(f"AMBIGUOUS - {r['why']}\nAsk which one:")
    for c in r["candidates"][:6]:
        s = f"  {c.get('score', 0):.2f}  " if "score" in c else "  "
        print(f"{s}{c['file']}  ({c['size']/1e6:.1f} MB)")
    return 3


if __name__ == "__main__":
    sys.exit(main())
