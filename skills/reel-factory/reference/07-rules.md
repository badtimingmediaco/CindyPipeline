# Never / learning loop

> Part of the Cindy Zhu Reel Factory spec (v3.0). Loaded on demand by the
> `reel-factory` skill - see SKILL.md for the routing table.

## 8. NEVER
UI mouse/keyboard automation on CapCut · touching her VO/face/color · deleting
anything outside the working draft's stale segments · proceeding past failed doctor
or dirty lint · inventing SFX filenames or effect slugs · cloud fetches during
builds · re-cutting the Descript edit · plain-font stickers · circular logos ·
edge-to-edge memes · captions >32 chars · captioned/sticker GIFs · **downloading a
Tenor meme as .gif when an .mp4 exists** · assets without
SFX · overlays surviving a jump cut · anything on screen during the title card ·
writing while CapCut is open.

## 9. LEARNING LOOP
After every delivered video ask the owner what they changed by hand → append to
`_state/learnings/<date>-<topic>.md` → apply next run. If learnings contradict this file 3+
times, propose a spec patch.

---

## 8B. NEVER REBUILD OVER A DELIVERED DRAFT

Every guardrail in this pipeline used to protect the **write** ("is CapCut closed?") and
none protected the **target** ("has this draft moved since I made it?"). On 2026-08-26
that cost the owner a full day of hand edits: nine rebuilds of an already-delivered draft,
each starting from a fresh template clone. Nothing was recoverable - not the backups
(every one was taken after a clone), not the CLI history, not shadow copies.

**Closed is not the same as untouched, and a delivered draft is not scratch space.**

`build.py` now refuses. It fingerprints what it produced (`engine/draftio.record_build`,
stamped by `enforce_track_order.py`, which is the last write of a build) and compares
before it touches anything:

- fingerprint matches -> build proceeds
- draft does not exist -> build proceeds
- **fingerprint differs, or there is no record at all -> REFUSE**

When it refuses, the fix is a **new draft name in the spec**, not `--force`. `--force`
exists so the owner can override; it destroys the edits and they do not come back. Do not
reach for it to get past a refusal on your own judgement, and never as a habit.

If the owner has hand-finished a draft and wants a change, put the change **in the spec**
and build to a new name, then tell them what to carry over. Mechanical corrections -
timings, label text, SFX choices, meme swaps - belong in the spec anyway; that is where
they survive the next rebuild.
