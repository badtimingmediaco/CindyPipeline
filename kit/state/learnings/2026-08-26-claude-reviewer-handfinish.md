# 2026-08-26 — Claude Reviewer, round 5 hand-finish

Measured off `CZ_ClaudeReviewer_20260825_v3_round5` by diffing the engine's build
(`_order_bak_060504.json`, 105 segments) against the owner's finished state (157 segments).
Every number below was **read off the draft**, not estimated.

---

## THE BIG ONE — the centre band belongs to screen recordings

- **Drawn cards do not go in the centre. The centre is reserved for the owner's screen
  recordings, and a card must sit ABOVE it.** All four subagent cards were moved to
  *exactly* the same place — which is what makes it a law rather than a nudge:

  | | engine built | owner moved to |
  |---|---|---|
  | top edge | 0.3100 | **0.6771** |
  | centre y | 0.1392 | **0.5208** |
  | scale | 0.9398 | **0.8598** |
  | displayed | 1015×319 | **929×300** |

  Her words: *"I will be placing screen recordings in the centre."* So `card_geom` was
  competing for the one band she needs kept clear. `CARD_TOP` and `CARD_W` in
  `house_layout.py` are corrected to the measured values, and `verify_build` now fails any
  drawn card whose bottom edge drops below the reserved strip.

- **Keep drawing cards anyway.** Asked whether the pipeline should stop fabricating and
  emit a capture list instead, the answer was *"keep drawing them as placeholders"* — a
  complete timeline is worth more than an empty slot she has to remember to fill. She
  swapped three of them for real footage (`rev_card_packet` → a recording at 28.0,
  `rev_sub_q` → a recording + `slide 1.gif` at 13.6, plus two screenshots at 53.8) and
  kept the rest.

## Annotation marks ring LOOSELY

- **A red marker circle needs a pad of ~3.2, not 1.18.** She rescaled the circle on the
  scoring card from 0.2986 to **0.7466** — exactly 2.5×. Its ink centre landed at
  (901, 835); the `score_ai` region's centre is (890, 842), so the *target was right* — it
  was the *size* that was wrong. Final ink 657×521px against a 202×68px target: **3.25×
  the region width.**

  Her note was "it should ring more than the number", and the measurement says that means
  a generous loop, not a different region. A hand-drawn circle that hugs its subject reads
  as a box. It is allowed to run off frame — hers ends at x=1229 on a 1080 canvas.

  Encoded as a per-mark `MARK_PAD` in `layout.py`, because the right looseness differs by
  mark: a circle rings loosely, an underline sits tight.

## SFX — POP UI Sound is a five-frame tick

- **`POP UI Sound.MP3` is 0.167s (5 frames), every single time.** All seven instances in
  her finished draft are identical to the millisecond. The engine was capping it at 1.20s
  like everything else, so it rang on ~7× too long. Now capped per-file.

  Her other durations vary and are left alone: `pop motion` 0.167–1.2, `error` 0.267–1.1,
  `magic reveal` 1.7–2.1, `answer right` 1.033, `computer mouse` 1.1.

## Labels — she cuts them, every time

- **Write the label shorter than reads naturally; she will cut it otherwise.** Five of
  mine were rewritten and every edit was a shortening:

  | engine wrote | owner shipped |
  |---|---|
  | Containing only this | **Containing only:** |
  | Step 2: a brand-new chat | **Step 2:** |
  | Paste the packet in | **Paste the packet** |
  | Or just switch models | **Just switch models** |
  | Even better: | **For example:** |

  Nothing she kept unedited runs past ~21 characters. `verify_build` now prints a warning
  above 22, as guidance rather than a failure — length is a judgement, not a law.

## Meme swaps, and the reason in each

Not "her taste differs" — each swap tightens the mapping from the clip to the *action* in
the sentence:

- `homer_backs_into_hedge` → **`isolation-covid`** at 47.2. The line is "reduces context
  contamination". Homer backing into a hedge is *disappearing*; isolation is *separation*,
  which is what reducing contamination actually means.
