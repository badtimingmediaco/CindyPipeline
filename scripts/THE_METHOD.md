# THE METHOD — how this stops shipping errors

Written 2026-08-25 after the Claude Reviewer build needed three revision rounds; rewritten
the same day for **version blueberry**, after an audit of every learning file found that
**76% of the ~103 defects that ever reached the owner were mechanical**, not taste:

| Root cause | Count |
|---|---|
| A — engine bug (deterministic, fixable once) | 30 |
| B — a number estimated that could have been solved | 30 |
| D — process / environment | 18 |
| C — actual creative judgement | 25 |

Berry's answer to A and B was to write the rule down. Blueberry's answer is that **a rule
you have to remember is a defect waiting for a busy day.** Everything below is either
enforced by code or is explicitly a judgement call.

---

## 0. THE SHAPE OF A BUILD (blueberry)

```
_state/engine/          ONE engine. No per-video fork, ever.
_runs/<name>/spec.json  The ~50 values that are a choice for THIS video.
python _state/build.py _runs/<name>/spec.json
```

Berry had two builders sharing **490 identical lines**. Four of the most expensive fixes
lived in one and not the other, and `build_seo.py` still carried the `save()` bug that
destroyed a finished build. **A fix that lands in a fork has a half-life.** Both forks are
now in `_state/_retired/`.

## 1. A SPEC MAY NOT CONTAIN GEOMETRY

No `x`, `y`, `scale`, `target_w`, `anchor`, or pixel width. `engine/spec.py` **hard-fails**
on any of them and names the band to use instead.

This is the fix for the recurrence the owner asked about. Bucket B kept coming back after
being "fixed" because a value was solved once, by hand, then pasted forward as a literal:

```python
L2_X = {"catch": 0.2973}                          # solved once, right once
annot=[("circle", 0.6890, 0.0851, 0.4099, ...)]   # correct only for that revision of that card
OPT_CHATGPT = optical.optical_scale(...)          # computed on line 63, never used
```

A literal is a measurement that has stopped tracking what it measures. If it cannot live
in the spec, it cannot be pasted forward — it has to be re-solved from the artefact, every
build, by `engine/measure.py`.

A spec names **relationships and bands**, never coordinates:

| Instead of | Write |
|---|---|
| `y=0.7156, scale=0.4419` | `"band": "top"` |
| `annot=("circle", 0.689, 0.085, 0.410)` | `"annotate": [{"mark":"circle","region":"score_ai"}]` |
| `L2_X = {"catch": 0.2973}` | `"gap_after": {"into": "Claude"}` |

Measured house constants (the 34px title word gap, the 430px meme height, the 1015px card
width) live in `house_layout.py` / `engine/layout.py` with their provenance recorded. That
is the *only* place a number is allowed to be typed.

## 2. NEVER ESTIMATE A NUMBER YOU CAN SOLVE — and now, you can't

Every one of these shipped because a value was eyeballed. All are now solved in code:

| Shipped defect | Solved by |
|---|---|
| Title spilled a giant "akes" across the frame | `foundation.py` width gate — **rejects the build before any write**. In berry this rule was a *comment*; there was no PIL import in `base.py` at all. |
| "Claude" and "catch" read as one smashed word | `measure.gap_after_x()` — from the neighbour's measured right edge |
| Two logos at one scale rendered different sizes | `measure.optical_scale()` — per file, from its content box |
| Annotations scribbled over the wrong things | `measure.card_region_target()` — from the card's own region manifest |
| A sticker landed off its target | `measure.place_sticker_on()` — the ink centre, not the canvas centre |

**Cards emit their own region manifest.** We draw them, so every element's rectangle is
known at draw time; `make_cards.py` writes `<card>.regions.json` beside the PNG and an
annotation names a region. Redraw the card and the annotation follows it.

## 3. THE VISUAL GATE — nothing ships unrendered

