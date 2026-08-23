# CapCut technical playbook

> Part of the Cindy Zhu Reel Factory spec (v3.0). Loaded on demand by the
> `reel-factory` skill - see SKILL.md for the routing table.

## 7. CAPCUT TECHNICAL PLAYBOOK (hard-won — do not relearn)
- Never string-edit text `content` fields. Structured JSON round-trips of transforms/
  durations/keyframes are fine (that's what the CLI does internally).
- capcut-cli gaps: `trim` fails on text segments; media `trim` keeps target start (no
  shift after); **the `keyframe` command is BANNED** (it writes
  `property_type:"UNIFORM_SCALE"` without `string_value` — not the validated schema;
  write keyframes by structured JSON in the §7a schema instead); no segment delete
  (structural JSON delete); add-audio needs explicit durations; forward slashes in
  paths; `import-srt --style-ref` copies style but NOT position (always set y after);
  `add-text` cannot set fonts (structured-edit the material afterwards); **ANY CLI
  write may reshuffle the whole track array** (one keyframe call regrouped tracks by
  type and floated the adjust layer to the top).
- **Paper stickers — the two-phase law.** CapCut regenerates text-template wiring on
  every open and DROPS any ids/children you invent. (a) Stamp copies via
  save-template/apply-template — **then IMMEDIATELY rebuild uniqueness: the saved
  template JSON embeds ITS OWN fixed `text_info_resources[0].id` and
  `text_material_id`, and apply-template stamps those same ids into EVERY copy. All
  copies therefore share ONE child — grafting by child id then rewrites the same
  object 17 times and the last text wins everywhere (this shipped: every sticker said
  "Any Website"). Per copy: new res id + new cloned styled child (unique id) + new
  cloned animation/extra materials — assert zero shared ids BEFORE any graft.**
  (b) After the owner's next open+save, graft onto CapCut's own child stubs: copy ALL
  fields from the donor child, KEEP CapCut's ids, set `content.text` + style ranges
  [0,len] + attach_info width ∝ length, **AND fill the template material's
  `origin_word_info`/`current_word_info` text** — that combination is what finally
  survives CapCut sessions. Keep the per-video
  segment→text map so re-grafting is one script run; if texts blank twice in a row
  anyway, stop and hand the owner the numbered type-in checklist (UI text survives).
- **`capcut prune` cannot see `text_material_id` references** — it eats grafted
  template children as orphans. Avoid prune on drafts with text templates; if run,
  verify every template child still resolves.
- CapCut resets `clip.alpha` (delete stale layers, never hide) and may reset
  externally-moved template-media segments; re-verify SFX/text after every session.

### 7a. RENDER-KILLERS (each shipped once — hard bans)
- **Never hand-attach caption-type animation materials** — segments carrying them
  render as NOTHING in export. Pop via scale keyframes; real caption animations are
  UI-only.
- **Keyframe blocks need CapCut's exact schema**: wrapper `id`(UUID), `material_id:""`,
  `property_type:"KFTypeScaleX"` (NOT `property`); each keyframe carries
  `string_value:""` and `graphID:""`. Wrong key = silently dead. A single ScaleX
  block pops UNIFORMLY only because the segment's `uniform_scale.on` is true —
  assert that flag (§7b check 7); if it were false you'd need a twin
  `"KFTypeScaleY"` block or the pop becomes a horizontal stretch. The shipped,
  export-verified block (per segment, in `common_keyframes`; `time_offset` is µs
  from segment start — 0/100000/166666 ≈ a 5-frame pop @30fps):

```json
[{"id":"<UUID>","material_id":"","property_type":"KFTypeScaleX","keyframe_list":[
 {"id":"<UUID>","curveType":"Line","time_offset":0,"left_control":{"x":0.0,"y":0.0},
  "right_control":{"x":0.0,"y":0.0},"values":[0.85],"string_value":"","graphID":""},
 {"id":"<UUID>","curveType":"Line","time_offset":100000,"left_control":{"x":0.0,"y":0.0},
  "right_control":{"x":0.0,"y":0.0},"values":[1.03],"string_value":"","graphID":""},
 {"id":"<UUID>","curveType":"Line","time_offset":166666,"left_control":{"x":0.0,"y":0.0},
  "right_control":{"x":0.0,"y":0.0},"values":[1.0],"string_value":"","graphID":""}]}]
```
- **`add-video` snapshots the file into draft assets** — rebuilding a PNG later does
  NOT update placed segments; `replace-media` every segment that used the old file.
  **It also does NOT overwrite an existing snapshot of the same filename**, so re-running a
  build after regenerating a graphic silently keeps the OLD art (this shipped a stale card).
  Fix: hash every file in `<draft>/assets/video/` against its source and copy over any that
  differ (safe when dimensions match; otherwise `replace-media` and recompute geometry).
  While there, delete snapshots no material references any more — they bloat the draft.
- **Never hand-assemble a segment dict.** Always deepcopy a REAL rendering segment of
  the same class from the draft and mutate it — hand-built "minimal" segments pass
  lint but CapCut renders NOTHING (shipped: logo labels invisible in two builds).
- **Assert `visible: true` on EVERY cloned/placed segment.** The template's sample
  captions carry `visible: false` and clones inherit it silently — this shipped
  twice as "no subtitles" (the segments existed, hidden). A donor's `visible` flag
  is never trusted.
- **Assert every transform is on-canvas (|x|,|y| ≤ 1)** after placement — an
  argument-order slip once parked all logo labels at y=6.1 (six screens up) while
  lint stayed green. Lint does not catch offscreen or invisible segments; only
  these scripted asserts do.

### 7b. FAILPROOF POST-SESSION VERIFICATION (scripted, after EVERY CapCut open AND
every write session — never eyeballed)
1. Paper texts: every template segment's child resolves, parses, and matches the
   text map; **print `text_info_resources[0].id` and `text_material_id` for EVERY
   text_template and assert NO duplicates** (a summary claim is not evidence);
   re-graft/rebuild uniqueness on failure.