- `magnifying_glass_examining` → **`wait-a-minute` + `waving-finger-no-noo`** across
  1.10–2.63. The hook is a challenge ("have you ever asked Claude to double-check its own
  work"), not an inspection. Two short clips in 1.5s where I had one long one.
- `chains_breaking_silhouette` → **`a-man-holding-a-chain`** at 23.13, same slot, same
  idea, better clip.
- `dr_evil_air_quotes` **moved** from "the impartial judge" (7.97) to "self-preference
  bias" (12.13), and a literal **`judge-juiz`** clip put on the judge beat. Air quotes are
  about insincerity; the judge beat wanted a judge.
- Dropped outright: `huge_document_stack`, `dicaprio_cheers_gatsby`.

She also moved `spiderman_pointing_spiderman` off-centre (x 0 → 0.348, +188px) and shrank
it 0.559 → 0.433, and pushed `dr_evil` up 89px — both consistent with clearing the centre.

## Smaller observations, recorded but NOT encoded

- **Title hold 3.80 → 3.40.** One sample, and her first clause ends at 3.40 in this video,
  so it may be per-video rather than a law. `TITLE_END_DEFAULT` left at 3.80.
- **The adjust layer was deleted.** Asked, and it is *not* a rejection: *"we are trying a
  new Descript-side colour grade, so the existing adjustment layer is currently of no use.
  But it's just a trial, nothing confirmed — keep adding it, I'll manually delete if
  required."* No change. Worth re-asking once the Descript trial concludes.
- The two CTA-area labels moved down ~243px (y 0.66 → ~0.405). Only two samples and both
  sit where her hands are in this take, so it is not promoted to a band change yet.

---

# Second pass — the full diff, and a correction to the entry above

The first pass read the diff with the added-text list truncated and asked about four
things. Re-read in full (79 additions, 27 removals, 33 of the additions being her
auto-captions). Two of the notes above are **wrong or incomplete** and are corrected here
rather than edited out — a lesson that had to be corrected is worth keeping.

## CORRECTION — "she shortens labels" is only a third of it

She does not simply cut. She makes the label **fit**, by whichever of three means suits:

1. **shorten** — `Containing only this` → `Containing only:`
2. **wrap onto two lines** — `Tell it to prove ⏎ you wrong`, `Reduces context ⏎ contamination`
3. **scale the paper down** — her paper-label scales are *not* the fixed 0.37 the engine
   uses. Measured across her own labels:

   | label | lines | scale |
   |---|---|---|
   | The reality: | 1 | **0.383** |
   | AI judges · Real independence · Remove bias completely · Just switch models | 1 | **0.370** |
   | Step 2: | 1 | 0.342 |
   | Just like people | 1 | 0.334 |
   | Reduces context ⏎ contamination | 2 | **0.306** |

   Short label → bigger. Long two-line label → smaller. She is fitting the frame, not
   obeying a character count.

   And she kept **"AI judges favor work from themselves" — 36 characters** — which blows
   straight through the 22-char warning the first pass added. It survives because it is
   **plain text at size 10**, not a paper label. So the warning was measuring the wrong
   thing.

**Therefore the engine should auto-fit a paper label — wrap, then scale — instead of
asking me to hand-shorten it.** That is now implemented; the 22-char warning is gone.

## There are TWO text registers, and I only ever used one

| | paper (torn-paper sticker) | plain text |
|---|---|---|
| size | 19 | 10–15 |
| scale | 0.31–0.38 | 0.44–1.0 |
| used for | the beat's headline label | small callouts pinned to a thing, and lower-third explainers |

Her plain-text placements, none of which the engine has ever produced:

- **`sub agent`** — size 15, scale 0.436, at **x +0.446**, y 0.34. A callout pinned to the
  *side* of a diagram, not centred.
- **`Context`** (x −0.257) and **`new chat`** (x +0.151) — size 15, scale 0.436, both at
  y ≈ 0.60, live at the same moment. Two callouts labelling two parts of one visual.
- **`AI judges favor work from themselves`** — size 10, scale 1.0, at **y −0.56**. A
  lower-third explainer line **below her face**, in a band the engine has never used.
- **`ChatGPT checking Claude`** — size 12 at y 0.317, which is exactly `LOGO_LABEL_Y`. The
  engine's logo-label row is correct and she adopted it unchanged.

## Rows the engine already gets right

Confirmed by her using them herself, unchanged: **y 0.407** for a meme's paper label (five
of her own labels sit there, and it is what `meme_geom` computes) and **y 0.66** for a
lower-band text row (`Original chat ->`, `Paste the packet`). No change needed to either.

