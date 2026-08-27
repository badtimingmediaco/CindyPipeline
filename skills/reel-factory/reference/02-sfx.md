# SFX grammar

> Part of the Cindy Zhu Reel Factory spec (v3.0). Loaded on demand by the
> `reel-factory` skill - see SKILL.md for the routing table.

## 3. SFX GRAMMAR (locked bank — authoritative count = sfx_map.json; 23 at last audit)
- **First SFX is ALWAYS `magic reveal.MP3` at 0:00.** Non-negotiable.
- Density ~40–60 hits/80s; sub-second gaps and overlapping tails are normal.
- Every visual pop gets a first-frame-aligned hit; `pop motion` = text-pop spine;
  POP UI = logos/UI; error = comedy/"don't" (bank has no record-scratch); kirarin/
  glitter = cute reveals; ascending whistles = risers; tring = announcements; answer
  right = results; bulb = insights; realistic typing = on-screen type-outs ONLY;
  app scroll = into screen recordings; peep = screen-rec underlay.
- **`sfx_map.json` schema** — one entry per bank file; rebuild on ANY bank change
  (Stage 0 fails on a map↔folder mismatch):
  `{"file":"pop motion.MP3","duration_ms":420,"tags":["pop","text"],"use_for":["sticker_pop"]}`
  Tag by filename meaning first, then ffprobe duration: <600 ms = pops, 600–1500 ms
  = whooshes/risers, >1500 ms = ambient/comedic. Ambiguous name → tags `["unknown"]`
  + one NOTES line for manual tagging; never re-ask.
- **The SFX must match the on-screen ACTION** (a pencil-writing GIF must not get a
  keyboard SFX).
- **Per-file level overrides:** every `success.MP3` segment plays at **−13 dB**
  (linear volume 10^(−13/20) ≈ **0.224**) — it is far louder than the rest of the
  bank. Set per segment via structured JSON.
- Scripted pairing audit before handoff: every visual start has a hit within ±0.15s;
  orphaned SFX deleted; SFX move together with retimed assets.

---

## 3B. WHAT AN SFX ACTUALLY MEANS (owner correction, 2026-08-25)

An SFX is **not a mood**. It is either a description of on-screen action, or a generic
accent for an asset entering. Three items in one review were wrong for the same reason:
the sound described something the viewer was not being shown.

### Class A - describes a screen recording that MUST exist

Never place one of these unless the matching screen recording is actually on the timeline.

| SFX | Means, literally |
|---|---|
| `app scroll.MP3` | a screen recording of **fast scrolling** |
| `click scroll.MP3` | scrolling **with clicks** in a recording |
| `computer mouse.MP3`, `pc mouse.MP3` | mouse interaction in a recording |
| `realistic typing.MP3` | a recording of **typing** |

Before placing any Class A sound, ask: *what recording is the viewer watching while this
plays?* If the answer is "none", it is the wrong sound. A placeholder counts only if a
real recording is going into it.

### Class B - generic accents, safe on any asset entering

| SFX | Use |
|---|---|
| `POP UI Sound.MP3`, `pop motion.MP3` | an asset popping in; short, so **good for rapid succession** |
| `peep.MP3` | **pasting** ("paste this prompt"), and general asset entry |
| a click sound | one deliberate action, and general asset entry |

### Class C - semantic, matched to the words

| SFX | Use |
|---|---|
| `error.MP3` | **"wrong"**, "won't work", "bad", "fails" |
| `answer right.MP3`, `success.MP3` | correctness, a passing result |
| `bulb sound.MP3` | a realisation |
| `tring.MP3` | a beat or step marker |
| `magic reveal.MP3`, `ascending whistles.MP3`, `kirarin glitter.MP3` | reveals and risers |

**Class C lands on the WORD, not the clause.** An `error.MP3` placed at the start of the
clause fired 1.7s before the word "wrong" and read as a random noise. Take the word start
from `words.json`.

These are reasons, not a lookup table. A sound not listed here is judged by the same
question: is it describing an action on screen, accenting an entrance, or naming a word?
