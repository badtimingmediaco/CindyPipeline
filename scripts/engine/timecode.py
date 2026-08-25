# -*- coding: utf-8 -*-
"""Timecode, in the owner's format. Never do this conversion in your head.

The owner gives timeline coordinates as **HH:MM:SS:FF** — the last field is FRAMES, not
hundredths. A whole review round was acted on with these read as MM:SS:

    "49:01"  is 49 seconds + 1 frame   = 49.033s,  NOT 49 minutes 1 second
    "38:13"  is 38s 13f                = 38.433s
    "42:24"  is 42s 24f                = 42.800s

Every note that came back as "the SFX at 32:27 is wrong" was therefore inspected at the
wrong moment in the video, which is a very efficient way to conclude that a correct thing
is broken.

FPS comes from the project, not from an assumption. `fps_of(draft)` reads it.
"""
import json
import os

DEFAULT_FPS = 30.0


def fps_of(draft):
    """Frames per second, read off the draft's own timeline."""
    p = os.path.join(draft, "template-2.tmp")
    if not os.path.exists(p):
        p = os.path.join(draft, "draft_content.json")
    try:
        return float(json.load(open(p, encoding="utf-8")).get("fps") or DEFAULT_FPS)
    except Exception:
        return DEFAULT_FPS


def to_seconds(tc, fps=DEFAULT_FPS):
    """'HH:MM:SS:FF' -> seconds. Accepts 'SS:FF', 'MM:SS:FF' and 'HH:MM:SS:FF'.

    A bare number is already seconds and passes through, so a spec can mix the two.
    """
    if isinstance(tc, (int, float)):
        return float(tc)
    parts = [p.strip() for p in str(tc).split(":")]
    if len(parts) == 1:
        return float(parts[0])
    frames = float(parts[-1])
    rest = [float(p) for p in parts[:-1]]
    while len(rest) < 3:
        rest.insert(0, 0.0)
    h, m, s = rest
    return h * 3600.0 + m * 60.0 + s + frames / fps


def to_tc(seconds, fps=DEFAULT_FPS):
    """seconds -> 'HH:MM:SS:FF', for talking back to the owner in their own units."""
    total_f = int(round(float(seconds) * fps))
    f = total_f % int(round(fps))
    total_s = total_f // int(round(fps))
    return "%02d:%02d:%02d:%02d" % (total_s // 3600, (total_s // 60) % 60,
                                    total_s % 60, f)


def snap(seconds, fps=DEFAULT_FPS):
    """Quantise to the nearest whole frame.

    CapCut stores microseconds, so a value like 41.96 sits between frames. Two assets that
    should butt up exactly will otherwise differ by a fraction of a frame and leave the
    sliver the owner keeps catching.
    """
    return round(round(float(seconds) * fps) / fps, 6)


def frames_between(a, b, fps=DEFAULT_FPS):
    return (float(b) - float(a)) * fps