## A mark that is not in our kit

`resource_id 7459434279869713725` — a **white dashed arrow**, ink 140×25 (5.6:1), used at
6.37–7.87 at scale 2.126, x +0.804, pointing in from the right edge. Our whole `ANNOTATE`
kit is red-marker; this is a quieter white pointer for indicating rather than correcting.
Added to the kit as `arrow_dashed_white`.

## Caption mishears — the real fix list

Her auto-captions garbled the brand words, and the actual errors are worth recording
rather than guessing at:

| caption says | should be |
|---|---|
| **Lord Code Sub Agent** | Claude Code sub agent |
| **claw chat** | Claude chat |
| **sites evidence** | cites evidence |
| **chat GPT check in Claude Work** | ChatGPT checking Claude's work |

"Claude" is heard as *Lord* and *claw*. That is the single most important word in her
channel, and it is wrong twice in one reel.

## Smaller things she did

- **The Claude app icon sits in the title card** (0.0–3.4, scale 0.269, centred) — the
  engine has never put a logo in the title.
- **She quotes a term when naming it**: `"Self-preference bias"` in quotation marks, where
  the engine wrote it bare.
- **She types arrows into labels**: `Original chat ->`.
- **Four identical copies of `waving-finger-no-noo` stacked** across 2.367–2.634 (8
  frames). Recorded, not imitated — four coincident segments may be an accident, and it is
  the kind of thing to ask about before copying.
- The two-column `sw_split`-style ending was not something she wanted: at 53.77–58.0 she
  put **two screenshots** there instead.

---

# Third pass — a correction the owner had to make, and what it exposed

## CORRECTION — the four stacked clips were a LOOP, and my diff tool lied

The second pass recorded *"four identical copies of `waving-finger-no-noo` stacked across
2.367–2.634 … may be an accident"*. Wrong on both counts. The owner:

> *"not an accident, that was actually an mp4 version of a gif, and was supposed to be
> looped. so i added 4 stacked together to let it run longer"*

They are **sequential, butted, each restarting at source 0.000**:

| # | timeline | source |
|---|---|---|
| 1 | 2.367 → 2.633 | 0.000 +0.533 |
| 2 | 2.633 → 2.900 | 0.000 +0.533 |
| 3 | 2.900 → 3.167 | 0.000 +0.533 |
| 4 | 3.167 → 3.400 | 0.000 +0.467 |

A 0.533s clip covering 1.033s. (Also played at **2×** — 0.533s of source in 0.266s of
timeline. Speed is a taste call about the clip; looping is arithmetic.)

**Why I got it wrong: the diff tool printed `times[0]` for every duplicate**, so four
sequential segments all reported the same start and read as four stacked ones. The same
bug misreported the three consecutive `pop motion` hits at 6.067 / 6.233 / 6.400 — which
are a deliberate **rapid triple-pop at 5-frame spacing**, not duplicates, and which
confirm "pop is the sound for rapid succession" more literally than I had understood.

The tool is fixed. The lesson is the one already written into THE_METHOD about gates and
repeated here at the analysis layer: **a measuring tool that misreports produces a
confident, wrong learning.** It is worse than no tool, because nothing about the output
looked suspect.

