# Memes & what fills the screen

> Part of the Cindy Zhu Reel Factory spec (v3.0). Loaded on demand by the
> `reel-factory` skill - see SKILL.md for the routing table.

## 4. MEME SELECTION — CONTEXT-FIRST, NEVER KEYWORD-FIRST
Bad memes come from typing a generic keyword into Tenor and taking the first result.
The process is understanding-first, and every step leaves a written trace in the plan:

**4.0 POPULARITY & BREADTH — cast a wide recognizable net, and OVER-ADD.** The core is
famous TV/cartoon/film moments (SpongeBob, Simpsons, The Office, Pixar, Looney Tunes,
Marvel, Wolf of Wall Street, Mr Bean, Terry Crews) and instantly-recognized internet
memes (Roll-Safe, "this is fine", skeptical kid, Drake) — but a frame-study of her
actual 76-meme library shows her taste is BROADER than "top-5 famous scenes only".
It also leans hard on: **relatable reaction / B-roll** (someone typing furiously, a cat
at a laptop, photographer & photoshoot BTS, a bored exec at a desk, a scream, a
facepalm, a talk-show host reacting); **"smart / analyzing" bits** (Roll-Safe head-tap,
magnifying-glass "allow me to examine", chalkboard math, equation-overlay eyes,
confident kid pointing up); **text-overlay reaction memes** ("NOPE", "REJECTED", "JUST
TAKE IT", "YOOOO", "SUBMIT!"); and the occasional **absurd** one (army cats, top-hat
weasel). So do NOT reject a clip just because it isn't a top-5 scene — if it's
recognizable OR relatably funny AND matches the subtext, it qualifies. Reject only
truly generic stock with no point ("funny robot"). Her library palette by theme —
draw from it: content/shoot → camera/photographer/photoshoot-BTS · let-AI-work →
laptop-typing / cat-at-laptop · rejection/judging → REJECTED stamp / skeptical
interviewer / Simon-Cowell facepalm · money → Simpsons cash / Wolf-of-Wall-St ·
smart → Roll-Safe / magnifying-glass / chalkboard · imagination/possibility →
SpongeBob rainbow · done/exhausted → tired SpongeBob · hype/win → Terry Crews /
DiCaprio-mic / "YOOOO" / dancing exec.
**OVER-ADD, never under-add — this is a hard rule.** Finished reels show only ~2–5
memes because the EDITOR REMOVED the extras; that is the POST-edit count, NOT the
target. The automation must place a meme on EVERY beat where one plausibly fits
(expect ~1 per 4–8s ≈ **8–15 on an 80s reel**) so the human editor SUBTRACTS. Removing
a meme is one click; sourcing + placing a missing one is a whole re-run. **When in
doubt, ADD it.** Fear of over-adding is the wrong instinct here.

**4.1 Read the transcript like a comedy writer (before any searching).**
For each candidate meme beat write a MEME BRIEF in the plan:
- `line`: her exact words at that moment
- `surface`: what the words literally say
- `subtext`: the hidden context — the emotion or situation she's REALLY invoking
  (exhaustion, relief, greed, smugness, fear, "finally!", "that's illegal-good",
  being exposed, pretending to work…). This is the layer the meme must match.
- `joke`: the one-line comedic translation ("she's describing every parent at 9pm",
  "the AI is basically a genie", "free stuff = unlimited greed")
