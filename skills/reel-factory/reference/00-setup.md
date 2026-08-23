# Kit & first-run setup

> Part of the Cindy Zhu Reel Factory spec (v3.0). Loaded on demand by the
> `reel-factory` skill - see SKILL.md for the routing table.

**`/reel-factory:reel-setup` now automates all of this** — it installs the kit, places `CZ_TEMPLATE`
into this machine's drafts folder, relinks the template's sample audio, and runs the
doctor. Read this file when a doctor check FAILS and you need to know what the check was
actually asserting, or when setting up somewhere the scripts do not cover.

Two things `/reel-factory:reel-setup` deliberately does not do: install **MADE Awelier** (licensed
personal-use, so each editor downloads it themselves — installed family name is
`MADE Awelier PERSONAL USE`), and warm CapCut's effect cache (item 3 below — only opening
the template in CapCut can do that).

## 0. KIT & FIRST-RUN SETUP (once per machine)
The automation needs these present; run Stage 0 (§6) to verify, and STOP if missing:
1. **Tools:** capcut-cli (npm), Python 3 + faster-whisper + Pillow, ffmpeg/ffprobe,
   CapCut desktop (any modern version; behind VPN in regions where CapCut is blocked —
   builds must NEVER trigger cloud fetches). A browser-automation MCP or plain HTTP
   access for Tenor downloads.
2. **Fonts:** Poppins + MADE Awelier installed as system fonts. The Markerist look
   lives only inside CapCut's effect cache — it arrives via the template, never by name.
3. **Template draft** (REQUIRED — no degraded mode): the house template draft
   (`CZ_TEMPLATE`) copied into this machine's CapCut drafts folder. On a new machine
   the owner opens it once in CapCut (online) so CapCut fetches the fonts/paper
   effects into its cache, then confirms it contains: the styled title lines, one
   sample paper-cutout sticker layer with sample text, a styled comment-card CTA
   layer parked past the video end, sample styled captions, and the color-grade
   adjust layer.
4. **SFX bank:** the locked SFX folder ("Cindiezhu sfx" — 23 files at last audit; the
   authoritative count is `_state/sfx_map.json`, and map ↔ folder must match exactly).
   Never invent filenames; build/refresh `_state/sfx_map.json` from it (schema +
   tagging method in §3).
5. **Pipeline home** (any writable folder; store the resolved path in
   `_state/paths.json`): `01_intake`, `02_transcripts`, `03_plans`, `04_assets/memes`,
   `04_assets/logos`, `04_assets/screenrecs`, `05_output`, `_state`, `_backups`.
6. **State files** in `_state/`: `master_reference.md` (brand bible — outranks this
   file on brand questions except where §2–5 carry newer verified values),
   `style_learnings.md` (read every session, append after every delivered video),
   `paper_donor_child.json` + `tpl_paper.json` (styled paper-text donors — regenerate
   from the template's sample layer via `capcut save-template` BEFORE ever deleting it),
   and a per-video `<name>_paper_text_map.json` (segment-id → sticker text).
7. **CapCut must be CLOSED during every external write.** It never re-reads from disk
   while open and its next autosave destroys your changes. Check the process list
   before every write; a watcher script is part of the kit (`_state/post_session_fix.py`)
   — it (a) polls the process list until CapCut exits, THEN (b) runs the §7b
   re-grafts/checks. If it's missing, regenerate BOTH halves — §7b describes only
   half (b); half (a) is a simple process-poll loop.
8. **Canonical timeline file:** run `capcut diagnose <draft>` — on modern CapCut the
   canonical is `template-2.tmp` and `draft_content.json` is a mirror; on older
   versions `draft_content.json` is canonical. ALWAYS write whichever diagnose calls
   canonical, then copy it over the mirror, and require `diverged: false`. Never
   assume — re-check per machine and after CapCut updates.

