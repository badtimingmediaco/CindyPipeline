## 2026-08-25 — Claude Reviewer build (first run after the routing fix)

- **THE ROUTING REGRESSION WAS REAL AND EXPENSIVE.** Splitting the monolithic CLAUDE.md into
  a router dropped `master_reference.md` and `learnings/` out of the routing table. They
  still shipped and still landed in `_state/`, but nothing told the agent to read them, so
  no build had opened either since the repackaging. An editor's build came out weak and the
  first assumption was "it's Sonnet" — it was half the context missing. Both are now
  REQUIRED reading at Stage 3 and the stale `style_learnings.md` path is fixed.
  Lesson: when you repackage a spec, diff what the OLD one caused to be read against what
  the new one routes to. Shipping a file is not the same as loading it.

- **What reading them actually changed on this build**, concretely: memes chosen as human
  reaction clips rather than clever abstractions (Spider-Man pointing at Spider-Man for
  self-preference bias); stickers written as LABELS not echoed speech; meme heights at the
  ~430 target; and catching that the owner had already rejected my black ChatGPT tile in
  favour of their green mark. Every one of those came from the learnings, not the spec.

- **build_seo.py carried its own meme_geom that sized to the 475 CAP.** house_layout.py has
  had DEFAULT_H=430 since the Claude SEO hand-finish, but the builder never used it, so
  every meme since has shipped one size too large. Forked builders must import
  house_layout, never re-implement geometry.

- **verify_build.py asserted V1 == 2.512 exactly.** 2.512 is the FLOOR; the owner has raised
  it by hand every time we've measured (2.9688 Claude SEO, 3.63 GoHighLevel). A correct
  build failed its own verifier. Now checks `>= floor`.

- **The collision sweep flagged the owner's own layout.** A centre card's label bottom sits
  exactly ON the card's top edge (CARD_LABEL_GAP is the label's half-height), and the logo
  header does the same — 1 to 6 pixel boundary contact reported as clashes. Added an EPS of
  0.012 half-units on both axes: touching is not colliding. Kept small enough to still
  catch real overlaps, and it did catch one — a meme starting at 3.50 over a title running
  to 3.80.

- **Harvest the owner's own assets FIRST, again.** The real green ChatGPT mark was sitting
  in the Claude SEO draft's material paths at
  `OneDrive/Desktop/Cindy Zhu/Chief Agent Officer/ChatGPT logo.png`. Grepping a finished
  draft's material paths for the logo/icon you need beats making one every time.

- **Pillow has no ✓/✗ glyph in Poppins** — setting them as text renders tofu boxes, which is
  what the first card build shipped. Draw marks as lines, never as characters.

- **Embedded subtitle tracks are free accuracy.** The Descript export carried an SRT stream
  with her exact words; whisper supplied the word timings. Using both gave a clean transcript
  AND the brand-word fix list (whisper heard "chat to PT" and "come to a reviewer"), instead
  of trusting one source.

- Not shipped, flagged in NOTES: the annotation sticker layer. Planned, not built. Second
  build in a row where it was the thing that slipped.

## 2026-08-25 (round 2) — v1 rejected: "negative 20% work done"

Owner's words on the v1 export: *"so many glitches, irrelevant memes, and even memes with
full caption sized text and black bars on the sides."* Every one of those was accurate.

- **FRAME-CHECK EVERY CLIP. I PICKED MEMES BY FILENAME.** The spec has always required a
  frame check (no baked-in captions, no watermarks, margins on every meme) and I ran it
  zero times. Shipped: a Drake clip with hard pillarbox bars + a burned-in caption + a
  **vevo watermark**; a white-background cutout that read as a pasted box on her warm
  room; and a moody Supernatural still that is not a meme at all. Built `_state/meme_qa.py`
  — bars, near-white cutout borders, extreme aspect — which flags **8 of the 37 bank
  clips**. It also auto-crops bars, because rejecting a good meme over someone else's
  re-encode throws away the joke; the owner's own DeVito shipped at 844x385, a crop of a
  barred source.
  A filename is not a frame. The bank's names are descriptive and that is exactly what
  made trusting them feel safe.

