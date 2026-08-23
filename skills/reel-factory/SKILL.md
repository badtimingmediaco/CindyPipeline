---
name: reel-factory
description: Build a Cindy Zhu reel - turn a descripted talking-head MP4 in 01_intake into a near-finished CapCut draft with title, torn-paper stickers, memes, logos, cards, SFX and CTA. Use when asked to "run it" on a video, build or edit a reel, or fix an existing CZ_ draft.
version: 4.1.0
---

# Cindy Zhu Reel Factory

One descripted talking-head MP4 in, one near-finished CapCut draft out. Distilled from
13 correction rounds across real builds plus frame and JSON study of finished reels.

**Trigger:** the editor drops an MP4 in `01_intake/` and says *"run it"*, usually with a
partial name. Resolve the name — never guess:

```bash
python _state/resolve_input.py "<whatever they typed>"
```

It handles case, separators, missing extensions and typos ("clade seo" finds
`Claude SEO.mp4`). If it reports AMBIGUOUS, **ask which file** — do not pick the newest.
Picking wrong costs an hour of build time.

---

## THE SEVEN RULES THAT ARE ALWAYS IN FORCE

These never leave context. Everything else is loaded on demand.

1. **CapCut must be CLOSED during every external write.** Check the process list before
   every write. CapCut never re-reads from disk while open and its next autosave
   destroys your changes. If the editor says they had it open, run the post-session
   verification before doing anything else.
2. **Never touch her VO, her face, or her colour grade**, and never re-cut the Descript
   edit. The adjust layer grades her footage only.
3. **Build no captions.** The owner runs CapCut auto-captions in the UI herself. Hand
   over the brand-word fix list instead (Claude, CapCut, Descript, this video's tools;
   whisper mishears "Comment" as "Common").
4. **Never invent an SFX filename.** Only files in the locked bank, which must match
   `_state/sfx_map.json` exactly. 23 at last audit.
5. **Write whichever timeline file `capcut diagnose` calls canonical**, then copy it over
   the mirror, and require `diverged: false`. Never assume which one it is — re-check per
   machine and after every CapCut update.
6. **Track-order enforcement is the literal last write.** Nothing after it.
7. **Verification is scripted assertions with printed evidence**, never an LLM
   summarising JSON by eye. A build is not done until `verify_build.py` prints zero
   failures. A reviewer once printed "all ids unique — PASS" while every copy shared one
   child, because it read the wrong field.

**Do not use OpenAI, ChatGPT, Remotion or Hyperframes.** Claude draws every fabricated
asset itself, with Pillow. See `reference/08-cards.md`.

---

## THE PIPELINE

Full detail in `reference/05-pipeline.md`. The shape:

| Stage | What happens |
|---|---|
| **0 Doctor** | `python _state/doctor.py` — resolve paths, verify the kit, confirm CapCut is closed. Any failure → report and STOP. |
| **1 Analyze** | ffprobe, faster-whisper with word timestamps, scene-detect the cuts, and **look at a frame contact sheet** to calibrate the safe zones on this framing. Then write the transcript analysis. |
| **2 Ask** | One batched round of questions, only for what the guardrails do not already decide. |
| **3 Plan** | `03_plans/<name>_plan.md` — title, every sticker, every meme brief, logo moments, SFX schedule, cut-trim table. Everything width-checked and density-checked on paper before touching CapCut. |
| **4 Execute** | Strictly per plan. Clone template → V1 → title → stickers → memes → logos → cards → SFX → volume → CTA → track order → mirror sync. |
| **5 Verify** | Run the checks, fix every finding, re-run. **Loop until zero failures.** Then write `05_output/<name>/NOTES.md`. |

---

## WHERE THE RULES LIVE

Load only what the current stage needs.

| File | Read it when |
|---|---|
| `reference/00-setup.md` | Setting up a machine, or a doctor check failed |
| `reference/01-layout.md` | Placing anything — canvas, layer stack, the three placement grammars, text width calibration |
| `reference/02-sfx.md` | Choosing or scheduling sound effects |
| `reference/03-assets.md` | Choosing memes, or deciding what fills the screen on a beat |
| `reference/04-timing.md` | Syncing to words, or trimming across a cut |
| `reference/05-pipeline.md` | Running any stage — the full stage-by-stage spec |
| `reference/06-capcut.md` | Touching CapCut JSON, or after a render-killer, or verifying |
| `reference/07-rules.md` | The hard NEVER list and the learning loop |
| `reference/08-cards.md` | Drawing any card, graphic or fabricated asset |

## THE SCRIPTS

All in `_state/` after setup. Import them; do not re-derive what they encode.

| Script | Does |
|---|---|
| `house_layout.py` | **The placement laws**, measured off her own hand-finished edits. `meme_geom()`, `card_geom()`, `place_sticker()`, the annotation sticker kit. Never hand-type a scale or transform — call these. |
| `verify_build.py` | The scripted assertions. The build's gate. |
| `tenor_fetch.py` | Meme sourcing from Tenor, no API key, MP4 only — never the .gif. Run `--selftest` first, or whenever a slot comes back empty: it separates "Tenor changed its markup" from "that query has nothing" from "no internet", which look identical from inside a build. |
| `resolve_input.py` | Fuzzy intake filename matching. |
| `doctor.py` | Stage 0. |
| `post_session_fix.py` | Waits for CapCut to exit, then re-grafts and re-checks. Run after every CapCut open. |
| `enforce_track_order.py` | The last write. |
| `preview_composite.py` | Renders the draft to a contact sheet — **for a quick look only**. Judge layout numerically or at full 1080x1920, never from a downscaled tile. |

## AFTER DELIVERY

Ask the editor what they changed by hand, and record it — that is how this gets better.
`/reel-factory:reel-learn` runs the loop; `reference/07-rules.md` covers what belongs in a learning
entry and what does not.
