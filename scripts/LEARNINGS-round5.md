# Round 5 — the blueberry review, and the reasons underneath it

Owner review of `CZ_ClaudeReviewer_20260825_v2_blueberry`, 2026-08-25. Eighteen items.
This file records the **reasons**, not the rulings — a ruling copied forward without its
reason becomes the next wrong literal. Where a rule is context-dependent, that is said
explicitly.

---

## 0. TIMECODE — I had this wrong

The owner's timeline coordinates are **`HH:MM:SS:FF`**, not `MM:SS`.

    "49:01"  =  49 seconds + 1 frame  =  49.033s   (at 30fps)
    "38:13"  =  38s 13f               =  38.433s
    "42:24"  =  42s 24f               =  42.800s

Frames per second come from **the project settings**, not from an assumption. 30 is
typical here; read it off the draft (`fps` in the timeline JSON) before converting.

Every earlier note that read one of these as `MM:SS` is wrong and was interpreted at the
wrong moment in the video. `engine/timecode.py` now does the conversion so it is never
done in my head again.

---

## 1. WHY THE SAME DEFECTS SURVIVED A "FIX"

Round 4 shipped with the title touching, a mis-sized circle, and labels spilling off frame
— **and every automated gate passed.** That is the important fact. The gates did not
disagree with the render; they measured a *different picture* from the one CapCut draws.

Root cause: **`visual_gate.py` models text width instead of measuring it.**

    w_px = PIL_bbox / 100 * size * 4.39 * scale

Three things CapCut adds that the model did not:

| CapCut applies | Model did | Effect |
|---|---|---|
| `border_width: 0.08` stroke on every title row | ignored it | text renders wider on both sides |
| `shadow_distance: 5.0` at -45° | ignored it | a few more px right and down |
| the torn-paper **graphic** behind a sticker label | drew only the glyphs | the paper is wider than its text |

So a row modelled at 780px can render past 1080. **A gate that under-measures is worse
than no gate**, because it converts "I should look" into "it passed".

The rule that follows: **a gate must over-estimate, never under-estimate.** Where the true
value is unknown, bias the estimate toward failing. A false alarm costs a look; a false
pass costs a revision round.

### The bias-cancelling trick

For anything that is *relative* — the gap between two title words — the model's bias
largely cancels if both sides are measured the same way. So the correct rule for placing a
replacement title word is **preserve the gap the template itself used, measured in model
units**, not "34px" or any other absolute. The designer's spacing was visually right; the
same model-space number reproduces it whatever the model's absolute error.

That is why `TITLE_WORD_GAP_PX = 34.0` was wrong even though it was "measured": it was
measured *in the model's units* off a render whose real gap was ~6px. It encoded the
error.

---

## 2. SFX — what they actually mean

The owner corrected this at the level of principle, and it is the most reusable thing in
this review. **An SFX is not a mood. It is either a description of on-screen action, or a
generic accent for an asset entering.**

### Class A — describes a screen recording that MUST exist

Never use one of these unless the matching screen recording is actually on the timeline.
This is what made items 7, 8 and 13 wrong: the sound described an action that was not
being shown.

| SFX | Means literally |
|---|---|
| `app scroll.MP3` | a screen recording of **fast scrolling** |
| `click scroll.MP3` | scrolling **with clicks** in a recording |
| `computer mouse.MP3`, `pc mouse.MP3` | mouse interaction in a recording |
| `realistic typing.MP3` | a recording of **typing** |

### Class B — generic accents, safe on any asset entering

| SFX | Use |
|---|---|
| `POP UI Sound.MP3`, `pop motion.MP3` | an asset popping in; **good for rapid succession** |
| `peep.MP3` | **pasting** ("paste this prompt"), and general asset entry |
| a click sound | a single deliberate action, and general asset entry |

### Class C — semantic, matched to the words

| SFX | Use |
|---|---|
| `error.MP3` | **"wrong"**, "won't work", "bad", "fails" — on the actual word |
| `answer right.MP3`, `success.MP3` | correctness, a passing result |
| `bulb sound.MP3` | a realisation |
| `tring.MP3` | a beat/step marker |
| `magic reveal.MP3`, `ascending whistles.MP3`, `kirarin glitter.MP3` | reveals and risers |

**The generalisation:** before placing a Class A sound, ask *"what recording is the viewer
watching while this plays?"* If the answer is "none", it is the wrong sound. Class C must
land on the **word**, not near it — the `error.MP3` at 36:15 was 1.7s early because it was
placed on the clause rather than on "wrong" at 38:10.

---

## 3. MEMES — the reasons, not the verdicts

Three rejections this round, and the reason differs in each:

