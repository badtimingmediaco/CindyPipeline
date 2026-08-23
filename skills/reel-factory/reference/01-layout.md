# Canvas, layer stack & layer specs

> Part of the Cindy Zhu Reel Factory spec (v3.0). Loaded on demand by the
> `reel-factory` skill - see SKILL.md for the routing table.

## 1. CANVAS & LAYER STACK
1080×1920 @30fps output canvas. Cindy's RØDE wireless mic is always visible — nothing
may cover it (captions included). Source may arrive 1440×2560 (same ratio; scales
cleanly — note it, never crop).
Track order (bottom→top), enforced after EVERY write session: **V1 talking head
(index 0) → adjust layer (index 1 — owner's color grade: NEVER change its grading
parameters, but DO trim its duration to exactly V1's length every build, and enforce
array index 1 — CapCut re-floats it on open) → memes/B-roll → logos (dual icons and
their labels each need SEPARATE tracks — same-track segments cannot overlap in time)
→ screen-rec placeholders → captions → paper stickers → title → CTA.** Every segment's `track_render_index` must
equal its track's array index (both CapCut AND capcut-cli shuffle order — renumber as
the last step of any session).
Audio: A1 VO — **boost the base descripted video's segment volume by +8 dB**
(CapCut `volume` is linear: 10^(8/20) ≈ **2.512**; set on the V1 segment via
structured JSON — the CLI's volume options cap at 1.0; **+8 dB is the FLOOR — the owner
has raised it to 2.97 (+9.5 dB) and 3.63 (+11 dB) on their last two finishes, so set
2.512 and flag the level in NOTES**); beyond that never touch her
levels → SFX on multiple tracks (tails may overlap) → music bed (duck −12 dB, only
if provided).

## 2. LAYER SPECS
**UNITS:** `clip.transform` values are fractions of **HALF** the canvas dimension
(±1.0 = frame edge; +y = UP). y −0.56 = 78% down; y +0.48 = 26% from top. Deriving
coordinates from full-frame measurements halves everything and parks assets on her
face — this exact bug shipped once.

