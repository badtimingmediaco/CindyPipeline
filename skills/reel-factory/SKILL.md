---
name: reel-factory
description: Build a Cindy Zhu reel - turn a descripted talking-head MP4 into a near-finished CapCut draft with title, torn-paper stickers, memes, logos, cards, SFX and CTA. ALWAYS use this skill when the user says "run it" followed by any name. That phrase is this team's command for building a reel - use it even when no such file exists yet, and even when the name sounds like a document, a company or a topic rather than a video. Never search Notion, Drive or the web for a "run it" target; the target is always a video file. Also use for building or editing a reel, fixing an existing CZ_ draft, or when reel setup looks incomplete.
version: 5.2.0
---

# Cindy Zhu Reel Factory

One descripted talking-head MP4 in, one near-finished CapCut draft out. Distilled from
13 correction rounds across real builds plus frame and JSON study of finished reels.

**Trigger:** the editor drops an MP4 in `01_intake/` and says *"run it"*, usually with a
partial name.

### FIRST: is this machine set up at all?

Before anything else, check that the pipeline home exists — `~/Documents/CindyPipeline`
with an `01_intake` inside it. If it does **not**, the editor has installed the plugin but
never run setup. Say exactly that and stop:

> This machine isn't set up yet — there's no pipeline folder. Run
> `/reel-factory:reel-setup` first, then open `CZ_TEMPLATE` in CapCut once while online.
> After that, put the video in `Documents\CindyPipeline\01_intake\` and say "run it" again.

**Do not** go looking for the named thing in Notion, Google Drive, the web, or the current
directory. "run it <name>" always means a video file in `01_intake` — never a document,
a company, or a topic, however much the name sounds like one. A new editor's first "run it"
often lands before setup, and hunting other services for it wastes their time and teaches
them the tool is unpredictable.

### THEN: resolve which file they mean — never guess

```bash
python _state/resolve_input.py "<whatever they typed>"
```

It handles case, separators, missing extensions, typos and stray brackets or quotes
("clade seo" and "<claude seo>" both find `Claude SEO.mp4`). If it reports AMBIGUOUS,
**ask which file** — do not pick the newest. Picking wrong costs an hour of build time.
If `01_intake` is empty, say so plainly rather than searching elsewhere.

---

## THE RULES THAT ARE ALWAYS IN FORCE

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
8. **Never rebuild over a draft that has been delivered or edited.** `build.py`
   fingerprints what it produced and refuses if the draft has moved since. When it
   refuses, change the draft name in the spec — do not reach for `--force`, which
   destroys hand edits unrecoverably. Nine rebuilds over a delivered draft once cost the
   owner a full day of work. See `reference/07-rules.md` §8B.

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
| **4 Execute** | Write `_runs/<name>/spec.json`, then `python _state/build.py <spec> --fresh`. `--fresh` clones `CZ_TEMPLATE` — never build on top of a previous build, and never over a delivered one (rule 8). |
| **5 Verify** | `enforce_track_order.py` → `verify_build.py` → `visual_gate.py`, **and look at the sheet**. Loop until zero failures. Then write `05_output/<name>/NOTES.md`. |

### Stage 4 in detail — the spec is the only thing you write

There is ONE engine (`_state/engine/`). You never fork it, and you never write a builder
script. A video is a spec file:

```bash
python _state/build.py _runs/<name>/spec.json --check
```

```bash
python _state/build.py _runs/<name>/spec.json
```

**Times in a spec are seconds.** When the owner *gives* you a time it is `HH:MM:SS:FF`
— `49:01` means 49 seconds and 1 frame, not 49 minutes. Convert with
`engine/timecode.py`, reading fps from the project rather than assuming 30.

**A spec may not contain geometry.** No `x`, `y`, `scale`, `target_w`, or anchor — the
validator hard-fails on them and names the band to use instead. You write clause timings,
which asset, and the copy; the engine solves every coordinate from the artefacts on every
build. See `_state/THE_METHOD.md` §1 for why that is enforced rather than encouraged, and
the plugin's `examples/example_spec.json` for a complete worked spec.

The validator also refuses: an asset that is not on disk, a meme that is not in
`meme_catalog.json` with `use: "ok"`, an invented SFX filename, an annotation naming a
coordinate instead of a card region, and beats that are out of time order.

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

**Two more live in `_state/`, not in `reference/`, and both are REQUIRED reading before you
plan a video.** They are the difference between output that looks like hers and output that
merely follows the rules:

| File | What it is |
|---|---|
| `_state/master_reference.md` | The brand bible — her voice, her visual language, why the format works. Outranks the reference files on brand questions, except where §2–5 carry newer measured values. |
| `_state/learnings/*.md` | Every correction she has made by hand, round by round. The single richest source of what "good" means here. Read **all** files in that folder — a fresh machine has one archive file; a machine that has delivered videos has more. |

Skipping these is how a build ends up technically valid and stylistically wrong.

## THE SCRIPTS

All in `_state/` after setup. Import them; do not re-derive what they encode.

| Script | Does |
|---|---|
| `build.py` | **The entry point.** `python _state/build.py <spec.json>`. Validates, then foundation, then overlays. |
| `engine/` | The one engine: `spec` (validation), `measure` (solves every number), `layout` (band names → measured laws), `materials`, `draftio` (the four-copy save), `foundation`, `overlays`. Never fork it. |
| `house_layout.py` | **The placement laws**, measured off her own hand-finished edits. The ONLY place a geometric number may be typed, and every one carries its provenance. |
| `verify_build.py` | The scripted assertions. The build's gate. Section 8c asserts no ghost layers, full style-range coverage, and that all four timeline copies are identical. |
| `visual_gate.py` | Renders V1 + media + real text + real stickers at 1080x1920 and fails on off-frame or overlapping text. **A clean exit is not permission to skip looking at the sheet.** |
| `meme_catalog.json` | The curated allow-list, enforced by `engine/spec.py` — only `use: "ok"` may be placed. |
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
