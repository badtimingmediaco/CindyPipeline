---
description: One-time machine setup — install the kit, place the CapCut template, verify everything
argument-hint: "[pipeline folder, default ~/Documents/CindyPipeline]"
---

Set this machine up to build reels. Run once per editor.

## 1. Run setup

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/setup.py" ${ARGUMENTS:+--pipeline "$ARGUMENTS"}
```

This creates the pipeline home, installs the kit (SFX bank, meme bank, logos, graphics,
donor JSONs, sticker kit, scripts), finds this machine's CapCut drafts folder, places
`CZ_TEMPLATE` into it, relinks the template's sample audio, and then runs the doctor.

It is additive and idempotent — safe to re-run. It will refuse to proceed if CapCut is
open, or if the chosen pipeline folder is inside OneDrive/Dropbox/Google Drive.

## 2. Read the doctor output and fix what it flags

Report the result plainly. Do not proceed past a failure. Common ones:

| Failure | Fix |
|---|---|
| `faster-whisper` / `Pillow` | `pip install faster-whisper pillow` |
| `ffmpeg` / `ffprobe` | `winget install Gyan.FFmpeg`, then reopen the terminal so PATH refreshes |
| `Node.js` | install from nodejs.org |
| `capcut-cli` | `npm i -g capcut-cli` |
| `CapCut drafts folder` | open CapCut once and create an empty project, then re-run |
| `Poppins installed` | install Poppins (free, Google Fonts) — per-user install is fine |
| `MADE Awelier installed` | **the editor must download and install this themselves.** It is licensed for personal use and is deliberately not redistributed in this repo. Its installed family name is `MADE Awelier PERSONAL USE` — CapCut needs that exact name, not "Awelier". |
| `CapCut is CLOSED` | close CapCut. This one is non-negotiable for every build, not just setup. |

Offer to run the pip/npm installs for the editor. Do not install fonts for them.

## 3. The one manual step

Tell the editor, in these words, that this part cannot be automated by anyone:

> Open `CZ_TEMPLATE` in CapCut once, while online. CapCut then downloads the Markerist
> font, the torn-paper effect and the caption assets into its own local cache. Those live
> inside CapCut, not on disk, so no kit can ship them.
>
> While it's open, confirm: the title lines render styled, the sample paper sticker shows
> its text, the CTA card sits past the video end, and the sample captions are styled.
> Then save and close.

## 4. Confirm ready

Re-run the doctor after they have done step 3:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/doctor.py"
```

When it prints READY, tell them how to start: drop an MP4 into `01_intake/` and say
**"run it &lt;name&gt;"**.
