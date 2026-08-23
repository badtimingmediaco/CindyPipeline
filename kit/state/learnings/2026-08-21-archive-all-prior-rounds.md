# Style learnings (append after every delivered video)

## 2026-07-08 - ScrollAnimations owner review: visual QA failed despite green JSON checks
- **Title collision is a hard fail.** The opening title can pass lint while visually reading as one smashed row ("make/Claude/build" overlapped). Future title verification must measure/render row spacing and treat visual overlap as a blocker. Do not rely on x positions by eye; use conservative spacing and smaller scales for multi-word line 2.
- **"Centered" must mean visually centered on the canvas, not just transform x=0.** Several text layers appeared shifted left/right because the template/paper asset's internal anchor and width were not accounted for. For paper stickers, CTA cards, placeholders, and title rows, add a visual-centering check or use calibrated offsets from rendered bbox/template width.
- **Screen-rec placeholders must not sit on Cindy's face.** Placeholder instruction text placed at center y=+0.10 covered her eyes/mouth. For placeholder cards, either build a real card/screenshot asset, or keep the placeholder in a safe band and much smaller; never cover her face or mic with plain white instruction text.
- **Meme fit check must reject side bars.** Patrick workbench shipped with black vertical bars on both sides; that should have failed the meme frame check. Reject or crop/pad any meme with visible pillarbox/letterbox bars unless the bars are intentionally part of the meme and not ugly at placement size.
- **Meme relevance check must be stricter.** Patrick workbench did not fit this reel well enough. Prefer literal/clean UI/product/scroll/typing/Apple/product-page jokes here; remove weak-fit memes even if they are recognizable.
- **CTA line break rule:** CTA paper card should hard-wrap after `Comment`; put the keyword on line 2, e.g. `Comment\n"PROMPT"` or `Comment\nPROMPT`, so it does not become one long off-center strip.
- **Automation density was too low.** A build with only a handful of memes/placeholders wastes the automation run. For this style of how-to reel, add many more automated assets: step labels, prompt/result cards, UI-proof placeholders, micro callouts, and meme/label pairs so the editor is subtracting, not building from scratch.
- **Verification gap:** green `capcut lint`, `diagnose`, and id/volume checks are not enough. Add screenshot/render-based QA for title readability, text centering, meme fit/crop, placeholder face coverage, CTA wrapping, and asset density before handoff.

## 2026-07-06 — HANDOFF KIT v2: dual-spec team handoff (owner-ordered)
- Kit rebuilt for team transfer with the TWO-SPEC choice: `CINDY_REEL_FACTORY.md` (Option 1 — no OpenAI key, no posters, $0 API) vs `ChatGPT_Claude_Reel_Factory.md` (Option 2 — full poster module, gpt-image-2, inspo approval gate). Both ship at kit root + kit _state; whichever is renamed CLAUDE.md is active. HANDOFF_GUIDE §A/§B7 updated with the choice + per-OS key setup (Windows setx / macOS ~/.zshrc export + new-terminal caveat).
- Kit now carries the FULL poster ecosystem: references (10 approved + PROMPTS.md style brief + worked examples), inspo/_approved_example (the owner-approved dark set — shows the taste bar), bank (2 reusable generated posters), plus card_templates (prompt/plan/RPM card HTML sources), 5 paper-text maps, 20-meme bank, 11 logos.
- START_HERE.pdf v2 (4 pages): p1 = the two-spec decision cards + what's-in-the-box; p2-3 = 7 setup steps with Windows/macOS split panels per step (installs, fonts, drafts paths, key setup) + the run loop incl. the poster approval gate; p4 = NEVER/ALWAYS two-column card ("never run with CapCut open", "never rename SFX", "trim memes freely", "reply to the inspo sheet with numbers"...) + quick-fixes table. Regenerate from _state/start_here_guide_source.html.
- Kit verification: 15 scripted checks (spec hashes ×3 each, HANDOFF ×4, poster ecosystem, _state completeness, banks/fonts/sfx counts, template+refs, PDF, zero identity + zero API key). 568 files, 87.7 MB.