| Layer | Vehicle | Scale | Position | Rules |
|---|---|---|---|---|
| Captions | **DO NOT BUILD (owner rule 2026-08-20).** The owner runs CapCut's auto-caption tool in the UI, which also gives the word-by-word reveal the automation cannot produce (§7a bans hand-attached caption animation). Build ZERO caption segments. | — | — | ≤32 chars/cue, word-timed; pop-in = scale keyframes 0.85→1.03→1.0 (~5 frames) in CapCut's exact keyframe schema (§7a) |
| Title LINE 1 | plain **Markerist** text, white, **basic drop shadow** | ~1.0–1.3 | (0, +0.69…+0.72) | short lead-in ("how to", "I let"); ONLY this first text layer keeps an intro animation |
| Title LINE 2 | **"Claude" in orange (#e8856a) Awelier** + any additional words as separate white Markerist segments on the same row | ~1.0–1.4 | (0, +0.575), words spread on x | the word "Claude" MUST appear in the title, always orange Awelier; per-word segments (no per-char color ranges exist) |
| Title LINE 3 | the video's MAIN KEYWORD (e.g. "5 Sub Agents", "Bedtime Stories") in **Awelier on the torn-paper template** (paper-cutout copy) | ~0.39 | (0, +0.44…+0.47) | 1–3 words only; this is the payoff word of the whole video; the 3 lines concatenated must read as one grammatical sentence (Stage 3 grammar law) |
| Paper stickers | the torn-paper text template cloned from the sample layer | 0.33–0.41 | above head (0, +0.35…+0.64) or below face (0, −0.37…−0.45); pairs x ±0.44…0.51 | 2–5 of her EXACT spoken words; 15–18/video; holds 0.4–3.3s; NEVER in the face band (−0.35…0); never repeating the title's words |
| Memes | full-frame-content **MP4 clip** (never the .gif — see §4.3; no cutout stickers) | **size by DISPLAYED px, NOT raw scale** | (0, 0) | **SIZE LAW: compute displayed size = src × min(1080/w,1920/h) × scale, and cap it at ~940px wide × ~600px tall (26–32% of frame height) — that is the measured house pattern (her screen-rec cards render ~1015×543px = 28%; median overlay 18%). Raw scale 0.7–0.85 is only correct for LANDSCAPE sources; applying it to a SQUARE source yields an 842px monster that buries her face — this shipped. Centre at y=0 like her screen-rec cards: eyes stay clear above, mic clear below** |
| Screenshots/UI proof | image/video card | 0.6–0.9 | centered mid-upper | |
| **Screen-recording PLACEHOLDER** | plain **System-font** text layer, white, size ~12 | ~1.0 | centered (0, +0.1) | spans the exact shot window; text = the precise capture instruction. **add-text does NOT wrap — hard-wrap the string yourself with `\n` every ≤28 chars, max 4 lines** (e.g. "R2: record pasting the\nprompt into Claude,\nzoom the send button"). Owner replaces with the real recording; placeholders listed in NOTES |
| App logos | app-icon PNG, square, 18–22% corner rounding — NEVER circular. Prefer the REAL installed app's icon resources or the tool's official apple-touch-icon; never repo/stub icons (the microsoft/vscode GitHub icon is an unbranded stub). Build with Pillow (white/brand square + art + rounded-rect mask, 800px) | 0.28 | dual: x ±0.48, y +0.48, no "+" between, icons AND labels on separate tracks; single: (0, +0.44) | label = **Markerist, size 12, white #faf7f2, scale 1.0**, NO animation, at (±0.48 or 0, +0.23). capcut-cli add-text cannot set fonts — add-text first, then structured-edit the text material: `content.styles[0].font` id+path copied from the template's own title material, plus material-level `font_path`/`font_resource_id`. Fires at the FIRST mention of each tool; replaces any sticker/meme naming the same tools |
| CTA card | the template's planted comment-card layer | as planted | as planted | shift to the CTA line, rewrite its text (e.g. Comment "WORD"), trim to end before video end; NEVER build your own |
- **MEME + LABEL PAIRING LAW (owner-authored 2026-08-20, measured from their own edit —
  reproduce it exactly):** every meme/graphic is CENTRED (x=0) with its **TOP EDGE at 8.4%
  of frame height**, and its label sticker is CENTRED and **straddles the meme's BOTTOM
  edge**. Formulas, in half-canvas units:
      displayed_h = src_h × min(1080/w, 1920/h) × scale
      (target 430px tall — the owner's measured typical; hard caps 844px wide × 475px tall)
      meme_y      = 0.832 − (displayed_h/2)/960
      label_y     = meme_y − (displayed_h/2)/960 + 0.023
  These reproduce the owner's hand-placed doom-scrolling values (meme y=0.585 scale 0.782,
  label y=0.361) to 3 decimals. Never size a meme by raw scale alone.
- **THREE PLACEMENT GRAMMARS — pick by WHAT the asset is (measured from the owner's own
  Claude SEO hand-finish, 2026-08-20; all of it is code in `_state/house_layout.py`, which
  every build script must import rather than re-deriving):**
  1. **TOP BAND** (`meme_geom`) — memes, gifs, small illustrative cards. The pairing law
     above: centred, top edge 8.4%, label straddling the bottom edge. Target **430px tall**,
     ceilings 844×475. A clip with aspect ≥ 2 is width-driven instead (it would be
     unreadable at 430 tall). Reproduces their DeVito 844×385 and Linus 694×430 exactly.
  2. **CENTRE BAND** (`card_geom`) — anything the viewer must READ: real screenshots,
     screen recordings, dashboards, prompt/result cards, a prioritised list. Centred at
     **y ≈ +0.04, ~1015px wide**, and the label goes **ABOVE the top edge (+0.085)**, NOT
     straddling. This is the house screen-rec card; sending dense UI through the top-band
     law instead shipped four unreadable beats.
  3. **TITLE-CARD BAND** — whatever shares the screen with the opening title lives in the
     **LOWER third (y −0.18…−0.48)**, small, and may bleed off the left frame edge. A motif
     drawn across her face at y +0.12 was rejected. The title itself may hold to ~3.8s.
- **LOGO ROW (corrected, measured):** icons at **y +0.493** scale **0.225**, plain white
  labels directly under them at **y +0.317**, x **∓0.518** for a 3-up row, under a paper
  lead-in ("Checks whether:") at y +0.700. Icons enter **one at a time on their own spoken
  name** and accumulate until the beat ends. y +0.12 is the title-card band, never the logos.
- **RED-MARKER ANNOTATION IS A REQUIRED LAYER, not a garnish (§4C already calls it the #1
  how-to overlay).** Every screenshot/UI card gets a red circle, arrow, underline, box or
  cursor-hand pointing at the thing being discussed. Use the owner's own CapCut sticker set:
  `_state/sticker_kit.json` (43 stickers harvested from 26 of their drafts) via
  `house_layout.place_sticker(...)`, which deep-clones a real rendering sticker segment.
  Their most-used mark is the red circle `7470375665200549181`.
- **FAKE THE NUMBERS, NEVER THE BRAND (owner, 2026-08-20).** Invented metrics in a mock are
  fine ("just fill in fake numbers"). A generic IDENTITY is not: every proof visual must
  carry **her real brand** — cindyzhu.com.au, her avatar, the coral accent, and real named
  competitors around her. A card saying "yoursite.com" reads as a placeholder and gets cut.
  Prefer a **photoreal product mock** (image-gen) over a flat HTML card for search results,
  AI answers and app UI.
- **A summary RE-PLAYS its visuals.** When she recaps items already shown, put each item's
  own card back on screen with its label — never a stack of text lines.
- **TEXT LAYERS ARE ALWAYS CENTRED (x=0).** No left/right split pairs. When two or more
  text layers share a frame, STACK them vertically ~0.18 half-units apart, top-down in the
  order she says them (e.g. "The hook" / "The format" / "Storytelling") — never side by side.
- Coral accent **#e8856a**; black stamp boxes for numbers; pill badges for tool names.
- **No-spill law (EVERY text layer, checked at plan time AND in §7b) — MEASURE,
  don't estimate:** load the material's ACTUAL font file with PIL (the ttf path is in
  the material's `content.styles[0].font.path`; template title materials are
  **size 15**, not 12) and measure the rendered pixel width, calibrating px-per-unit
  against a known-good row in the template itself. Keep total row width ≤ ~980px on
  the 1080 canvas. The old `chars × size × scale × 4.7px` heuristic under-measured by
  ~25% and shipped an off-frame overlapping title — an UNDER-measuring model can
  never approve a row: if PIL is somehow unavailable, multiply the heuristic by 1.3
  and still treat the result as optimistic. Over budget → scale down, shorten, or hard-wrap with `\n`
  (CapCut text never auto-wraps).
- Title-card exclusivity: nothing else on screen 0–3.2s; first meme ≥3.3s.
- **GLOBAL COLLISION LAW (all asset types — this shipped as a logo rendered on top of
  a meme):** at plan time, compute every visual asset's bounding box (position ±
  scale×media dimensions, in half-canvas units) across its time window. **No two
  visual assets may overlap in BOTH space and time, ever** — sticker/meme/logo/
  screenshot/placeholder/title, any combination. The only sanctioned pairing is
  sticker-above + meme-below (label+illustration), and only with boxes verified
  non-touching (≥0.04 half-units clear) and ONE shared SFX hit.
- **Logos are exclusive occupants:** while a logo is on screen, no meme, screenshot,
  or placeholder may be visible anywhere in frame. If a beat names or depicts a tool,
  the LOGO is the asset for that beat — a meme about the tool is auto-rejected at the
  brief stage (§4.1), never layered under the logo.
- **Title rows may not touch:** measure each row's rendered height (PIL, §2 width
  law); rows stack with ≥0.02 half-units vertical clearance — line 3's paper box top
  edge must clear line 2's descenders (this shipped once as "Claude" tail touching
  the paper box).
- **TWO TEXT LAYERS AT THE SAME TIME — split upper/lower (owner rule):** two text
  layers MAY share a time window when one sits in the UPPER half (above-head band,
  y +0.35…+0.64) and the other in the LOWER half (below-face band, y −0.37…−0.45).
  When a second text layer is needed and the upper band is occupied, place it in the
  lower band — do NOT drop it and do NOT shift its timing off its word. Never stack
  two text layers in the SAME half at the same time.

