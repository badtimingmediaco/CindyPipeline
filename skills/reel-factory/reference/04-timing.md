# Sync & cuts

> Part of the Cindy Zhu Reel Factory spec (v3.0). Loaded on demand by the
> `reel-factory` skill - see SKILL.md for the routing table.

## 5. SYNC & CUTS
- Every asset fires at the START of the exact spoken word (whisper words.json).
- Detect the invisible Descript jump cuts BEFORE building:
  `ffmpeg -i base.mp4 -vf "select='gt(scene,0.05)',metadata=print:file=scenes.txt" -f null -`
  (cd into the output dir first — Windows drive-letter paths break the filter, and
  cd-first is safe on every OS). Scores
  ≥~0.08 are cuts. **Every overlay ends at the first cut inside its window** (ignore
  cuts within 0.1s of its own start).
  **OWNER OVERRIDE (2026-08-20): the rule stands, EXCEPT when the same asset is still
  explaining the phrase on the other side of the cut — then let it run through.**
  Obeying it blindly pushes the START past the cut instead, which cost ~0.8s of screen
  time on three beats of the Claude SEO build. `house_layout.trim_at_cut(...,
  carries_explanation=True)`.

## 6. THE PIPELINE (fully autonomous — no approval stops; Stage 2's single
batched clarification round is the ONLY permitted pause)

---

## 5B. READING A TIMECODE THE OWNER GIVES YOU

When the owner writes a time as `49:01`, that is **`SS:FF`** - 49 seconds and 1 frame -
not 49 minutes. The full form is `HH:MM:SS:FF`, the last field being FRAMES at the
project's fps.

**Read the fps from the project, do not assume it.** It is 30 in almost every reel here,
so `49:01` is 49.033s - but a 24 or 60 fps project makes the same string a different
instant, and a frame-accurate hit placed against the wrong fps is silently off.
`engine/timecode.py` does the conversion: `to_seconds`, `to_tc`, `snap`, `fps_of`.

## 5C. GAPS UNDER 5 FRAMES ARE NOT GAPS

If two assets are separated by **less than 5 frames**, extend the earlier one so it ends
on the exact frame the later one starts. A 2-frame hole flashes the bare talking head for
66ms, which reads as a glitch rather than as a beat. `engine/overlays.close_gaps(beats,
fps, max_gap_frames=5.0)` does this to the whole schedule; it is not a per-beat decision.

Larger gaps are left alone - those are deliberate breathing room.

## 5D. A SHORT CLIP THAT MUST COVER A LONG BEAT IS LOOPED

Never stretch it, and never let the beat end early because the source ran out. The engine
lays repeated spans end to end until the beat is covered, and applies the same geometry to
every copy (`b["loop"]`, default on).

This matters most for the MP4-of-a-GIF assets in the bank: their sources are 1-3s and are
authored to cycle. The owner does this by hand when the engine does not - four stacked
copies of one clip in a hand-finish is a **loop**, not four separate placements, and a
diff tool that reports only the first start time will tell you the wrong story.
