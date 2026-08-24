# The pipeline, stage by stage

> Part of the Cindy Zhu Reel Factory spec (v3.0). Loaded on demand by the
> `reel-factory` skill - see SKILL.md for the routing table.

**Stage 0 — Doctor.** capcut doctor; resolve paths; fonts present; sfx_map matches
bank; template draft + donor JSONs + sample layers present; CapCut closed. Any
failure → report and STOP.
**Stage 1 — Analyze.** ffprobe the input. faster-whisper — **use the model named in
`_state/warm_models.py` (`small.en`); do not pick a different one.** Four editors on four
models produce four different transcripts, and every sticker's exact words and every asset's
timing are anchored to that transcript. **Never substitute a smaller or faster model
because a download is slow** — that silently changes the transcript the whole build rests on.

**Check the model is cached BEFORE transcribing** (`python _state/warm_models.py --check`).
If it is not, do **not** try to download it from inside a tool call: the weights are ~500MB
and the download will exceed the tool timeout, which reads as a connection failure and
wastes ten minutes. Stop and tell the editor to run this at their **PowerShell** prompt,
with Claude closed, then say "run it" again:

```
python -c "from faster_whisper import WhisperModel; WhisperModel('small.en', device='cpu', compute_type='int8')"
```

With the model cached, `word_timestamps=True` →
words.json + transcript. Scene-detect the cuts. **Extract a frame contact sheet of
the input** (tile ~16 frames) and LOOK at it: framing, where her face/hands sit,
mic position — this calibrates safe zones. Then do a **written transcript analysis**
in the plan file: the video's core promise, the beat map (hook / pain / solution /
steps / payoff / CTA), the tools mentioned (→ logo moments), the emotional turns
(→ meme beats, §4.1 briefs), the punchiest exact phrases (→ sticker copy), and the
main keyword of the whole video (→ title line 3). Build the brand-word caption fix
list (Claude, CapCut, Descript, this video's tools; whisper mishears
"Comment"→"Common").
**Stage 2 — Ask.** If anything is ambiguous (which tools get logos, CTA word, whether
screen recordings are wanted, unclear beats), ask the user NOW — one batched round of
questions. Don't ask about things the guardrails already decide.
**Stage 3 — Plan of action** → `03_plans/<name>_plan.md` (agent's own reference +
audit trail):
- **Title drafting happens HERE, from the transcript analysis.** Draft 3–5 candidates
  in her molds ("how to X" > "turn Claude into Y" > "N secret Z" > "stop X from Y").
  **GRAMMAR LAW: write the title as ONE natural sentence FIRST, then split it into
  the three lines — the lines concatenated top-to-bottom must read back as exactly
  that sentence.** Apply the read-aloud test to every candidate. If the §2 pattern
  constraints (Claude in line 2, main keyword last on line 3) can't split the
  sentence grammatically, REPHRASE the sentence until they can — never force words
  into slots. Shipped failure: "how to / recreate with Claude / Any Website" reads
  "how to recreate with Claude any website" (broken); the same idea phrased right:
  "how to / make Claude recreate / Any Website" → "how to make Claude recreate any
  website" (correct). Then lock ONE winner satisfying the §2 pattern exactly: line 1
  = short white-Markerist lead-in; line 2 = contains "Claude" (orange Awelier) +
  optional white Markerist words; line 3 = the video's main keyword (1–3 words) on
  the torn-paper layer. Record in the plan: the full sentence, the per-line split,
  the read-aloud confirmation, and the measured width check for each line.
- every sticker {t_in,t_out,text,zone} in her exact words
- every meme slot as a full §4.1 MEME BRIEF {line, surface, subtext, joke, cast
  scenes, chosen queries}
- logo moments {tool, first-mention time, dual/single}
- screen-recording placeholder list {window, hard-wrapped instruction text}
- full SFX schedule, CTA word + card copy, cut-trim table.
Everything word-anchored, cut-trimmed, density-checked and width-checked ON PAPER
before touching CapCut.
**Stage 4 — Execute strictly per plan + guardrails.**
Order: clone template (full folder copy, new name `CZ_<topic>_<date>_v<N>`, zip
backup first) → V1 — **after add-video, register the file in `draft_meta_info.json`
→ `draft_materials[type=0]` (clone an existing entry's shape: metetype "video",
width/height/duration, import timestamps) so the draft looks like a UI import, and
smoke-test with `capcut render --scale 0.25` on a few seconds to prove the timeline
and media actually resolve; if V1 still opens black (environment-side CapCut cache
issue), relink to the original intake path, and as last resorts: manual re-import in
the UI or lossless rewrap (`ffmpeg -c copy -movflags +faststart`) — NEVER re-encode
her footage** → captions (≤32-char SRT → import-srt --style-ref, set y=−0.56,
add pop keyframes) → title (set-text on plain lines; paper main line) → paper
stickers (§7 two-phase) → memes (download → frame-check → place → margins) → logos →
screen-rec placeholder text layers → SFX → volume pass (V1 +8 dB = 2.512; success.MP3 −13 dB = 0.224) → CTA
retime/retext → track-order enforcement (the literal last WRITE) → mirror sync
(a plain file copy) → read-only lint clean + diagnose not diverged.
**Stage 5 — Verify loop.** Verification is **scripted assertions with printed
evidence** (id lists, exact values, pass/fail per check) — never an LLM summarizing
JSON by eye: a reviewer once printed "all ids unique — PASS" while every copy shared
one child (it read the wrong field), plus three false FAILs. Write the §7b checks as
code; the review subagent's job is to RUN that code, read the printed evidence, check
plan conformance and §2 style, and report discrepancies. Fix every finding,
re-verify. **Loop until the checks print zero failures.** Then write
`05_output/<name>/NOTES.md`: placeholders pending, uncertainty list, polish checklist
(type-in fallback list for any paper text that blanks, apply auto-caption animation
in UI if wanted, color grade, watch at 1×, export). Report build stats + top 3 checks.