`python _state/visual_gate.py <draft> --out sheet.png`

Composites V1 + media + **text at real font, size and position** + **annotation stickers
from CapCut's own cache** at 1080x1920, for every moment an asset starts. Fails on text
crossing the frame edge, text overlapping text by more than 12px, and any sticker with no
cached artwork (it cannot be checked, so it cannot ship).

**A clean exit is not permission to skip looking.** Relevance, legibility and whether a
joke lands are not measurable. Open the sheet. Every time. For anything annotated, render
that moment at **full resolution** — composition was once judged from 340px tiles and the
defect was invisible at that size.

Two traps the gate itself fell into: it originally drew bounding boxes and **not glyphs**,
hiding every text defect; and sticker GIFs are **animated with an empty frame 0**, so a
correctly-placed underline looked missing. Both fixed. Both are why section 5 exists.

## 4. NEVER PICK AN ASSET BY ITS FILENAME

`_state/meme_catalog.json` is the allow-list, curated by eye. **`engine/spec.py` now
enforces it** — in berry the catalog existed and *no script read it*, so any filename that
sounded right was accepted. Only `use: "ok"` may be placed; anything in
`banned_burned_text` or `banned_cutout` is rejected by name.

A burned-caption detector was attempted and **did not work** — it ranked a clip with no
text above one with a full caption. A check that lies is worse than no check, so it was
deleted and the bank curated by looking once.

**Owner rules, absolute:**
- ANY visible burned-in text disqualifies a clip — including a meme's own famous caption
- over-add memes, but every one must be a tight match. **"No tight match" is a valid
  answer** — a loose meme is worse than none.

## 5. A CHECK THAT HAS NEVER FAILED IS NOT A CHECK

`verify_build.py` section 8c asserts what the engine fixes:

- **no ghost layers** — every `text_template` `attach_info` matches its segment
- **every style range covers its whole string** — the giant-stray-letter bug
- **every timeline copy identical to the canonical** — all four

Each was verified by **injecting the bug into a throwaway copy of the draft and confirming
the assertion fires.** Passing on a good build proves nothing; two checks in this pipeline
have already shipped reporting clean on the exact defect they existed to catch.

## 6. WRITE EVERY COPY OF THE TIMELINE

There are **four**, not two:

```
template-2.tmp                          <- canonical
draft_content.json                      <- mirror
Timelines/<uuid>/template-2.tmp         <- CapCut reads this
Timelines/<uuid>/draft_content.json
```

`engine/draftio.save()` writes all four, and `enforce_track_order.py` — the **last** write
of a build — now mirrors all four too. In berry it mirrored only `draft_content.json` and
re-syncing was a step in this document that a human had to remember.

## 7. THE ORDER OF A BUILD

1. Fresh clone of `CZ_TEMPLATE` — **never** rebuild on top of a previous build
2. `python _state/build.py <spec>` — validates, then foundation, then overlays
3. `python _state/enforce_track_order.py <draft>` — the last CLI write
4. `python _state/verify_build.py <draft>` — must be zero failures
5. `python _state/visual_gate.py <draft> --out sheet.png` — zero failures **AND look**
6. full-res render of every annotated moment
7. only then, NOTES and handover

CapCut must be **CLOSED** for all of it. The engine checks the process list and refuses.

## 8. WHAT ACTUALLY HELPS FROM THE OWNER

Bucket C — taste — does not shrink from any of the above, and should not be expected to.
What changes is that **C becomes the only thing that needs reviewing.** Two things help:

- **Name a golden reference draft.** One finished reel that is the standard, so density and
  style are diffed against a real artefact instead of a remembered number. (The 242-per-80s
  figure counts SEGMENTS; a spec's beat count is a different unit — comparing them is how a
  build once talked itself into thinking it was four times sparser than it was.)
- **Say when a rule changes.** "No burned text at all" reversed a written learning. A
  reversal is cheap to record and expensive to guess.
