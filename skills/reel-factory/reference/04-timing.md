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
