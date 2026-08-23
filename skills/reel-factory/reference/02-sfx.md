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

