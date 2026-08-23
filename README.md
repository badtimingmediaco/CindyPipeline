# Cindy Zhu Reel Factory

Turns one descripted talking-head MP4 into a near-finished CapCut draft — title, torn-paper
stickers, memes, logos, cards, SFX and CTA — then proves the build with scripted assertions
before handing it over.

It runs inside **Claude Code**. There is no app to launch and no GUI: you drop a video in a
folder and say *"run it"*.

---

## Install

You need [Claude Code](https://claude.com/claude-code), logged in with your own
subscription. Then, once:

```bash
claude plugin marketplace add cindyzhu/cindy-reel-factory
```

```bash
claude plugin install reel-factory@cindy-reel-factory
```

That pulls down the whole kit — the SFX bank, the meme bank, the logos, the CapCut
template, the placement laws, the scripts. Then open Claude Code and run:

```
/reel-setup
```

It builds your pipeline folder, finds your CapCut drafts directory (including a custom
one), places the template, and tells you exactly what is missing. Fix what it flags and
re-run — it is safe to run as many times as you like.

## Use

Drop an MP4 into `01_intake/` and say:

```
run it claude seo
```

The name does not have to be right. Case, dashes, missing extensions and typos are all
fine — `run it clade seo` finds `Claude SEO.mp4`. If two files are genuinely close, it
asks rather than guessing.

Then it analyses the video, plans the edit, builds the draft, and verifies its own work in
a loop until the checks pass. You open the result in CapCut and polish.

When you have polished it, tell it what you changed:

```
/reel-learn
```

That is the loop that makes the next build better. Use it every time.

---

## What you need on your machine first

`/reel-setup` checks all of this and tells you what to do about anything missing. Most of
it it can install for you if you ask.

| | |
|---|---|
| **CapCut desktop** | Any modern version. If CapCut is blocked in your region: paid VPN, desktop app, one server, never switched mid-session. |
| **Claude Code** | Logged in with your own subscription. |
| **Node.js** + `capcut-cli` | `npm i -g capcut-cli` |
| **Python 3** + `faster-whisper`, `pillow` | `pip install faster-whisper pillow` |
| **ffmpeg** | `winget install Gyan.FFmpeg` |
| **Poppins** | Free, Google Fonts. Per-user install is fine. |
| **MADE Awelier** | You install this one yourself — it is licensed personal-use, so it is not redistributed here. Its installed family name is `MADE Awelier PERSONAL USE`. |

**Windows only for now.** The scripts have POSIX branches so they do not crash on a Mac,
but macOS is not supported yet.

### The one step nobody can automate

After setup, **open `CZ_TEMPLATE` in CapCut once, while online.** CapCut then downloads the
Markerist font, the torn-paper effect and the caption assets into its own local cache.
Those live inside CapCut, not on disk, so no kit can ship them.

While it is open, check that the title lines render styled, the sample paper sticker shows
its text, the CTA card sits past the video end, and the sample captions are styled. Save
and close.

---

## The rule that matters most

**CapCut must be closed whenever the agent is writing.** CapCut never re-reads from disk
while it is open, and its next autosave will destroy the build. The scripts refuse to write
while it is running — but if you had it open mid-build, say so, and the post-session
verification will run.

## What it will not do

- **Captions.** You run CapCut auto-captions in the UI yourself. It hands you the list of
  brand words the recogniser gets wrong instead.
- **Touch your VO, your face, or your colour grade**, or re-cut the Descript edit.
- **Generate images with any other tool.** Claude draws every fabricated card itself, with
  Pillow. No OpenAI, no ChatGPT, no Remotion, no Hyperframes — those may come in a later
  version.

---

## What is in here

```
skills/reel-factory/    the spec — a router plus reference files loaded on demand
commands/               /reel-setup, /reel-run, /reel-learn
scripts/                doctor, setup, fuzzy input matching, placement laws,
                        verification, Tenor sourcing, post-session repair
kit/                    SFX bank (23), meme bank (37), logos, graphics,
                        CZ_TEMPLATE, donor JSONs, the 43-sticker annotation kit,
                        the brand bible and the accumulated learnings
```

`scripts/house_layout.py` is worth knowing about: every constant in it was measured off a
draft Cindy finished by hand. It is the difference between the output looking like hers and
looking like a robot's.