2. Track order: V1 idx 0, adjust idx 1 (trimmed to V1's exact length), overlays
   after; all `track_render_index` == array index. **The full track-order re-sort +
   renumber is the LITERAL last WRITE of the session — zero CLI writes after it**
   (any CLI write can reshuffle the array). The only permitted followers are the
   mirror sync (a plain file copy) and read-only `lint`/`diagnose` — exactly the
   Stage 4 tail order.
3. Media resolves: V1 registered in draft_meta_info `draft_materials` and a
   low-scale `capcut render` proxy of a few seconds succeeds (catches black-screen
   media-cache failures the JSON can't show).
4. Don't "fix" frame-snapping: CapCut re-snaps segment starts to frame boundaries
   on open (5.02→5.03) — expected drift, not an error.
5. SFX: every visual start paired within ±0.15s; template-media audio hasn't drifted
   to 0:00; no orphans. Volumes: V1 segment ≈ 2.512 (+8 dB); every success.MP3
   segment ≈ 0.224 (−13 dB).
6. Collision sweep (§2 law): print every pair of visual assets whose time windows
   overlap, with both bounding boxes; assert zero spatial intersections; assert no
   meme/screenshot visible during any logo window.
7. Transforms spot-check: one caption, one sticker, one meme, one logo vs §2. Print
   every styled text material's font resource id and assert only the expected pair —
   Markerist `7525275079106776337`, Awelier `7462241028796337414` (the
   copy-from-template chain must propagate exactly these). Keyframed segments must
   have `uniform_scale.on` true (§7a).
8. Text-width sweep: every text layer passes the §2 no-spill measurement (including
   screen-recording placeholders — verify their strings contain hard line breaks).
8b. Render-truth sweep: EVERY placed segment has `visible: true` AND on-canvas
   transforms (|x|,|y| ≤ 1) — print offenders with ids (lint passes both failure
   modes silently). EVERY logo window contains its name-label text segment —
   print logo windows beside label list and assert none missing.
9. `capcut lint` = 0 errors; `capcut diagnose` → diverged false.
9b. **LOOK AT A COMPOSITED FRAME — mandatory, never skip.** Every check above can
   pass on a draft whose video is visibly wrong: `capcut render` only flattens the
   main video track and mixes audio, it does NOT composite overlays, so JSON
   assertions alone have shipped a reel with memes buried across her face. Run
   `python _state/preview_composite.py <draft> <out.png> <times…>` (places video
   overlays exactly; draws text layers as labelled boxes at their true bounding
   boxes) and actually VIEW the sheet before handoff. Compare it against a finished
   reel in `Cindy Zhu/Final Videos/` — that is the ground truth for how big an
   overlay should be and where it sits.
10. Snapshot the canonical to `_backups/` BEFORE every write pass.