- **The QA tool cannot judge the thing that matters most.** Bars and cutouts are
  measurable; "is this recognisable, does it match the beat's subtext" is not. The
  eavesdropping clip passes every mechanical check and is still wrong. The tool prints a
  contact sheet and says LOOK at it, because that step cannot be automated away.

- **Near-black borders are NOT a defect.** First version of the QA flagged DiCaprio-cheers
  and DeVito for dark borders — but DeVito is in the owner's own hand-finish. Darkness is
  a scene; bars are a defect. Removed that check rather than ship false positives that
  would train people to ignore the tool.

- **DENSITY: beat-by-beat is not clause-by-clause.** v1 anchored ~15 beats and shipped 69
  segments against a 162-segment reference — 93 per 80s vs 242. v2 anchors all 30 clauses
  and ships 101 (136 per 80s). The density mandate's "~25-40 overlays per 80s" badly
  understates what her finished reels actually contain; measure against a REFERENCE DRAFT,
  not against the number in the spec.

- **Don't pad to hit the number either.** The remaining gap to 242 is real and is mostly
  screen recordings this video does not have. Filling it with filler labels would be the
  same mistake in the other direction ("fill with SUBSTANCE, not memes").

- **The donor gets consumed.** The build deletes the sample paper sticker segment and
  caches it, but `gc_text_materials` then collected the donor TEMPLATE once its segment
  was gone, so the next run could not find it and died with `sticker=False`. A rebuild
  must start from a fresh clone of CZ_TEMPLATE, not from the previous build's draft.

- **A meme starting inside the title window collides with it.** Twice now: 3.50 and 3.62
  against a title ending at 3.80. First overlay cannot start before the title clears.

- **A card's own label must be time-boxed with `label_t`** when the card also carries
  sequential item labels, or the main label sits on the same row for the whole window and
  every item label collides with it.

## 2026-08-25 (round 3) — three revision rounds. The method changed, not just the build.

Owner: *"more than 1 revision round means this automation is fucking useless."* Fair. The
defects across rounds 1-3 all had one shape: **the JSON was right and the pixels were
wrong**, and verify_build.py passed every one. Full method in `_state/THE_METHOD.md`.

- **THE VISUAL GATE (`_state/visual_gate.py`) is now mandatory.** Renders V1 + media +
  TEXT AT REAL FONT/SIZE/POSITION + annotation stickers from CapCut's artistEffect cache,
  at 1080x1920, for every asset start. Fails on off-frame text, text-on-text overlap, and
  any sticker with no cached art. Two traps inside the gate itself: it first drew
  bounding boxes and not glyphs (hiding the very defects it existed to catch), and
  sticker GIFs are animated with an EMPTY frame 0, so a correctly placed underline
  looked missing. Take the frame with the most ink.

- **NEVER ESTIMATE A SOLVABLE NUMBER.** Title overflow, the word gap, logo sizing and all
  three annotations were eyeballed and all four were wrong. Now solved:
  `optical.optical_scale` (scale is not size - the ChatGPT mark fills 50.6% of its canvas,
  Claude's 100%), `optical.card_anchor` (we draw the cards, so every element's pixel
  coordinate is known), `optical.place_sticker_on` (a sticker's INK is off-centre - the
  red circle's is at (0.457,0.411), so placing by canvas centre misses).

- **TITLE TEXT IS WIDTH-CONSTRAINED BY ITS GRAPHIC.** The torn-paper row does not grow.
  "Its Own Mistakes" measured 495.6px against the 369.7px "5 Sub Agents" occupies, so it
  overflowed and threw a giant "akes" across the frame. Replacement "Its Own Bias" is
  357.0px - and "bias" is the video's real keyword, so the constraint improved the title.
  MEASURE EVERY TITLE ROW AGAINST ITS DONOR BEFORE BUILDING.

- **NEVER PICK AN ASSET BY FILENAME.** `_state/meme_catalog.json` is now the allow-list,
  curated by eye. Owner rule, absolute and reversing an earlier learning: ANY burned-in
  text disqualifies a clip, including a meme's own famous caption (GREAT SUCCESS, THE
  RESULTS ARE IN). Over-add memes, but every one must be a tight match.