## Promoted — the engine now LOOPS a short clip instead of trimming its window

This was a real capability gap. Faced with a clip shorter than its beat, the engine said:

    ! simpsons_judges_scorecards.mp4: window 0.90s > source 0.80s - trimmed

and shortened the beat, leaving a hole before the next asset. The owner's answer is to
repeat the clip and keep the beat the length the VO gave it. That is now what
`overlays.build()` does — it lays down as many butted copies as the window needs, and every
copy takes the same geometry so a looped clip cannot change size halfway through. Opt out
per beat with `"loop": false`.

On the AI Sandwich rebuild it fired immediately and correctly:

    looped simpsons_judges_scorecards.mp4 x2 to fill 0.90s (source 0.80s)

This also removes the constraint recorded in that reel's notes — that a beat window had to
be sized down to its clip's real duration. It no longer does.

---

# Fourth pass — I destroyed the owner's work, and what guards it now

## What happened

Between roughly 05:00 and 15:06 on 2026-08-26 the owner hand-edited
`CZ_AISandwich_20260825_v1` after I delivered it. At 15:06, 15:14 and 15:16 I rebuilt that
same draft — each time `rm -rf` on the folder followed by a fresh `CZ_TEMPLATE` clone —
while applying the new card-band law, auto-fitting labels and clip looping.

**Their edits are gone and are not recoverable.** Checked and exhausted: all nine
`_backups/ai_sandwich_*` files (identical 405,697 bytes — each taken *after* the fresh
clone, so all mine), the 40 `.capcut-cli-history` snaps (all 15:16, mid-build),
`template-2.tmp.bak` and `draft_content.json.bak` (15:16 and 19:11, both after the wipe),
the `Timelines/` mirrors, CapCut's project recycle bin (nothing from today), other drafts
(none touched in the window), exports (none), volume shadow copies (unavailable) and File
History (not configured).

## The rule that did not exist

Every safeguard in this pipeline guarded **the write**:

> *CapCut must be CLOSED during every external write.*

I obeyed it every single time. Not one guarded **the target**:

> *Has this draft moved since I made it?*

**Closed is not the same as untouched, and a delivered draft is not scratch space.** The
build-order rule even says "always start from a fresh clone" — which is right for a *new*
build and catastrophic when pointed at a draft someone is working in. A rule written for
one situation became a weapon in another, and nothing checked which situation it was.

## Encoded

`draftio.record_build()` / `check_untouched()` and a `_state/build_provenance.json`
ledger. The engine fingerprints the canonical timeline of everything it produces, and
`build.py` refuses to touch a draft whose current fingerprint does not match:

    REFUSING TO BUILD
      CZ_ProvGuardTest has been EDITED since the engine built it at 2026-08-26T21:56:09.
      Recorded sha 5d5bae9e74093d71, current sha 1dcf54e57a4664a4.
      Rebuilding destroys that work and it is NOT recoverable.

Three behaviours, each tested end to end:

| situation | result |
|---|---|
| draft untouched since the engine built it | proceeds, prints `provenance: unchanged since …` |
| draft edited since | **refuses**, exit 3, names both fingerprints |
| draft exists with no build record at all | **refuses** — unknown provenance is not permission |

`--force` overrides, and says out loud what it is destroying. `build.py` also took over
cloning (`--fresh`) so no shell `rm -rf` can bypass the gate.

The stamp is written by **`enforce_track_order.py`**, not by `build.py`, because that is
the genuine last write — fingerprinting before it would record a hash the finished draft
never has, and every later build would cry "edited" on its own output.

One bug found while testing, worth its own note: the ledger was keyed by the raw path
string, so `C:/CapCut Drafts/X` and `C:\CapCut Drafts\X` became two entries and the guard
false-alarmed on an untouched draft. **A guard that cries wolf gets switched off**, which
would have defeated the entire point. Keys are normalised now.