## 2026-07-03 — Bedtime Stories v1 feedback (owner, with reference screenshots + 2 finished drafts)
- Captions: System-family font size 10, scale 1.0, position (0, −0.56). import-srt puts them at y=0 (her face) — always fix.
- Stickers: torn-paper text templates at 33–41% scale, or plain text size 15 at ~50% scale. Zones: above head (+0.35…+0.64) or below face (−0.37…−0.45), side pairs x ±0.44–0.51. NEVER mid-frame over her chest. Word-timed holds, 0.4s pops are normal.
- Title: per-WORD segments. Lead-ins scale ~1.37 size 12 #faf7f2; keyword MADE-Awelier-Black size 13 **#e8856a** scale ~1.46; all at y ≈ +0.69. Boxed line = text template 41%.
- Coral is #e8856a, not #E8663D.
- First SFX at 0:00 is ALWAYS magic reveal.MP3 (his rule #4, and it's what Catch Mistakes does).
- SFX density: ~57 hits / 83s in Catch Mistakes. Overlaps and sub-second gaps everywhere. The 1.5s-gap rule from the old docs does not survive contact with her real edits.
- Memes: fullscreen (or 0.83–0.93) flash cuts, 0.4–2.5s, 15–40 per video. "Use as much as the video actually requires. More is not a problem, less is." Tenor downloads explicitly allowed (his call, 2026-07-03).
- CapCut 8.7: canonical timeline = template-2.tmp; draft_content.json is a mirror. External patches must hit both or they get clobbered.

## 2026-07-03 pm — Bedtime Stories v2 feedback (owner)
- Stickers must be the paper-cutout template ONLY — he plants a sample layer ("5 Sub Agents") to clone from; plain Awelier text stickers are not a thing in her videos. Clone via save-template/apply-template + per-copy child text material in template-2.tmp.
- Title rows were overlapping and the long main line spilled the frame: one element per row, scale main line to fit (20 chars ≈ scale 0.7), everything x=0.
- Memes: NO baked-in captions, NO transparent sticker-GIFs, margins on every meme (scale ≤0.85 centered), frame-check every file before use (8 of my 12 first picks failed the caption check).
- capcut trim on video segments keeps target start — don't shift afterwards (made this mistake twice now).

## 2026-07-03 late — Bedtime Stories v3 feedback (owner)
- CapCut DEDUPES text-template copies on open if text_info_resources ids are shared — all 16 stickers collapsed to one phrase. Fix: unique resource id + unique child material per copy (child keeps the shared resource *name*).
- CapCut also resets clip.alpha on open — opacity-hides don't survive. DELETE stale segments structurally + capcut prune.
- Adjust layer goes directly above V1 (grades only her footage) and is trimmed to exactly the video length.
- Title main line is a paper-cutout copy too (black Markerist on paper); CTA reuses HIS planted comment-card layer (retime + retext), never a home-made one.
- Density: no ~4-5s stretch without a new asset (sticker/meme/SFX).

## 2026-07-03 night — Bedtime Stories v4 feedback (owner)
- Pre-building text-template wiring in JSON does NOT survive CapCut: it regenerates template materials + bare child stubs and drops the text. Two-phase fix: stamp copies -> the owner opens/saves once (CapCut wires it) -> graft donor-styled content onto CapCut's own child stubs, keeping CapCut's ids, changing only content.text + ranges.
- Keep a donor child JSON (fully styled paper text material) saved BEFORE deleting the sample layer.
- Adjustment layer: the owner locked it at layer 2 (above V1). Never touch it via automation; CapCut re-floats adjust tracks on open anyway. New drafts: verify + flag, don't patch.

## 2026-07-03 round 5 — Bedtime Stories export review (owner)
- Assets must be word-exact (words.json start of the literalized word) and TRIMMED at the base video's invisible Descript cuts (ffmpeg scene detect >=0.08; cuts align with sentence ends).
- No stickers/memes during the title card; deleted the redundant "bedtime story apps" sticker that collided with the title rows.
- Mandatory scripted SFX-pairing audit before handoff (every visual start ±0.15s); orphaned SFX deleted; SFX move together with retimed assets.
- CapCut reset the template's own retimed magic-reveal segment back to 0:00 — recheck SFX after every CapCut session.

## 2026-07-04 round 6 — reference-study + captions/logos (owner)
- Caption animation = CapCut "Isolated Popout" (caption-type sticker_animation, resource_id 7582432032513412353), one material per cue, duration = cue duration. Cues must be <=32 chars or they overflow; re-split and re-import rather than patching long cues.
- App-logo grammar: rounded-square app icons scale 0.28; dual = x +/-0.26 y +0.24 + white "+" between + script labels below (y +0.115); single = centered (0,+0.22). Fires at first mention of a tool; replaces any sticker naming the same tools. Build icons with Pillow (rounded mask) if no official app icon on hand.
- CORRECTED meme placement from the 4-reel study: memes are mid-size PIPs ~0.55-0.75 scale in the UPPER half (y +0.10..0.25) over/above her face - NOT fullscreen. Screenshots 0.6-0.9 cards; phone screenshots ~0.55. Sticker above + meme below = label+illustration pairing.
- Other asset classes seen: editorial posters (Auditor/Surgeon/Orchestrator, ~0.5-0.6 centered), pixel-mascot swarms during hooks, notes-app summary overlay at CTA, number flipboard cards, washi-tape note cards.
- CLAUDE_v2.0.md written as the portable team spec (placeholders, no personal paths).

## 2026-07-04 round 7 — export review (owner)
- UNITS: clip.transform = fraction of HALF the canvas (+/-1 = edge). Deriving coords from full-frame measurements halves everything and parks assets on her face (shipped once with logos).
- Logos: never circular — square with ~18-22% corner rounding. Dual (x +/-0.48, y +0.48) scale 0.28, '+' (0,+0.47), labels (+/-0.48,+0.23) scale 0.9 NO intro animation; single (0,+0.44). A literal-subject meme is not a substitute for the tool's logo.
- Only the first title text layer keeps an intro animation; apply-template copies animations - strip them from all other stamped text.
- Memes must be RECOGNIZABLE pop-culture reactions (SpongeBob/Pixar/famous shows); famous-and-close beats obscure-and-literal. SFX must match the on-screen action (pencil-writing gif got keyboard-typing SFX - flagged).
- Adjust layer: CapCut floats its track above overlays in the FILE even when the UI says layer 2 -> it grades all memes/logos. Post-session: enforce array order V1, adjust, overlays + renumber track_render_index.
- Template texts attempt #4: graft + fill template origin/current_word_info. If blanked again on next open -> hand-type checklist fallback (UI text survives).

## 2026-07-04 round 8 — export (4) review (owner)
- WIN: word_info graft survived a full CapCut open+export - paper texts finally persist.
- Hand-attached caption-type animation materials make caption segments render as NOTHING in export. Removed; pop now via scale keyframes (0.85->1.03->1.0, ~5 frames) in CapCut's exact keyframe schema (property_type key, string_value/graphID fields).
- add-video snapshots the media file into draft assets: rebuilding a PNG later requires replace-media on every segment using it (circular fish icon shipped because of this).
- No "+" between dual logos (owner call); logo labels scale 1.0.

## 2026-07-04 — ATS build (agent, caught by owner)
- capcut-cli `apply-template` text override does NOT reach the text-template child: every
  stamped copy kept pointing at the ONE shared donor child ("5 Sub Agents") with a shared
  text_info_resources id — the exact round-3 dedupe trap, reintroduced by trusting the CLI.
  Fix pattern (now scripted): immediately after stamping, clone the styled child per copy
  (unique material id + unique resource id, keep resource name), set content.text + ranges
  [0,len] + attach_info width ∝ length + origin/current_word_info. VERIFY texts right after
  stamping — never assume the override landed.

## 2026-07-04 — WebsiteRebuild first-open review (owner) — 5 issues, all fixed
- **apply-template stamps the template JSON's OWN res/child ids into every copy** — all 16 stickers +
  L3 shared ONE child; grafts by child-id all rewrote the same object (last text won → every paper
  layer showed "Any Website"). Fix: unique res id + unique cloned child + cloned extra refs PER COPY,
  immediately after stamping, before grafting. §7b must assert res/child id uniqueness with printed ids.
- Verification subagents must print evidence, not claims: the Stage-5 reviewer passed the id-uniqueness
  check that was actually failing, and false-failed 3 checks by reading wrong fields. Scripted asserts > LLM reads.
- Title materials are font size 15 (not 12); the 4.7px/char width model under-measures ~25%+. Measure
  with PIL against the material's own cached font.ttf, calibrated to a known-good template row.
- Logo labels ship in Markerist size 12 white (the "script font" idea is dead — ATS's accepted build
  used Markerist). add-text can't set fonts → structured edit of style font id/path afterward.
- Adjust layer: owner wants it trimmed to exactly V1 length every build (overrides v3.0 "never retime").
- V1 black screen with draft JSON provably identical to a working build = CapCut-side media cache
  issue. Cover: relink to a fresh path + register in draft_meta_info draft_materials; fallback manual
  re-import. Consider capcut render proxy smoke test in doctor/verify.

## 2026-07-04 — WebsiteRebuild build (agent, pre-delivery technical notes)
- capcut-cli `keyframe` writes property_type "UNIFORM_SCALE" without string_value — NOT the round-8
  validated schema (KFTypeScaleX + string_value/graphID). Write pop keyframes via script, never the CLI.
- ANY capcut-cli write can reshuffle the track array mid-session (a single keyframe call regrouped
  tracks by type and floated adjust to the top). Track-order enforcement must be the literal LAST write.
- apply-template (current CLI) DOES generate unique child ids + text_info_resources per stamp and DOES
  carry the donor's segment clip scale — but the text override still doesn't land (all stamps read the
  donor text). Graft pass still required; unique-id cloning no longer is.
- Dual logos/labels need SEPARATE tracks (same-track segments can't overlap in time) — logos2/logolabels2.
- Tenor v1 API with the public demo key still works for meme search/download (media[0].mp4).
- Antigravity's real app icon extractable from %LOCALAPPDATA%\Programs\Antigravity IDE\resources\app\
  resources\win32\ (VS Code-fork layout); VS Code's true icon from code.ico in the hashed install dir
  (the OSS GitHub repo ships an unbranded stub — wrong art).

## 2026-07-04 — meme popularity rule (owner, spec addition)
- Meme selection must PRIORITISE widely-recognized memes (famous TV-show/cartoon/film moments —
  SpongeBob, The Office, Simpsons, Pixar — + well-known internet memes) over generic/random ones.
  Two candidates fit the subtext equally → the more famous one always wins; famous-and-close beats
  niche-but-literal; an unrecognizable meme reads as random B-roll and is rejected. Added to spec as
  §4.0 POPULARITY LAW (CINDY_REEL_FACTORY.md + CLAUDE.md) and folded into §4.4 scoring + master_reference
  visual identity.

## 2026-07-04 round 9 — spec-only feedback (owner)
- Meme choice quality: keyword-first searching banned. New §4 flow: transcript analysis -> MEME BRIEF (line/surface/SUBTEXT/joke) -> cast 2-3 named famous scenes from memory -> search by SCENE NAME -> audition >=3 candidates w/ frame checks -> bank-first reuse. Empty slot beats off-brand meme.
- Text wrapping: CapCut text segments never auto-wrap; screen-rec placeholder instructions must be hard-wrapped (
 every <=28 chars, max 4 lines); no-spill width formula now checked at plan time AND post-session (width sweep in 7b).
- Title pattern locked: L1 white Markerist + drop shadow lead-in; L2 must contain "Claude" in orange Awelier (+ white Markerist words as separate segments); L3 = the video's main keyword (1-3 words) in Awelier on the torn-paper layer. Title research/drafting moved into the planning stage.

## 2026-07-04 round 10 — WebsiteRebuild incident report folded into spec (v3.0)
- apply-template stamps the template JSON's OWN res/child ids into every copy -> all stickers shared one child, last graft won ("Any Website" everywhere). Law: rebuild uniqueness (new res id + cloned child + cloned extra materials) immediately after stamping, assert zero shared ids BEFORE grafting.
- Verification must be scripted assertions with printed evidence — an LLM reviewer false-PASSed the exact critical check (read the wrong field) and false-FAILed three others.
- Width model replaced: measure with PIL against the material's real font.ttf (path in content.styles[0].font.path), calibrated on a known-good template row; title materials are size 15. The 4.7px/char heuristic under-measured ~25% and shipped an overlapping off-frame title.
- Logo labels are Markerist size 12 white #faf7f2 (not "script font"); add-text can't set fonts -> structured-edit the material after. Dual icons + labels each need separate tracks.
- Adjust layer: DO trim to V1's exact length each build; never touch its grading params; enforce index 1.
- V1 black screen: JSON was provably correct — CapCut media-cache issue. Mitigations now in spec: register V1 in draft_meta_info draft_materials + low-scale render smoke test; fallbacks relink -> UI re-import -> lossless rewrap (never re-encode).
- capcut-cli keyframe command BANNED (wrong schema: UNIFORM_SCALE, no string_value). Any CLI write can reshuffle the track array -> track re-sort + renumber must be the literal last write.
- Tenor v1 API (public key LIVDSRZULELA) works headless for meme search/download. Real app icons from installed app resources; repo stub icons banned. CapCut frame-snaps segment starts on open — not a bug, don't fix.

## 2026-07-04 round 11 — WebsiteRebuild export screenshots (owner)
- Logo rendered ON TOP of a meme (which itself had a baked 'Claude Code' caption). Spec now has a GLOBAL COLLISION LAW: bounding boxes computed at plan time, no two visual assets may overlap in space+time; logos are exclusive occupants (no meme/screenshot visible during a logo); tool-naming beats get the logo, meme auto-rejected at brief stage; frame-check verdicts must be WRITTEN into the plan per candidate.
- Title line 3 paper box touched line 2 descenders -> rows must stack with >=0.02 half-units clearance, measured via PIL.
- Audio: V1 descripted video +8 dB (linear 2.512, JSON only - CLI caps at 1.0); every success.MP3 segment -13 dB (linear 0.224). Both added to Stage 4 volume pass + 7b checks.

## 2026-07-04 round 12 — title grammar (owner)
- Shipped title read "how to recreate with Claude any website" - broken grammar from filling pattern slots mechanically. GRAMMAR LAW added: write the title as one natural sentence first, split it into the 3 lines so the top-to-bottom concatenation reads back exactly; read-aloud test recorded in the plan; rephrase the sentence (never force words) when the pattern slots fight the grammar.

## 2026-07-04 round 13 — full spec audit (subagent review, owner-ordered)
- 19 findings, all fixed. Highest: the machine's live CLAUDE.md was still v1.0 ("Marketist" misspelling, hook cards, approval stops, real names) — replaced with the v3.0 spec content; CLAUDE_v1.x/v2.0 archived to _backups/spec_archive/ so no stale spec loads as context.
- Facts corrected: SFX bank is 23 files, not 22 (authoritative count = sfx_map.json, both docs now defer to it); sfx_map.json schema + duration-tagging heuristic restored (dropped in the v3 rewrite); "12 correction rounds" not 8; HANDOFF taught two nonexistent commands (`capcut projects`, `capcut relink`) and pointed the meme bank at 04_assets/memes/ instead of .../memes/bank/.
- Keyframe truth pinned from the shipped Bedtime draft: KFTypeScaleX ALONE pops uniformly because segment uniform_scale.on=true (all 76 caption segments verified) — spec now embeds the real JSON block and asserts the flag; a ScaleY twin is only needed if uniform_scale is ever false. (Auditor suggested "always add ScaleY"; the draft evidence says otherwise — flag-dependent.)
- "Literal last write" clarified: zero CLI WRITES after the track re-sort; the mirror sync is a plain file copy and lint/diagnose are read-only — Stage 4's tail order is the sanctioned sequence. §7b renumbered 1–10 (markdown-safe) with new asserts: font resource ids (Markerist 7525275079106776337 / Awelier 7462241028796337414) and uniform_scale on keyframed segments.
- Kit hygiene: this file sanitized to "the owner"; HANDOFF gained a pre-zip sanitize step (exclude 05_output/ and NOTES_FOR_*.md, grep for names). Width heuristic reframed as a lower bound (×1.3, only PIL approves). Tenor download field documented (results[].media[0].gif.url / .mp4.url). post_session_fix.py documented as two halves (exit-watcher + §7b checks) so a regeneration doesn't lose the watcher.

## 2026-07-04 — handoff kit built (owner-ordered)
- Full kit assembled at Desktop "Cindy Reel Factory - Handoff Kit" (522 files, ~49 MB, 16 scripted checks pass): START_HERE.md setup guide + spec + HANDOFF + CindyPipeline (sanitized _state, logos, meme bank, folder purpose-cards) + 23-file SFX bank + CZ_TEMPLATE (103 files) + 2 reference drafts (Claude Cleaner(1), Sub Agents(1); Catch Mistakes omitted at 131 MB — send on request) + Poppins fonts.
- master_reference.md sanitized at source (names → "the owner", machine paths → %LOCALAPPDATA%/<Desktop> placeholders, bank 22→23, "all bank SFX") + a PRECEDENCE banner: spec §2–5 outrank it on technique; it rules brand voice only (its old SFX rules — "never <1.5s apart", "magic reveal for payoffs" — are dead).
- post_session_fix.py now portable + arg-driven: `python post_session_fix.py <draft-folder> <video-name>`; STATE/_backups resolve relative to the script; falls back to draft_content.json as canonical when template-2.tmp is absent (old CapCut). The old edit-the-constants usage is gone — a config guard exits with instructions.
- Fonts law for kits: Poppins ships (SIL OFL); MADE Awelier ALSO ships — owner's explicit call after being flagged on the PERSONAL-USE license ("dont worry about the license", 2026-07-04); FONTS_README keeps a soft "keep it inside the team" line. Markerist never installs (CapCut cache via opening CZ_TEMPLATE online). Donor JSONs/draft folders ship as-is — internal source-machine cache paths are expected and harmless (HANDOFF §A6 exception; CapCut re-resolves by resource id).
- Setup guide format: the owner rejected the markdown START_HERE ("isnt good looking and too complicated") → replaced with **START_HERE.pdf**, a 3-page designed PDF (Poppins, coral #e8856a, step cards + rules/fixes tables) rendered via headless Chrome (`--headless=new --user-data-dir=<temp> --no-pdf-header-footer --print-to-pdf`) from HTML; verified via pypdf (3 pages, page-bottom elements painted = no clipping, zero identity strings). Keep future guides SHORT and visual; regenerate from HTML, never hand-edit the PDF.

## 2026-07-04 — kit made fully cross-platform (owner-ordered, macOS support)
- capcut-cli VERIFIED macOS-compatible (npm readme: "macOS · Windows · Linux — pure Node ≥18, no native modules"; full test suite runs on macOS CI; Mac drafts dir `~/Movies/CapCut/User Data/Projects/com.lveditor.draft/`). CapCut Mac uses the same draft JSON format; the spec's diagnose-based canonical detection already covers it.
- post_session_fix.py process check is now OS-branched: Windows → `tasklist` substring (image names only, no self-match); macOS/Linux → `pgrep -ix CapCut` (NEVER `pgrep -f` — it self-matches the script's own command line because the draft-path argument contains "CapCut"); FileNotFoundError → warn and continue. PowerShell dependency removed.
- Both-OS wording added everywhere one OS was assumed: HANDOFF B4 (Mac drafts path) + C5 (arg-form script call), master_reference ×2 path spots, FONTS_README (right-click vs Font Book), guide PDF step 1 (brew), step 2 (install idioms), step 3 (both paths + "Mac first open may ask to relink template media — point at the draft's own folder"). Spec §5 cd-first note reworded OS-neutral.
- Verification lesson (2nd occurrence): substring asserts on extracted PDF text fail on letter-spacing (kicker) AND line wraps (checkline pill) — match with whitespace-tolerant regex or check the painted context, don't re-render on a false miss.

## 2026-07-04 — ChatGPT/OpenAI poster module → ChatGPT_Claude_Reel_Factory.md v3.1 (owner-ordered)
- New variant spec on Desktop: **ChatGPT_Claude_Reel_Factory.md = v3.0 (incl. §4.0 popularity law) + §4B poster generation + §4.0b HUMOR LAW + §7b check 11**. Original CINDY_REEL_FACTORY.md and the handoff kit are NOT upgraded — promote v3.1 into CLAUDE.md/kit only when the owner confirms.
- §4B core laws: fires ONLY on enumerated-items videos ("5 formations", "7 codes"); ONE poster per item, NEVER a combined poster; ONE billed API call per item, bank-first reuse (04_assets/posters/bank/), retries need a written plan reason; key ONLY via `OPENAI_API_KEY` env var — never in files/kit; Stage 0 reports it, Stage 3 hard-stops without it.
- gpt-image-1 CANNOT output 4:5 (1122×1402): generate `1024x1536` + a crop-safe bleed line in every prompt ("keep everything inside the central 1024×1280; top/bottom 128px are bleed"), then Pillow CENTER-CROP to 1024×1280 (crop only — squashing warps typography). References ride along via `client.images.edit(image=[refs...])` — same set every call for campaign cohesion.
- References seeded: 4 ATS posters (Auditor/Scout/Strategist/Surgeon, verified 1122×1402) in 04_assets/posters/references/; owner still needs to drop in the 5 formation posters from the ChatGPT chat (agent cannot save chat attachments to disk). PROMPTS.md there = style brief + crop line + 5 worked examples.
- Placement: meme mechanics + poster specifics (0.65–0.8 centered 0…+0.2, starts at the item's word start, 1.5–3s, never two at once, reveal SFX, poster outranks meme on item-name beats like logos).
- The permission classifier BLOCKED the agent from persisting the API key to the user env (credential-write needs owner review) — the owner sets it himself: `setx OPENAI_API_KEY <key>` once per machine. Key was pasted in chat → owner advised to rotate.
- Sync lesson: the §4.0 popularity-law round updated Desktop spec + CLAUDE.md but NOT the kit copies (caught by a stale-hash check this round). EVERY spec edit must end with the ×5 sync: Desktop spec → CLAUDE.md → pipeline _state → kit root → kit _state. (v3.1 ChatGPT_Claude_Reel_Factory.md is the exception — Desktop-only until promoted, so it does NOT get the ×5 sync yet.)

## 2026-07-04 — poster refinement: Pinterest = downloaded images, not words (owner)
- Owner: do NOT produce written art-direction takeaways from Pinterest — DOWNLOAD the inspiration images and hand them to ChatGPT as an actual visual guide. §4B reworked: search Pinterest/web images ("movie posters", "cool poster designs", "web series posters"), download 3–6 frame-checked results to `04_assets/posters/inspo/<video>/`, and attach them to `images.edit(image=[approved_refs + inspo_imgs])` — approved posters = primary/campaign cohesion, inspo = secondary art-direction energy, same set reused for all posters in a video. Pinterest pins expose direct `i.pinimg.com/originals/...` jpgs for plain HTTP GET (no scraping needed). Cost note added: every attached image is billed as input tokens, so keep references/ tight (~6–10) and inspo ≤6. New NEVER: "describing poster inspiration in words instead of attaching the actual downloaded images."
- All 10 approved references now live: 4 ATS role posters + 6 formation posters (Fan-In, Orchestrator, Council, Consensus, Debate + 1 variant), all 1122×1402. inspo/ folder created with a purpose card. Owner set OPENAI_API_KEY via setx himself (164 chars, user scope) — poster module now fully operational.

## 2026-07-05 — GoHighLevel build (first full run of ChatGPT_Claude_Reel_Factory v3.1)
- **Title grafting from a reference draft WORKS and is the reliable way to hit exact owner styling.** Owner had a parallel manual build "GoHigh Emergent" (same 42s 4K gohighlevel.mp4) and gave a screenshot + told me to match its title positioning/sizing. Grafting the 4 title layers (segment + all extra_material_refs: text/text_template + material_animations + effect + template child) verbatim with a consistent id-remap (fresh UUIDs for every id: segment, material, text_template resource id + text_material_id child) → zero collisions, fonts/colors/transforms identical, lint 0, diverged False. Owner approved on first try.
- Exact GoHighLevel title (owner-specified, overrides my grammar-law draft): L1 "Build your own" Markerist white #faf7f2 (y+0.701 sc1.105) / L2 "GoHighLevel" Awelier TORN-PAPER (effect 7602106273437371701, child size 19, y+0.578 sc0.373) / L3 "using" Markerist white (x−0.345 y+0.453 sc1.126) + "Claude" Awelier orange #e8856a (x+0.197 y+0.459 sc1.262). Reads "Build your own GoHighLevel using Claude". NOTE the keyword (GoHighLevel) is on L2 torn-paper here, Claude on L3 — a valid variant of the §2 pattern.
- **CZ_TEMPLATE clone carries a WHOLE prior sample build** (a sub-agents video: sample title "How to turn Claude into / 5 Sub Agents", sample captions "if you've been wondering how people spin up sub agents…", sample sticker "Make money while you sleep", CTA "Comment Agents"). These are intentional STYLE DONORS (spec §0.3) but they OVERLAP a freshly-grafted title → must strip the sample title pieces (structural delete by seg id) so only the new title shows. Donors persist in _state so deletion from the clone is safe. Keep the CTA card (retext later).
- gpt-image poster module: GoHighLevel is NOT an N-items video (its 5 features — CRM/pipeline/booking/lead form/dashboard — are named in a 3.6s aside, can't carry 1.5–3s posters). Correctly SKIPPED posters (Stage-2 asked; owner confirmed skip). The §4B trigger judgment held up on first real use.
- Stage-2 questions that mattered on a real video: poster skip (cost+fit), CTA word from a garbled transcript ("Come and own on our DMU" → Comment "OWN" + I'll DM you), screen-rec placeholders (owner: "do both" = placeholders at build beats + overlays elsewhere), GHL logo at hook. All 4 were genuine, none guardrail-decidable.
- Logo sourcing: Emergent's real icon lives on their webflow CDN (found via grepping the app SPA HTML for <link rel=icon/apple-touch>). GoHighLevel exposes only a 16–32px favicon → built a Pillow "High Level" wordmark tile as the §2 fallback and flagged it for the owner to swap real art. Google favicon service (s2/favicons?sz=256) only returns what the site provides (GHL=32px).
- add-video put V1 on a NEW track and floated an empty video track to idx0 → CLI reshuffle, fixed by the literal-last-write track enforce. Black-screen risk auto-retired when a reference draft already renders the same 4K file.

## 2026-07-05 — GoHighLevel density feedback (owner) — THE BIG LESSON
- **Owner rejected the first assembly as too sparse: "very less assets… that kills the purpose… I want automation to do 80% of the work, you did 30%."** First pass shipped only 1 meme + 4 stickers + 3 logos for 42s. That reads as ~30% done. → Added a **DENSITY MANDATE** to §4.6 of BOTH specs (base + v3.1): target the HIGH end (~25–40 overlays + ~45–60 SFX per 80s), assign an asset to EVERY beat at plan time, flag+fill any >2.5–3s gap, emptiness is the exception not the default. Under-filling is now a named shipped defect.
- Second pass brought it to **6 memes + 9 stickers + 3 logos + 32 captions + 27 SFX** for 42s (~18 overlays + full captions) — that's the density bar. Lesson: DON'T stop at "within range"; a 42s reel needs ~15–20 overlays, not 5. Walk the transcript clause-by-clause and place a sticker on every punchy phrase + a meme on every emotional turn.
- **CTA timing bug:** placed the "Comment OWN" card at 38.4s but she says "Comment" at 39.66s → card appeared ~1.3s early. Assets fire at the START of the exact spoken word — the CTA card is no exception. Fixed to 39.66s. (I'd copied the reference's 38.4 start without re-anchoring to her actual word.)
- Meme sourcing at volume works: Tenor batch download (8 candidates) → ONE contact sheet → ONE image read → pick winners. Round-2 winners: This-is-fine dog (waste/denial), Patrick building (build), confused math lady (which feature), sweating Jordan Peele (overwhelm at options), DiCaprio cheers (ownership win), SpongeBob control panel (guessing). All famous, clean, matched to the exact sentence. Short Tenor clips (~1s) → cap requested duration to source length (add-video errors if longer).
- Density pass structure that worked: position new memes + graft N stickers (torn-paper, unique ids) + add paired SFX + fix CTA, all in one structured-JSON write, THEN re-run the literal-last-write track-order enforce (add-video reshuffled again). Recheck printed asset COUNTS, not just pass/fail — counts are what catch sparseness.

## 2026-07-05 — frame-study of 5 finished reels (owner: "why don't you understand what memes to add")
- **THE CORRECTION to the density pass: fill with SUBSTANCE, not memes.** Studied 5 finished reels frame-by-frame + transcripts (Reve poster tool, 5 secret Claude codes, resume unrejectable, creative-studio 7 skills, Higgsfield-MCP setup). In EVERY reel memes are only **2–3 per 60s** (up to ~5 for a playful "7 skills" topic) — the SPICE. The screen is ~80% filled with PROOF: screen recordings w/ red arrow/cursor annotations (the #1 overlay for how-to/setup), generated outputs & result screenshots, numbered-section posters (THE REWRITER / THE HIRING MANAGER / CLAUDE ARTIFACTS), prompt/formula cards (the actual prompt on paper; "accomplished X, as measured by Y…"; Claude's blunt replies as black message cards), infographics (ATS hexagon, OODA loop), logo cards. Added §4C ASSET MIX to both specs + tied §4.6 density to it (density ≠ memes).
- **Stickers are LABELS, not echoed spoken words** — they NAME the on-screen visual or mark the step: numbered ("2 Competitor ads-extractor", "1. Diagnose"), content ("Art direction", "Reference", "Result", "Directing"), STEP ("Go to Claude", "Then Connectors", "Add Custom Connectors"), status ("LIVE", "4k", "No Editing needed!"). My GoHighLevel stickers ("own it", "half used") echoed words — should have been step/section labels.
- **Mix is chosen by VIDEO TYPE.** Setup/how-to ("connect X to Claude & build" = GoHighLevel + Higgsfield-MCP) → 70–90% SCREEN-REC placeholders + STEP-LABEL stickers, only 1–2 memes. Higgsfield-MCP (the twin of GoHighLevel) used ~1 meme, ~90% cursor-annotated screen-recs. **My GoHighLevel shipped 6 memes — 2–3× too many for a setup video, and too few screen-rec/step overlays.**
- Good memes are SPECIFIC + subtext-matched: Roll-Safe "smart" at "can't be detected", deadpan cat at "polite/blunt", dog-at-laptop at "just pasting their resume", chalkboard math at "hardest", director character at "Claude does the directing". Never generic, never filler.
- Reference hook mold confirmed across all 5: "Did you know you can now [X]… most people [wrong way]… so before you [waste], try this…" then numbered steps.
- ACTION taken: reduced GoHighLevel memes 6→3, converted fillers to screen-rec placeholders + step-label stickers to match the setup-video recipe. [PARTLY WRONG — see 07-05 override below: the substance-adding was right, the meme-REDUCING was wrong.]

## 2026-07-05 — meme OVER-ADD correction (owner) — REVERSES the "reduce memes" lesson
- **Owner: "dont be afraid to overadd memes. they can always easily be removed by the final editor but adding more is the pain."** The finished-reel meme count (~2–5) is the POST-EDIT state — the editor REMOVED the extras. The automation must OVER-ADD: a meme on EVERY beat where one plausibly fits (~8–15/80s). Removing a meme = one click; a missing one = a re-run. When in doubt, ADD. My previous "memes are spice, reduce to 3" was exactly backwards. Fixed §4.0/§4.4/§4.6/§4C in both specs; the SUBSTANCE layer (screen-recs/outputs/cards) stays — memes are now a FULL SECOND LAYER over-added on top, not a capped spice. (Reconciliation: two dense layers — Layer A substance backbone + Layer B over-added memes — not one or the other.)
- **Studied her actual 76-meme library frame-by-frame (filenames are random — looked at content).** Taste is BROADER than "top-5 famous scenes": core famous memes (SpongeBob, Simpsons, Office, Pixar, Looney Tunes, Marvel, Wolf of Wall St, Mr Bean, Roll-Safe, this-is-fine) PLUS heavy relatable reaction/B-roll (typing furiously, cat-at-laptop, photographer/photoshoot BTS, bored exec, scream, facepalm, talk-show reactions), "smart/analyzing" bits (Roll-Safe head-tap, magnifying-glass "allow me to examine", chalkboard math, equation-overlay eyes, confident kid), text-overlay memes ("NOPE"/"REJECTED"/"JUST TAKE IT"/"YOOOO"/"SUBMIT"), and absurd ones (army cats, top-hat weasel). → §4.0 POPULARITY LAW was too strict ("only famous, reject generic"); relatable reaction clips qualify.
- **Baked-caption rule was WRONG.** Library is full of iconic-text memes (NOPE/REJECTED/JUST TAKE IT). Corrected §4.4: the meme's OWN iconic short text is FINE (it IS the meme); reject only ADDED/off-topic captions, competitor-tool names, or lazy-repost watermarks.
- Library palette by theme (added to §4.0): content/shoot→camera/photographer/BTS; let-AI-work→laptop-typing/cat-at-laptop; rejection→REJECTED stamp/skeptical interviewer/Cowell facepalm; money→Simpsons cash/Wolf; smart→Roll-Safe/magnifying-glass/chalkboard; imagination→SpongeBob rainbow; done→tired SpongeBob; hype/win→Terry Crews/DiCaprio-mic/YOOOO/dancing exec.
- ACTION: over-added GoHighLevel back to 6 memes placed on the beats BETWEEN the screen-rec cards (memes+cards both center → sequence them in time, never overlap); kept all substance (4 screen-rec cards + feature card + 9 stickers + 3 logos). Both layers dense, zero collisions, 30 SFX.

## 2026-07-05 — "make it ACTUALLY 80%" round: HARVEST + FABRICATE real content (the big unlock)
- **Check the owner's parallel/manual asset folders FIRST.** The reference draft's material paths pointed at `Desktop\GoHighLevel\` — the owner's own stash for THIS video: a real $297 pricing screen-rec (297.mp4), the REAL HighLevel logo (fixes the wordmark-tile flag), and a ChatGPT-generated $297 torn-receipt PNG (transparent). Harvesting those replaced 3 placeholders with real content at zero cost. NEW STANDING STEP: at Stage 1, `find` sibling folders named after the topic + read the reference draft's material paths — the owner often pre-collects assets.
- **Placeholders are the LAST resort, not the default.** For each screen-rec beat, try in order: (1) owner's own assets (above); (2) generate the content as HOUSE-STYLE CARDS — reel 2 renders Claude prompts/replies as styled message cards, NOT UI screenshots, so a paper typewriter prompt-card + a "CLAUDE'S BUILD PLAN" spec card ARE the on-brand fulfillment of those beats (HTML → headless-Chrome transparent screenshot: `--default-background-color=00000000`, then PIL-trim); (3) public-page capture: headless-Chrome screenshot of the tool's site (emergent.sh) → ffmpeg Ken Burns (`zoompan z='1.0+0.0018*on'` @30fps) → real-feeling screen-rec MP4; (4) only a beat that truly needs the owner's logged-in session stays a placeholder (GoHighLevel kept exactly ONE: the Emergent build capture).
- capcut `replace-media <project> <segment-id> <file>` works clean for swapping placeholder art (used for the real GHL logo; keeps timing/keyframes).
- CORRECTION to round-13 audit: `capcut projects` DOES exist in v0.12 (the auditor flagged it as nonexistent and we removed it from HANDOFF — restored). Verify CLI claims against `capcut --help`, not against a reviewer's assertion.
- Chrome-extension MCP was disconnected → couldn't capture a live claude.ai chat; the house-style card route turned out MORE on-brand anyway (matches how the finished reels actually show Claude replies).
- Result: GoHighLevel center band = real content 1.2s→42.2s with ONE remaining owner recording. That's the honest 80/20 split: automation ships everything fabricatable; the owner supplies only what needs their real logged-in sessions.

## 2026-07-05 — posters v2 shipped (gpt-image-2 + owner-approved inspo): APPROVED WORKFLOW PROVEN
- Owner picked inspo #6/#9/#12 (all from HIS queries, all [dark]) -> regenerated with gpt-image-2 -> results dramatically better and on-taste (dark grain, red/black/cream, bold condensed type). The inspo-approval gate is the quality lever: taste alignment happens on 47 free Pinterest downloads, not on billed generations.
- gpt-image-2 works on the same images/edits endpoint + params as gpt-image-1 (1024x1536, quality high, b64).
- Saved-original rule paid off immediately: P1's title clipped at my fixed 128px crop -> re-cropped from the saved 1536 original (auto: first bright row - 40px margin) at zero API cost.
- New failure mode seen: model rendered BOTH topics side-by-side in one image (two-up) when the style brief listed both topics. Fix: per-poster prompt now says "Generate EXACTLY ONE single poster (NOT a set, NOT side-by-side panels)" and the shared brief no longer enumerates the other topics. Two-up = sanctioned retry (layout defect), logged: 1 retry this run (3 calls total for 2 posters).
- Smart crop upgrade: choose the 1280-tall window by scanning for the first bright row in the original (numpy rowmax > 200) instead of a fixed 128px bleed.

## 2026-07-05 — poster config update (owner)
- Inspo queries are now OWNER-SET in §4B: "poster design spy", "bold aesthetic poster design", "dark modern poster design" (replaced the generic movie-poster queries). Pinterest via headless-Chrome --dump-dom + i.pinimg.com 736x regex is the reliable route (Bing scrape rate-limits).
- Image model is now **gpt-image-2** (owner call) — all §4B references updated; same edits-endpoint flow, 1024x1536 + bleed line + center-crop to 1024x1280 until proven otherwise on first gpt-image-2 run.
- Approval gate in effect: v3 inspo sheet (12 candidates, query-tagged) shown to owner; generation waits.

## 2026-07-05 — FacelessYouTube owner review: TWO invisible-text root causes + new rules (major)
- **"No subtitles" root cause: the template's sample caption segment carries `visible:false`, and clones inherit it.** All 61 captions existed in JSON, passed every check, and were hidden. **CORRECTION to the GHL "caption endgame" learning:** his GHL auto-captions were a WORKAROUND for my invisible captions (same inherited flag — the final dump's `visible=False` on my track was MY bug, not him hiding it). Keep the brand-fix-list-in-NOTES advice; drop the "he prefers auto-captions" conclusion until seen again with actually-visible captions. RULE: assert `visible:true` on every placed segment; never trust a donor's flag.
- **"No logo labels" root cause: argument-order slip** — position values fed into time slots parked every label at y=6.1 (six screens up) in BOTH the GHL and FYT builds. Lint stays green for offscreen AND invisible segments. NEW §7b check 8b (both specs): render-truth sweep — every segment visible:true + |x|,|y|≤1 + every logo window must contain its name label.
- **Hand-assembled segment dicts render as NOTHING in CapCut** even when lint passes — always deepcopy a real rendering segment of the same class and mutate (GHL's R-cards worked because they cloned a title segment; GHL labels were hand-built and never showed — explains why the owner built his own labels there).
- **Sticker timing must be word-EXACT, not phrase-approximate:** "these two things" placed 18.50 but spoken 19.84 (owner caught it). Anchor to the exact words' start from words.json, not the sentence start. Audited + fixed 3 stickers.
- **NEW OWNER RULE — two text layers may share a time window split upper/lower:** if the upper band (above-head) is taken and another text layer is needed, put it in the below-face band (−0.37…−0.45); never drop it, never shift its timing, never stack two in the same half. Added to §2 of both specs.
- **NEW OWNER RULE — poster inspo approval gate:** show the owner the downloaded Pinterest/web inspiration contact sheet and STOP; generate only after explicit approval ("for now"). Added to §4B. The first posters were rejected as "trash" — inspo taste-alignment comes before spend.
- FYT fixes shipped: 61 captions visible, 7/7 logos labeled (y+0.40), big "+" restored, 3 stickers word-exact, both posters pulled from the timeline (files kept), zero offscreen segments. Lint 0, diverged False.

## 2026-07-05 — FacelessYouTube build: §4B poster module's FIRST LIVE RUN + hand-finish learnings applied
- **Posters work end-to-end.** N=2 enumerated sections ("Number one, pick the right niche" / "number two, the voice") → 2 gpt-image-1 calls (references ×10 + Bing/Pinterest inspo ×3 attached via images/edits multipart `image[]`), 1024x1536 → center-crop 1024×1280 (exact 4:5), placed at the items' word starts (20.82/47.48) with big torn-paper step numbers "1"/"2" beside (owner's numbered-marker pattern). §7b check 11 all green on first firing. P1 came out excellent (exact title, hero concept, all 4 stat callouts, campaign palette); P2 good but the model pushed a "RULE 02" block into the bottom bleed → half-clipped at the crop line. **NEW RULE: always save the uncropped 1024x1536 original beside the crop** so re-framing costs zero API calls. Titles exact → no retry burned (cost law held).
- Inspo download route verified: Bing image search murl regex + PIL verify → 4 real posters incl. a direct i.pinimg.com original; frame-check culled 1. gpt-image edits endpoint: multipart `image[]`, data model/prompt/size/quality; b64 response.
- Hand-finish learnings applied at BUILD time (first video to ship them): logo quick-flashes with big "+" between duals + labels directly under icons (y icon +0.55–0.58, label +0.40); per-word rapid paper trio for the spoken enumeration "(excited)/(whisper)/?"; meme+callout thinking; ducked ambient SFX (0.29); captions built as scaffold with the brand-fix list surfaced in NOTES for the auto-caption pass; V1 +8dB floor with the +11dB note.
- Env-var gotcha: `setx` vars are invisible to shells whose parent predates them — read the key at runtime via PowerShell `[Environment]::GetEnvironmentVariable('OPENAI_API_KEY','User')` into memory (never echo).
- Tooling: bash heredocs (`<<'EOF'`) started failing mid-session ("unexpected EOF") — Write-the-script-to-a-file-then-`python file.py` is the robust pattern for big structured passes.
- Sample-cleanup nuance: removing template sample SEGMENTS leaves orphan materials — harmless, but list them in NOTES with a do-not-prune warning (prune eats grafted template children, §7).

## 2026-07-05 — GoHighLevel FINAL: full diff of the owner's hand-finish (the richest learning set yet)
### What he KEPT from the automation (validated, do these exactly the same next time)
- Title (all 4 layers untouched) · CTA Comment "OWN" (his start 39.70 vs my 39.66) · the 297.mp4 hook at my exact placement · real GHL logo + claude_appicon · magic reveal @0 · success.MP3 @0.224 · torn-paper stickers SURVIVED his whole edit session (the unique-id graft held) · my caption texts/timings used as the scaffold.
### CAPTIONS ENDGAME (workflow change): he generated CapCut AUTO-captions in the UI and HID my imported track (visible=False)
- The live captions are CapCut's own recognition track (native caption animation, which JSON captions can never get, §7a). External captions = timing/copy scaffold + fallback, not the shipped layer. NOTE: the auto captions carry RAW lowercase text ("go high level", "claude", >32ch lines) — brand-word fixes did NOT make it to screen. Next build: keep writing our captions (he uses them to check copy) but EXPECT auto-caption replacement; list the brand-word fixes prominently in NOTES so he can correct the auto captions in-UI.
### MEMES — what survived tells the real taste (5 of my 6 cut, but replaced with BETTER memes, net count similar)
- Kept: SpongeBob-controls at "don't guess" (retimed to the word, a native CapCut sticker slapped on top).
- Swapped for MORE LITERAL visual jokes: this-is-fine → **money-burn.gif + a "-$297/month" text callout + error.MP3** (money joke for a money line, with a stat callout riding the meme). Deleted: Patrick, sweating-guy, math-lady, DiCaprio (relatable-but-indirect).
- ADDED a rapid summary trio @36.5–39.1: one meme per phrase ("scopes it"→sadad.gif, "builds it"→engineer.gif, "own it"→compound clip w/ boosted audio), EACH paired with a mini below-face paper label. → Pattern: meme+label pairs, meme = LITERAL translation of the exact phrase; rapid-fire meme-per-phrase is ON-brand for summary runs.
### FEATURE ENUMERATION pattern (the beat I asked Stage-2 posters about): rapid per-word TORN-PAPER stickers
- CRM → Pipeline → Booking page → Lead form → Dashboard, one sticker per spoken word (0.5–1.1s each) at BELOW-face y≈−0.405, one pop motion per sticker, over a full-screen compound screen-rec montage. So rapid per-item visuals WERE wanted — the vehicle is stickers-over-montage, not posters.
### LOGOS — several spec rules overturned by his final (spec-patch candidates, §9)
- Dual logos are ~0.8s FLASHES (4.67–5.50), not 3.2s holds; staggered entrance (Claude first, then Emergent).
- **The "+" between dual logos is BACK** (big plain-text "+", scale ~2.16, between icons) — reverses the round-8 "no +" call.
- Logos sit HIGHER (y≈+0.55–0.63) with plain white text labels DIRECTLY under the icon (y≈+0.37–0.43), not at +0.23.
- Summary run = logo-per-phrase (Claude icon+label @"Claude scopes it", Emergent @"Emergent builds it").
- Emergent art: he swapped my white rounded icon for **logo_square.jpg** (the true black square mark) — prefer the tool's REAL square mark over a white-tile recomposition.
### STICKERS — copy/timing polish
- Casing/copy edits: "own it"→"Own It", "no coding"→"No coding needed". Holds got SHORTER (0.5–1s pops tight on the word). Added a big torn-paper number "1" as a step marker beside "don't guess" (numbered steps!), a "You" paper on the summary, and a multi-line paper phrase card. Below-face band (−0.40..−0.42) used as much as above-head.
### SFX — count grew to ~44 with LEVEL DISCIPLINE
- Ambient/long SFX are DUCKED: jingle of time 0.29–0.41, ascending whistles 0.29, vine boom 0.23 (only short pops play at 1.0).
- pc-mouse click chains (3 overlapping tracks) run UNDER screen-recs; peep under screen-rec confirmed; error.MP3 on the money-burn.
- **vine boom.mp3 pulled from his PERSONAL library** (`Desktop\SFX\Essential Sound Sfx\...`) — locked bank untouched (23 ✓). Owner may go off-bank; automation still must not.
- V1 volume raised further: 2.512 (+8dB) → **3.63 (~+11.2dB)**. Consider +8dB a floor; flag final level to owner.
### Structure notes
- He inserted screen-recs BETWEEN V1 and the adjust layer; track names now stale (V1 lives on a track named "logo_ghl") — on a FINISHED video: verify, never "fix" track order/names post-edit.
- Compound clips (subdrafts) bundle montages; one had segment volume=10 (compound audio trick).
- His real recordings landed almost exactly in my placeholder windows (15.1–20.1 vs my 16–18+21.4; 31.0–33.2 vs 30.5–33.2; 33.2–35.6 vs 33.4–36.2) — the word-anchored windows were right; only the CONTENT swapped. Cards→real recordings: prompt card→"GHL feature claude.mp4"+"response.mp4", emergent zoom→"paste prompt new.mp4", R4→"app preview.mp4", + muted WhatsApp clip at the CTA.
### PROPOSED SPEC PATCHES (≥3 contradictions per §9 — pending owner confirmation)
1. §2 logos: dual = quick staggered flash (~0.5–1s) + big "+" between + labels directly under icons (y≈+0.37) + icons y≈+0.55; prefer the tool's real square mark. 2. Captions: document the auto-caption endgame (ours = scaffold). 3. §1 audio: V1 default +8dB, note owner may push to ~+11dB. 4. §4: meme choice = literal-visual first at money/action lines; meme+label pairing; rapid meme-per-phrase on summary runs. 5. Feature-enumeration recipe (stickers-over-montage). 6. SFX: duck ambient/long files to ~0.25–0.4.
- Kit excludes: paths.json (machine-specific), ATS_placed_segments.json (build artifact), 05_output contents, NOTES_FOR_*.

## 2026-07-08 - Scroll Animations repair: frame-truth beats JSON-green
- **Title-card exclusivity must include captions and paper stickers, not just memes/cards.** This draft shipped with `Scroll animations`, `Agency $$$`, and captions fighting the 0-3.2s title even though lint was green. Standing check: sample/export frames inside the title window and assert title-only visuals until the exact end of the title card.
- **A label-only density pass is fake automation.** Adding many paper stickers that repeat the spoken captions does not satisfy the 80% automation goal. For setup/how-to reels, every major step needs a substance asset: generated proof card, UI mock, prompt card, frame strip, output/result card, or real screen recording. Stickers should label those assets, not replace them.
- **Weak/face-covering memes are worse than no meme in a how-to segment.** Fry/SpongeBob/DiCaprio covered Cindy's eyes/face and distracted from the tutorial. If a meme cannot fit outside the face/mic lane at a readable size, replace it with a side-card proof asset or a literal workflow visual.
- **Side proof-card geometry for this framing:** compact 900x360 card assets work at scale ~0.42, x about +/-0.60, y about -0.16. This keeps them off the eyes and mostly clear of the center mic lane while still adding substance. Re-check with a visual audit sheet because hand/mic position changes per clip.
- **CTA duplicate rule:** when the big CTA card says `Comment\nPROMPT`, do not also leave a caption reading `Comment PROMPT and I'll` underneath. Keep the caption minimal around the CTA, e.g. `pages.` then `send you the full walkthrough.`
- **Transcript cleanup matters in exported captions:** fix obvious Whisper/segmentation errors (`is it` -> `ZIP`) before handoff; otherwise the mistake is visible even if the overlay assets are fixed.
- **Verifier must decode CapCut text_template children.** Plain text checks missed paper-template layers because their displayed text lives in `text_info_resources[].text_material_id` plus `origin_word_info/current_word_info`. Any "old label removed" or title/CTA placement check must read template children too.

## 2026-07-08 - Scroll Animations v2: CLAUDE 2.0 / v4 smart-add pass
- **Duplicate before spec reruns.** When the owner asks to edit the same video again with an updated spec, copy the whole CapCut draft to a new versioned folder first, then patch only the duplicate. Keep a pre-edit backup of the duplicate.
- **v4 meme direction is smart-add, not flood.** For this `CLAUDE 2.0.md` pass, target about 2-5 memes for a short how-to and only keep them where they can sit side-safe outside Cindy's face/mic lane. Substance overlays remain the backbone.
- **Media-on-media collision checks must include proof cards and memes together.** Memes can coexist with the workflow backbone only when their time windows and boxes do not overlap the proof-card boxes.
- **CapCut proxy render is not enough for overlay QA.** The CLI proxy may report `overlaySegments: 0`; use a JSON-driven visual audit sheet plus scripted verifier for overlays, title bands, CTA wrap, and collision truth.

## 2026-08-20 — social media research (v1 export reviewed by the owner)
Owner verdict: "a lot of errors ... none of the memes made any sense."
Root causes, all confirmed against a finished reel (Final Videos/Sub Agents(.mp4):

1. **Overlay SIZE was computed from raw scale, not displayed pixels.** Spec §2 says
   memes at 0.7–0.85 scale. That figure only holds for LANDSCAPE sources. Applied to
   SQUARE 498x498 clips it produced 842x842px overlays = 44% of frame height, dead
   centre on her face. Measured house pattern: screen-rec cards render ~1015x543px
   (28% of frame height); median overlay across the whole reference reel is 18%.
   FIX: size by displayed px (cap ~940x600), centre at y=0. Spec §2 amended.
2. **Meme selection collapsed when Tenor died.** The spec's public demo key is dead,
   so the bank was substituted wholesale - Kirby inhaling for "save folder", confused
   math lady for "deep analyze". Bank-first is correct as a CHECK, not as a fallback
   for every slot: if Tenor is unreachable the honest move is to say so loudly, not
   to ship six approximate memes. FIX: _state/tenor_fetch.py (no API key, scrapes
   og:video from tenor.com view pages). Spec §4.3 rewritten.
3. **Screen-rec placeholders were bare white text centred on her face.** In finished
   reels the real recordings are wide short cards at y=0. FIX: placeholders now carry
   a dark rounded background card and sit at y=0, exactly where the recording lands,
   so replace-media needs no repositioning.
4. **Every scripted check passed while the export looked wrong.** verify_build.py
   cannot see composition; `capcut render` does not composite overlays. FIX:
   _state/preview_composite.py + new §7b check 9b - LOOK at a composited sheet and
   compare against Final Videos/ before handoff. Non-negotiable.

Not a defect: captions. The reference DRAFT carries the same long cues at size 10 /
y -0.56; the short word-by-word text in her finished videos is CapCut's per-word
reveal animation, applied in the UI (§7a keeps it UI-only). Leave as is.

## 2026-08-20 (round 2) - social media research v3, owner's 15-point review
What the owner actually wanted, and what I had been getting wrong:

1. **Captions: stop building them.** She runs CapCut auto-captions in the UI, which also
   produces the word-by-word reveal the automation cannot. 36 caption segments deleted.
2. **The title was already perfect** - do not touch it once she says so.
3. **Think in CONNECTED VISUALS, not isolated overlays.** Her ask: at "Claude into a social
   media research machine", show the Claude logo LEFT -> an arrow -> the output graphic RIGHT.
   Build motifs that carry an idea across the frame; that is the level of creative filler
   expected, and it is what makes a reel feel authored rather than decorated.
4. **Be literal about the noun.** "one Claude SKILL" needs a skill artefact (a .skill file
   card), not the Claude logo again. "save folder" needs an actual folder window.
5. **Say-it-show-it:** if she says a word that could be a label ("/research", "try this",
   "the hook / the format / the storytelling"), it gets its own text layer on that word,
   with a paired SFX. Every step of a UI walkthrough gets a text layer + a mouse-click SFX.
6. **Layout law she authored herself** (now in spec section 2): meme centred, top edge at
   8.4% of frame; label centred, straddling the meme's bottom edge. All text CENTRED -
   never left/right pairs; multiples STACK vertically.
7. **Memes must survive a "does this make sense" reading.** Rejected by her: Kermit sipping
   tea for "competitors" (irrelevant), Charlie Day for "deep analyze" (he is EXPLAINING, not
   analysing). The test is not "is it a meme about smart" - it is "does this depict the exact
   verb she just said". Replaced with: peeking through blinds (spying on competitors) and a
   man with a magnifying glass (examining).
8. **Sweep wide.** 62 Tenor candidates downloaded this round, 8 kept, the rest deleted.
   Volume is cheap; a wrong meme costs the owner a re-edit.
9. **add-video will not overwrite an existing snapshot in assets/video/** - regenerating a
   PNG and re-running the build silently kept the old art. Hash-check snapshots against
   sources every build (now spec section 7a).

## 2026-08-20 (round 3) - v4, and three bugs that all had the same shape
Every item the owner raised traced to a mechanical fault, not taste:

1. **Same-track overlap gets SILENTLY SERIALISED.** All media went onto one track;
   add-video pushes an overlapping segment to start where the previous ended. The
   dashboard slid 2.10 -> 3.30 and the skill card 4.00 -> 4.50 while its label stayed at
   4.00. Nothing errored; every scripted check passed. FIX: assign lanes BEFORE adding,
   one track per lane - the same greedy allocator already used for text layers.
2. **An unnamed track survives a name-based strip.** A leftover arrow on an unnamed video
   track came back as a duplicate on rebuild. FIX: strip every video track except V1, not
   just the ones this script named.
3. **SFX were capped only at the video end.** `realistic typing` ran 5.37 -> 8.83s straight
   over the doom-scrolling beat. FIX: cap each hit at the NEXT hit; only reveals/risers/
   the CTA jingle keep a natural tail.
4. **Size: the owner's own edit is the spec.** Everything they called "too big" was at my
   620px height cap; everything they accepted was 475px - including the clip they placed
   by hand. Read their manual edits as measurements, not suggestions. CAP_H is now 475.
5. **Frame-contiguity** (new standing rule): when overlays run back to back the next starts
   one frame after the previous ends. Gaps under 0.5s are now closed automatically.
6. **I twice replaced the right analogy with something more dramatic** - Homer-in-the-hedge
   -> Indiana Jones warehouse, SpongeBob rainbow -> head explosion. Both were in my own
   original cast list. Bias to the literal analogy of the exact phrase; "more visually
   striking" is not the goal.
7. Sourcing note: nearly every copy of the SpongeBob imagination meme on Tenor carries baked
   text (POSITIVITY / CHARACTER DEVELOPMENT / TOO BAD / CONFIDENCE). Sweep wide (20 candidates
   for two slots here) and expect to reject most on captions and watermarks alone.

## 2026-08-20 - Claude SEO build (first reel with zero placeholders)
1. **Public pages ARE the screen recordings.** github.com/AgricIDaniel/claude-seo,
   search.google.com/search-console/about and rankscale.ai are all public, so headless
   Chrome + a crop + a slow ffmpeg zoompan produced three real "screen recs" and the reel
   shipped with NOTHING for the owner to record. Placeholders are the last resort (route 3
   of the 07-05 harvest ladder) and on a tool-review video that route covers most beats.
2. **Crop for the 844px cap, not for the page.** A 1440-wide capture shrinks to 0.59x and
   its type becomes unreadable at phone size. Crop to ~1000-1100px wide regions so the
   displayed scale stays near 1:1.
3. **Leave a bottom strip on anything a label will straddle.** The owner's pairing law puts
   the label across the asset's bottom edge, so a card whose content runs to the edge gets
   its last row covered (this is what they flagged on the saves-folder card last round).
   Fix at the SOURCE: every fabricated card now renders with a 78px transparent strip at the
   bottom, and real captures are cropped to include whitespace under the content.
4. **The below-face band is unusable on this framing** (mic sits 66-73% down), so a second
   simultaneous text layer cannot go there. When a step label collided with its own card,
   the fix was to FOLD it into the card's label ("1. Install claude-seo") rather than move
   it - and `label_t` now lets one card carry several labels in sequence.
5. **Plain-text width finally has a calibration.** K = 10.716 render-px per (PIL-unit x font
   size) measured off the template's three paper layers, divided by the template's own
   internal clip scale 2.44 -> **K0 = 4.39 for plain text**. It reproduces the known-good
   "Claude"+"into" title row with an 85px clear gap. preview_composite.py now uses it
   instead of its old 700x200 guess, which had been drawing title boxes 3x too wide and
   making a perfectly fine title look like a collision.
6. **Charlie Day is correct for "tell you WHY" even though he was rejected for "analyse".**
   Same clip, different verb - the rejection was about the verb, not the meme. Worth
   recording so a past rejection is not over-generalised into a ban.
7. **The donor sample sticker gets deleted at the end of build 1, which breaks build 2.**
   Cache the donor SEGMENT to _state/<video>_donor.json on the first run; the materials
   survive in the draft either way. Also added a reference-walking GC for orphan text
   materials (rebuild 3 had piled up 120) - safe because it follows
   segment -> text_template -> text_material_id, which is exactly what `capcut prune` fails
   to do.
8. **Two verifier rules were too strict and both were MY rules, not the owner's:**
   the sanctioned meme+label pair now also covers a card carrying several sequential labels
   on the straddle line, and logo exclusivity now flags only FULL-WIDTH overlays (the
   owner's own logo -> arrow -> card motif is three narrow assets sharing a window by design).

## 2026-08-20 (round 2) - Claude SEO: the owner's hand-finish, diffed segment by segment
Their draft `CapCut Drafts/Claude SEO` (27 tracks / 157 segments) vs my build (14 / ~102).
They kept my skeleton and rebuilt the CONTENT layer. What the diff says:

### A. REAL beats INVENTED - the biggest single change
- My `card_serp` and `card_ai_answer` (generic "yoursite.com") were thrown out and replaced
  with two **Codex-generated photoreal mocks**: a Google SERP and a ChatGPT answer that rank
  **cindyzhu.com.au #1**, with her real favicon/avatar, her coral highlight, and REAL
  competitor names beside her (DataCamp, Gumloop, OpenAI Academy, Anthropic, DeepLearning.AI).
  LESSON: a proof card must be about HER site, with real competitors. "yoursite.com" reads as
  a placeholder and gets cut. Flat HTML cards lose to a photoreal product mock.
- My invented audit card was rebuilt as `cindyzhu_seo_audit_card.png` (660x336) - MY design,
  HER real numbers (NO VIDEOOBJECT / 4 ORPHANS, not MISSING / 12 ORPHANS).
- The four enumerated items (crawlability / core web vitals / schema / internal links) each
  got their OWN real screenshot from her actual audit, instead of one static card with four
  paper labels over it. Same for "where you stand" (real dashboard, health score 72/100).
  LESSON: an enumeration wants one real artefact per item, not one card plus text.

### B. TWO placement grammars, not one
- **Memes and small cards**: top-edge at ~0.83 (my pairing law, confirmed) with the paper
  label straddling the bottom edge. But displayed heights came in at **385-484px, typically
  ~430** - my 475 cap is their MAXIMUM, not their default, and a low-res source gets shrunk
  rather than blown up (charlie 640w -> 627 displayed, i.e. 0.98x; I had it at 768).
- **Dense UI (screenshots, screen recs, the fix list)**: CENTRED at y ~ +0.04, ~1015-1100px
  wide, with the label ABOVE the card, not straddling it. This is the house screen-rec card
  from the frame study - I had never applied it because everything went through meme_geom.
- A real screen recording can also run **full frame** under a meme + label (technical
  analysis.mp4 at 16.30, 1718x1080, speed 2.64).

### C. The title-card window belongs to the LOWER half
My hook motif (Claude -> arrow -> card at y +0.12, across her face) was deleted. Theirs:
three beats in the lower third under the title - audit card at y -0.378 (bleeding off the
LEFT frame edge), then the skill card at -0.411 with a red hand-drawn ellipse + red arrow,
then the Claude icon + "Claude" + paper "Skill" at y -0.33. Title runs 0.00 -> **3.80**
(not 3.20) and L1 carries a **Typewriter** intro animation. Captions run from 0.03 under it.

### D. Logos sit HIGH, enter one at a time, under a header
Icons y **+0.493** sc 0.225 (243px), labels as plain white text at y **+0.317**,
x = -0.518 / 0 / +0.518, each entering on its own spoken name (26.90 / 28.03 / 29.07) and
accumulating, under a paper header **"Checks whether:"** at y +0.700. My y +0.12 band was
wrong - that band is for the title-card motif only. Also: they used the real green ChatGPT
mark from their own logo folder, not my black tile.

### E. Overlays MAY cross a Descript jump cut
Three of my starts were late because I obeyed "end at the first cut inside the window" and
pushed the start past it: thumbs-down 35.70 (mine 36.52), birdman 36.83 (mine 37.70),
devito 9.03 (mine 9.44). Theirs run straight through the cut. Everything else matched my
timings to within 0.03s, so word-anchoring is right - the cut rule is what cost screen time.

### F. Annotation is a layer I skipped entirely
Native CapCut stickers used as red marker pen: an ellipse circling "claude-seo", a curved
arrow into it, three straight arrows pointing at the P1/P2/P3 rows, a pointing-hand cursor,
a shine burst on the Rankscale logo, a red underline + arrow on the health score, and two
compound clips that draw red boxes around the score card's reasons. Spec section 4C calls
this "the #1 overlay for how-to" and I shipped zero of it.

### G. Memes: 4 of my 8 replaced, all in the same direction
Kept: DeVito burning money, Birdman hand-rub, Charlie Day's board (famous, face-forward,
expressive). Cut: spider (-> Linus crawling across a shop floor), Maury (-> real screenshot),
eavesdropping (-> an "ok nice" kid reaction), Roxbury bouncer (-> a thumbs-down guy).
LESSON: the replacements are all simple HUMAN REACTION clips that read at 430px. My cuts
were "clever but abstract" - a spider and a man listening at a wall need a beat of decoding.

### H. Copy: longer and more explicit, two lines are fine
"$4,500 a month" -> "$4,500+ a month" · "2. Run Rankscale" -> "2. Run your site\nthrough
Rankscale" · "Recommending you?" -> "Recommending your\nwebsite?" · "Why you're skipped" ->
"The exact reason" · "In priority order" -> "Auto order based on priority". Added lead-ins
with a colon ("Checks whether:", "So in summary:") and per-word micro-labels ("Your SEO",
"Free", "Skill", "Now feed", "both reports").

### I. The summary replays the visuals
My stacked text trio was deleted. Each summary item got its card back on screen (audit card
46.97, score card 48.40, fix list 49.77) with its own paper label. Recap = replay, not a
text stack.

### J. Misc measured values
- V1 volume **2.9688 (+9.5 dB)** - above the 2.512 floor again (2nd time; GoHighLevel was 3.63)
- CTA paper carries a **Tremble** animation; title L1 Typewriter; captions Lineup Release
- Their clips are trimmed TIGHTER than mine (birdman 0.93 vs 1.40, charlie 1.70 vs 2.45,
  rankscale 1.83 vs 3.76) and the freed time is spent on a NEW asset - density over duration

### Owner's answers to the round-2 questions (2026-08-20)
1. **Cut rule:** stays intact, "but you can override the rule when the same asset is required
   for explanation for further adjacent phrases." -> `house_layout.trim_at_cut(...,
   carries_explanation=True)`.
2. **Proof visuals:** photoreal mocks carrying HER brand - cindyzhu.com.au, her avatar, the
   coral highlight, real named competitors. Flat generic cards are out.
3. **Real numbers are NOT required - "fake it, just fill in fake numbers."** So CORRECT the
   framing of section A above: what they replaced was the generic IDENTITY ("yoursite.com"),
   not the invented figures. Invented metrics are fine; an invented BRAND is not.
4. **Annotations:** yes, reuse their sticker set. Harvested to `_state/sticker_kit.json`
   (43 stickers from 26 drafts; all 43 resolve in CapCut's artistEffect cache on this
   machine, and a new machine re-fetches them by resource_id on the first online open).
   Their most-used by far is the red circle highlight `7470375665200549181` (22 placements).

### What was built out of this round
- **`_state/house_layout.py`** - the three placement grammars as code, validated against
  their own numbers: `meme_geom` reproduces DeVito 844x385 and Linus 694x430 exactly and the
  other four within ~10%; `card_geom` reproduces the centred screenshot at 1015px wide with
  its label at y +0.365 exactly. Also holds the logo band (icons +0.493 / labels +0.317 /
  x +/-0.518 / scale 0.225 / staggered entry / paper header at +0.700), the title band
  (-0.18..-0.48), V1 = 2.97, the cut-override, and `place_sticker()`.
- **DEFAULT_H = 430** is the new meme size target; 475 stays as the hard ceiling.

## 2026-08-20 (round 3) — Remotion as the graphics factory (owner-directed)
Owner: "use actual graphics and imagery like we did with the SEO video instead of filling
everything with just memes… make it ultra realistic and aesthetic", plus integrate Remotion
and Hyperframes.

- **Remotion is the right tool for this pipeline; Hyperframes is not (yet).** Remotion is
  local, free, deterministic, and renders overlay CARDS — exactly the unit this pipeline
  composites. Hyperframes authors a WHOLE video project from a prompt and its `render_video`
  is a paid cloud action, so it fits as an optional b-roll interlude or a platform cutdown,
  not as the asset factory. Did not fire a paid render without asking.
- **A UI-walkthrough video wants a UI mock, not a meme.** Eight compositions replaced five
  memes and all seven screen-rec placeholders: the skill file, the Skills upload flow with
  an animated cursor, `/research` typing itself, the pillars breakdown, the deep analysis
  with a scrolling transcript, the viral counter, the saved folder, and a legible
  thumbnail-sized variant for the title motif.
- **Build the brand from the owner's own site, not from memory.** cindyzhu.com.au gave the
  exact palette (cream #faf7f2, coral #e8856a, ink) plus the pill-badge idiom and her real
  numbers (165k audience, 7.5M monthly views) — all now in `04_assets/remotion/src/theme.ts`.
- **Render MP4 full-bleed, not alpha.** A rounded card on a transparent background becomes a
  black-cornered rectangle in MP4. Making the composition itself the card sidesteps the whole
  alpha question and reads as a real screen recording, which is the house look anyway.
- **Crop every composition to the height its content uses.** First renders were 30–45% empty
  because the frame was taller than the layout; an overlay that is half empty reads as a
  mistake. Also caught a grid overflowing its window - LOOK at the rendered frames, the same
  rule as section 7b check 9b.
- **A shrunk dense dashboard is unreadable.** The title motif needed a 380px-wide graphic;
  the full Pillars card at that size was mush. `PillarsMini` (three big rows) is the answer —
  design a separate composition for thumbnail sizes rather than scaling one down.
- **Solve annotation positions from the card geometry, don't eyeball them.**
  `x = -0.47 + 0.94 * (px_x / comp_w)`, `y = card_top - (dh/960) * (px_y / comp_h)`.
  My first pass was guessed and would have put the red circle in empty space.
- Remaining unknown: the composite preview has no sticker renderer, so annotation stickers
  are the one layer that ships unobserved. Worth teaching preview_composite.py to draw the
  sticker's cached PNG from `material.path` next round.

## 2026-08-21 — the owner's asset-supply loop (they proposed the workflow)
Owner verdict on my Remotion mocks: "very mid… claude can not fully visualize things on its
own without proper reference images." The fix they designed, now the standing process:

1. I identify every beat needing an image/video and write **exact generation prompts**, plus
   a list of **real app screenshots** to capture. Drop folder named up front (Desktop).
2. They generate/capture while I keep working; I check the folder after ~15 min.
3. I identify each asset, crop it, and build with it.

**Do not imagine an app's UI.** My invented "Claude Settings" window was wrong in layout AND
in flow: the real thing has an Add ▸ dropdown and a separate upload modal, so the walkthrough
is 6 steps, not 2. Ask for the screenshot.

**Crop tight, then upscale.** A 2559px desktop grab shown at 1015px wide renders its 14px UI
text at ~9px - unreadable on a phone. Cropped to the named panel (~370-1176px wide) the same
text lands at 20-30px. This is what their own SEO screenshots were doing (538x244 shown at
1015 = a 1.9x upscale) and I had read it as "small screenshots" rather than "crop and enlarge".

**Measure crop boxes off a coordinate-grid overlay.** Two auto-detectors (percentile, then
longest-bright-run) both failed on these dark-mode grabs. Drawing a labelled 5%-grid over one
screenshot and reading the panel bounds took one look and was exact.

**Generated images beat hand-built HTML for finished art.** G2/G3/G4 are better than my
Remotion equivalents at a fraction of the effort. Remotion earns its place for things that
must MOVE or be assembled from parts (cursor paths, typing, counters), not for static cards.

**Judge composition at full resolution only.** preview_composite.py renders each frame at
~340px wide. I twice called correctly-centred cards "off-centre and bleeding off frame" from
those tiles. `_runs/social_research/fullres_check.py` pastes real overlays on real V1 frames
at 1080x1920 - use it before reporting any layout fault, and trust the numeric transforms
over a downscaled sheet.

**Centre-band cards are TOP-anchored** (y +0.31) as of this round: centre-anchoring made a
247px-tall card sit across her eyes while a 700px card sat correctly, so a run of step cards
jittered vertically.

## 2026-08-21 — the graphics-generation round was REJECTED OUTRIGHT
Owner: "noooo, this was super bad. remove this process entirely from future runs." Asked
which part, they chose **the whole v6 direction** — treat the entire round as a dead end.
The draft is restored to **v4** and `build_social_v5/v6.py` are moved to `_state/_retired/`.

What that covers, so it is not attempted again on any video:
- Building the reel's substance out of **generated images / code-drawn UI cards** placed as
  large centre-band overlays. Two flavours were tried and BOTH were rejected: Remotion
  mocks (v5, "very mid") and real screenshots + ChatGPT art (v6, "super bad").
- The **asset-request loop** (me writing generation prompts and screenshot requests, the
  owner supplying files) came out of this round and dies with it.

DO NOT read this as "the owner dislikes real screenshots" — their own Claude SEO finish is
full of them. The rejected thing is the automation driving that direction on its own.
Before rebuilding this reel again, ASK what the target should look like rather than
inferring it; two full rounds were spent inferring and both missed.

STILL VALID (owner-derived, from their own hand-finished edit, not from this round):
`_state/house_layout.py` grammars, the sticker kit, and the section-2 spec patch.