**`roxbury_bouncer_denied` — banned outright.** Not merely a weak match: the owner's note
is *"super bad, should never be used again."* The deeper error was reading the VO's
**word** instead of its **meaning**. The line is about *removing* the old context, not
about *rejection*. "Denied" was a synonym-level match to a word that was not even the
point of the sentence.

> **The search-term rule:** search the *action* the sentence describes, not an abstract
> noun from it. For "the old context vanishes" the terms are *separating, chopping,
> cutting away, removing, wiping* — not *denied*.
>
> Corollary, from the owner: a crossed-arms "no" gesture IS right when the context really
> is rejection. The clip is not banned as an image; the *mapping* was wrong.

**`charlie_day_conspiracy_board` at 38:13 — wrong axis.** The beat is about **grading**;
the meme is about **explaining/overanalysing**. Both are "intellectual activity", which is
how it slipped through. Matching on a category rather than on the specific action is the
same error as above. Correct choice: a **scoring** meme (the Simpsons scoring/judging
panel).

**`spongebob_imagination_rainbow` — fine, but beatable.** Not wrong; just not the tightest.
"Give it real independence" is literally about **freedom**, so *broken chains* is the
tighter image. Worth recording that "acceptable" and "tight" are different bars, and the
owner wants tight.

---

## 4. PACING — one card per clause, not one card per section

The biggest structural note. The subagent card sat on screen for **9.3 seconds** carrying
four bullet lines, while four separate text labels fired over it.

The owner's correction: **each line gets its own card, entering on its own clause, and the
previous card ends.** Same for the "grades every criterion / cites evidence / corrects
failures" beat — three cards, not one card with three rows.

The reason given is worth keeping verbatim in spirit: *"this way people specifically focus
on what part is being talked about instead of 1 singular card containing all elements
together."*

Two things follow:

1. **A card is a unit of attention, not a unit of information.** If the viewer must be told
   which row to look at, the card is doing too much. Splitting is not decoration — it is
   what makes the edit read fast.
2. **A long-lived asset is a smell.** Any card alive for more than ~2.5s while other
   layers change over it should be examined. This is now a check
   (`verify_build`: `[INFO] long-lived assets`).

Same principle behind item 6: the packet card must not appear on *"produce a review
packet"* — at that moment the right visual is a **file icon labelled "review packet"**.
The card full of contents appears only when she says *"containing…"*. **Show the thing
being named at the moment it is named**, and show its contents only when the contents are
named.

---

## 5. GAPS — the exact threshold

Previously `close_gaps(max_gap=0.26)` (≈7.8 frames). The owner's rule:

> if the gap between two assets is **less than 5 frames**, extend the former asset to end
> at the exact frame the latter starts.

So the threshold is `5 / fps` seconds, derived from the project's real fps, and the join is
exact — not "close enough". Anything ≥5 frames is a deliberate beat and is left alone.

---

## 6. THE PROCESS FAILURE UNDERNEATH ALL OF IT

Round 4 and round 5 share one cause, and it is not any individual defect:

**I trusted a proxy of the render instead of the render.** The visual gate is a model.
`verify_build` reads JSON. Neither one is the video. Both passed while the owner's own eye
found nine visual problems in the first pass.

The fix is not a better model — it is to stop treating the model as sufficient:

- the gate must **over-estimate** widths so it errs toward failing (done)
- the gate must render the **paper graphic**, not just the glyphs, because the paper is the
  thing that overflows (done)
- the gate must cover **every frame**, not only the moments an asset starts — several of
  these defects were mid-asset (done: `--every N`, e.g. `--every 1` for every frame,
  `--every 15` for one every half second). **An MP4 proxy is NOT built yet** — that is the
  thing that would let the owner scrub a composite instead of reading a contact sheet, and
  it is the top of the next session's list.
- **the owner's CapCut preview is the ground truth.** When the gate and the preview
  disagree, the gate is wrong and gets calibrated. A disagreement is a bug in the gate,
  never an acceptable difference.

---

## 7. WHAT IS A HARD RULE AND WHAT IS CONTEXTUAL

Recorded explicitly, because the owner asked for reasons rather than commandments.

**Hard, apply everywhere:**
- Class A SFX require the matching screen recording to exist.
- Class C SFX land on the word, not the clause.
- Gaps under 5 frames close exactly.
- Never place a meme that carries burned-in text.
- A gate may over-estimate; it may never under-estimate.

**Contextual, decide per video:**
- Card splitting: right when a list is being *enumerated aloud*; a single card is fine when
  the viewer is meant to take in a comparison at a glance (the two-judges score card is
  correctly one card, because the *comparison* is the point).
- `roxbury_bouncer_denied`: banned by owner instruction, so treat as hard for now — but the
  underlying lesson is about mapping, not about that file.
- Meme density: over-add, but every one tight. "No tight match" remains a valid answer.