- **A CHECK THAT LIES IS WORSE THAN NO CHECK.** A burned-caption detector was attempted
  and scored a clip with no text above one with a full caption. Deleted rather than
  shipped. 37 clips is small enough to look at once and record the answer.

- **DENSITY IS MEASURED AGAINST A REFERENCE DRAFT.** The spec's "~25-40 overlays per 80s"
  is stale; her finished reel is 242 segments per 80s. Following the spec number shipped
  a reel at 93.

- **THERE ARE FOUR COPIES OF THE TIMELINE, NOT TWO.** Root canonical + mirror, AND
  `Timelines/<uuid>/template-2.tmp` + its own draft_content.json. Writing only the root
  pair left the Timelines copy holding template content; CapCut read it, displayed an
  empty timeline, and saved that over a finished verified build. Every asset lost. This
  is the most dangerous failure found so far because the build reports success and the
  loss only appears when CapCut is opened.

- **Rebuild from a FRESH CLONE, never on top of a previous build.** The paper donor
  segment is deleted at the end of a build and its template then gets garbage-collected,
  so the next run cannot find a donor and dies.

## 2026-08-25 (round 4) — the owner's 11-point review. Two were systemic.

- **THE GHOST LAYER IS SOLVED, AND IT WAS NEVER MYSTERIOUS.** A `text_template` carries
  its OWN `attach_info.duration`, independent of its segment's. The title's paper row ran
  0->3.80s on the timeline while attach_info said **3.23s**, so the text vanished 0.57s
  early while its box stayed - which is exactly "something on the timeline that only
  shows its outline box". ALL 32 template segments were mismatched. Fixed at three
  levels: `base.py sync_attach()` when retiming, `clone_sticker` on creation, and a
  **ghost sweep** in build_reviewer that re-syncs every template's attach_info to its
  segment as the last structural act. Segment durations are frame-quantised and attach
  values are not, so even correct clones drift a frame - sweep unconditionally.

- **NEVER CLAMP A STYLE RANGE WHEN THE NEW STRING IS LONGER.** Replacing "into" (4 chars)
  with "catch" (5) left the style range at [0,4], so the final "h" had NO style and CapCut
  rendered it at giant default size splashed across the frame. `set_text` now forces the
  first range to start at 0 and the LAST range to end at len(new). This is why a huge
  stray letter kept appearing over the title.

- **ZERO GAPS.** The owner watches for 1-5 frame slivers between assets - they read as a
  flicker. `close_gaps()` butts any adjacent pair whose gap is under ~8 frames, per layer
  so a meme is never stretched to meet an unrelated label. Deliberate empty beats survive.

- **A LABEL MUST END WITH ITS CLAUSE.** "Rewrites what failed" ran to 42.60 while the next
  beat "Do this and:" fired at 42.14, so the new text appeared over the old one. Labels
  end when the clause they name ends (41.96), not when the card does.

- **TWO LABELS SIDE BY SIDE COLLIDE.** "ChatGPT" at x=-0.26 and "checks Claude" at +0.26
  rendered as "ChatGPTchecks Claude". One centred label under a logo pair, always.

- **A LOOSE MEME IS WORSE THAN NO MEME.** The owner rejected fry-take-my-money AND
  birdman on "want the exact two prompts" - both are money/scheming clips, neither is
  about wanting a prompt. There is no tight match in the catalog for that beat, so it now
  has none. "Over-add" means over-add TIGHT matches, not fill every gap.

- Spider-Man moved to "biased to its own work" - it is the self-reference joke and belongs
  on the sentence about favouring yourself, not on the sentence that merely names the bias.