**4.2 Cast the scene from memory FIRST.** From the subtext, name 2–3 SPECIFIC famous
scenes that embody it (show/film + moment): "Mr Krabs' dollar-sign eyes", "WALL-E
looking up confused", "SpongeBob ready to fight", "The Office — Michael screaming
NO". If you cannot name the show AND the exact moment, you don't have a meme yet —
think longer instead of searching vaguer.
**4.3 Search by the SCENE, not the emotion.** Query Tenor with the scene's own name
("mr krabs money eyes", "michael scott no god no"), 2–3 query variants per slot.
Generic emotion keywords ("funny robot", "tired gif") are banned as primary queries.
(**The Tenor v1 API and its public demo key `LIVDSRZULELA` are DEAD** — v1 returns
403 on both `g.tenor.com` and `api.tenor.com`, and v2 rejects the demo key. Do not
retry them. **Use `_state/tenor_fetch.py`**, which needs no API key and no browser:
it GETs `https://tenor.com/search/<slug>-gifs` (the raw HTML server-renders ~49
`/view/` links), then GETs each view page and reads
`<meta property="og:video" content="...mp4">` — that IS the MP4. Watch the regex:
the tag carries `class="dynamic"` BEFORE `property=`, so a pattern anchored on
`<meta property=` silently finds nothing. Run it as
`python _state/tenor_fetch.py --queries queries.json --out <dir>` with
`{"M1":["query a","query b"],...}`. Discard any candidate under ~0.5s — Tenor
serves a lot of single-frame 0.04s clips that look fine in a still and are useless
on the timeline. Legacy v1 shape, kept for reference only:
**ALWAYS download `media[0].mp4.url` — NEVER `media[0].gif.url`.** Tenor GIFs are
256-colour, dithered, often half the frame rate and 5–10x the file size of the same
clip; the MP4 is the same footage in full colour and imports into CapCut cleanly.
If a result has no `mp4` entry, take `media[0].tinymp4.url` / `media[0].nanomp4.url`,
and only if the result carries no MP4 of any kind, skip that candidate and take the
next search hit — do not fall back to the GIF. Save every meme to the bank as `.mp4`.)
**4.4 Audition ≥3 candidates per slot — with WRITTEN evidence.** Download them,
extract a frame from EACH (ffmpeg), LOOK at it, and record a one-line verdict per
candidate in the plan ("frame checked: clean / REJECTED: baked caption 'Claude
Code'"). A meme placed without its frame-check verdict on record is a spec
violation — a captioned GIF shipped precisely when this step was skipped. Score:
recognizable OR relatably funny (§4.0 breadth) and clear in one frame? · caption check —
the meme's OWN iconic short text ("NOPE", "REJECTED", "shut up and take my money") is
FINE (it IS the meme); reject only ADDED/off-topic captions, a competitor-tool name, or
a watermark that looks like a lazy repost · full-frame content (no transparent sticker
GIFs)? · **downloaded as .mp4, not .gif (§4.3)?** · emotion matches the subtext? ·
watchable at 0.7–0.85 scale for 1–2s?
**If the beat names a tool, stop — that slot belongs to the logo (§2), not a meme.**
Pick the best; **when a beat plausibly fits, ADD a meme (over-add, §4.0) — the editor
trims.** Only a genuinely off-brand or no-scene beat is left empty; do not withhold a
fitting meme out of caution.
**4.5 Bank first, then Tenor.** Check `04_assets/memes/bank/` (vetted, reusable) before
searching; every winner gets copied into the bank with a descriptive name, so the
library compounds and repeat searches disappear.
**4.6 Placement mechanics — DENSITY MANDATE (the automation must do ~80% of the
assembly; a sparse reel defeats the purpose and is a shipped defect).** Cindy's real
reels have near-constant visual activity. TARGET THE HIGH END, not the floor:
**~25–40 overlays and ~45–60 SFX per 80s** (≈ one visual overlay every 1.5–2s of
runtime; captions always on; a visual + first-frame SFX on essentially EVERY beat).
Every clause is a candidate — her exact punchy words → a sticker, every emotional
turn → a meme, every tool mention → a logo, every proof moment → a screenshot/screen-rec.
At Stage-3 plan time walk the transcript beat-by-beat and assign an asset to each beat,
then count overlays-per-10s and FLAG every gap >2.5–3s with no new overlay and fill it.
Concretely a ~40–90s reel carries **~15–25 SUBSTANCE overlays + full word-timed captions
+ ~25–45 SFX, PLUS an over-added meme layer (§4.0, ~8–15/80s)** on top — total overlays
run high on purpose. Fill from the **§4C ASSET MIX: substance is the backbone (screen-recs,
outputs, prompt cards, section posters, label stickers), memes are a full layer over-added
on top for the editor to trim.** The failure mode is SPARSE (too few of either) — NOT
too many. Leave a beat empty ONLY when both no substance overlay AND no fitting meme apply
(rare) — emptiness is the exception, never the default.
Meme (MP4) segment duration ≤ real file duration (ffprobe); `replace-media --retime`
refits to the new clip — re-trim if long (trim keeps target start; never shift after).
The paired SFX must match the on-screen ACTION. No cringe/punching-down; dry humor OK.

## 4C. ASSET MIX — WHAT ACTUALLY FILLS THE SCREEN (frame-study of 6 finished reels)
TWO layers, both dense. **Layer A = SUBSTANCE (the backbone):** every beat gets an
overlay from the priority list below — this is what a how-to/setup reel is mostly made
of and it must NOT be sparse. **Layer B = MEMES (over-added on top, §4.0):** on top of
the substance, add a meme on every beat where one plausibly fits (~8–15/80s) for the
editor to trim. Finished reels look ~80% substance / few memes only because that is the
POST-edit state — the automation ships BOTH layers full. Two failure modes, both
rejected: (a) sparse — too few overlays of either kind; (b) memes as the ONLY filler
with no substance backbone. Do both. Fill each substance beat from THIS priority, top
first:
1. **Screen recording + red arrow/cursor annotation** — the #1 overlay for how-to / setup /
   prompt videos. Shows the exact action (typing the prompt, clicking the button); a red
   arrow/box points at the key text/button. Placeholders (System-font cards, §2) until the
   owner records — for a build/setup video these are the MAJORITY of overlays.
2. **Generated outputs & result screenshots** — the actual thing produced (poster,
   dashboard, app, resume, portfolio, essay, the built feature). Proof it works.
3. **Numbered-section posters/cards** — for "N things / skills / roles" videos, ONE per
   named item with a CORNER NUMBER sticker + bold label ("THE REWRITER", "THE HIRING
   MANAGER", "CLAUDE ARTIFACTS"). **Draw these yourself with Pillow** — see
   `08-cards.md`. This build has no image-generation module: no OpenAI, no ChatGPT,
   no Remotion, no Hyperframes. Claude draws every card.
4. **Prompt / formula cards** — the actual prompt or formula on a paper / torn-paper /
   black message card ("You are a world-class designer…"; "accomplished X, as measured by
   Y, by doing Z"; Claude's blunt replies as text-message cards).
5. **Infographics / diagrams** (ATS hexagon, OODA loop) and **app-icon / logo cards**.
6. **Memes** — the comedic layer, OVER-ADDED on top of the substance (§4.0): a
   recognizable-or-relatable meme on every fitting beat; the editor trims to the final few.
- **Stickers are LABELS, not echoed spoken words.** They NAME the on-screen visual or mark
  the step: numbered labels ("2 Competitor ads-extractor", "1. Diagnose"); content labels
  ("Art direction", "Composition", "Reference", "Result", "Directing", "Copywriting");
  STEP labels ("Go to Claude", "Then Connectors", "Add Custom Connectors", "Try this!",
  "Here's how >"); status callouts ("LIVE", "4k", "No Editing needed!", "Ready to post and
  sell"). Pair each LABEL above its illustration/screenshot below.
- **Pick the SUBSTANCE mix by video TYPE at Stage 1 (this decides Layer A):**
  · Setup / how-to / "connect X to Claude & build" (GoHighLevel, Higgsfield-MCP) →
    70–90% SCREEN-REC placeholders w/ cursor annotations + STEP-LABEL stickers.
  · Tool / output showcase (Reve poster tool) → generated outputs + prompt cards +
    Reference/Result comparison pairs.
  · "N skills / things / roles" (resume, 7-skills) → numbered posters + per-section
    screenshots + number stickers.
  · Prompts / codes (5 secret codes) → prompt screen-recs + result screenshots + message cards.
  (The meme counts in FINISHED reels — ~1–2 setup, ~2–5 playful — are POST-edit keeps, NOT
  automation targets: Layer B still over-adds per §4.0 regardless of type; the editor trims.)
- **Why the observed memes worked (all specific + subtext-matched):** Roll-Safe
  "smart" at "can't be detected"; deadpan cat at "polite/blunt"; clueless dog-at-laptop at
  "just pasting their resume"; chalkboard math at "the hardest part"; a movie-director
  character at "Claude does the directing." Aim for that sharpness — but per §4.0 breadth a
  relatable reaction clip also qualifies, and per §4.0 over-add you place one on every fitting
  beat (substance still fills the beats where no meme lands). Memes are a full layer, not a rarity.

