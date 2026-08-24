# Cindy Zhu Reel Factory

Turns one descripted talking-head MP4 into a near-finished CapCut draft — title, torn-paper
stickers, memes, logos, cards, SFX and CTA — then proves the build with scripted assertions
before handing it over.

It runs inside **Claude Code**. There is no app to launch and no GUI: you drop a video in a
folder and say *"run it"*.

> ### Run it on the computer you edit on
>
> Not on Claude Code for web, and not in a cloud session. This tool drives **CapCut
> desktop** — it writes into CapCut's local drafts folder, and you open the result in the
> app afterwards. Cloud sessions are Linux containers, CapCut has no Linux version, and the
> container is thrown away at the end of the session anyway.
>
> Setup will stop and tell you if you are on the wrong kind of machine. Install Claude Code
> on your Windows editing machine and run it there.

---

## Install

**Open PowerShell and paste this one line.** Nothing else.

```powershell
irm https://raw.githubusercontent.com/badtimingmediaco/CindyPipeline/main/install.ps1 | iex
```

Press enter and leave it. It takes a few minutes and asks you nothing.

It installs git, Node, Python, ffmpeg, `capcut-cli`, the Claude Code CLI, **both fonts** and
the plugin itself — skipping anything you already have. Then it tells you the one thing
left to do.

<details>
<summary>To open PowerShell: press <b>Win</b>, type <code>powershell</code>, hit enter.</summary>

You don't need to "run as administrator" — everything installs for your user only.

If the installer stops with problems listed, close the window, open a **new** PowerShell,
and paste the same line again. Most failures are just Windows not having noticed a newly
installed program yet, and a second run clears them.

</details>

### Then

**1.** Open a new terminal, run `claude`, and type:

```
/reel-factory:reel-setup
```

That builds your pipeline folder, finds your CapCut drafts folder wherever it is, and
places the house template. It tells you if anything is still missing.

**2.** Open `CZ_TEMPLATE` in CapCut once, **while online**, then close it. CapCut downloads
its own fonts and the torn-paper effect at that moment. Nobody can automate this part —
those files live inside CapCut, not on disk.

That's it. You're ready to build.

### Two different prompts — this trips everyone up

There are two places you can type, and they are not interchangeable.

| Prompt | Looks like | What goes here |
|---|---|---|
| **PowerShell** | `PS C:\Users\you>` | `claude`, and anything starting with `claude plugin ...` |
| **Claude** | a bare `>` after you have run `claude` | `run it mobile app`, `/reel-factory:reel-setup`, and anything you want Claude to do |

If you type a `claude plugin ...` command at the **Claude** prompt, Claude will ask
permission to run it as a shell command. Saying yes works fine — but it is cleaner to
`/exit` back to PowerShell first.

## How this works day to day

**You do not edit in PowerShell.** PowerShell is only where you *talk to Claude* — it
replaces the chat window, not CapCut. You still edit in CapCut exactly as you always have,
and that is still where you will spend most of your time.

| Where | What you do |
|---|---|
| **File Explorer** | Drop your MP4 into `Documents\CindyPipeline\01_intake\` |
| **PowerShell** — run `claude` | Say `run it` and the video's name, e.g. `run it mobile app`. It analyses, plans and builds the draft. **CapCut must be closed while it works.** |
| **CapCut** | Open the new `CZ_...` draft. Polish, run auto-captions, colour grade, export. |
| **PowerShell** | `/reel-factory:reel-learn` — tell it what you changed by hand |

One rule ties those together: **CapCut closed while Claude is building, open once it is
done.** CapCut never re-reads from disk while it is open, so its next autosave would
overwrite everything Claude just built.

> The Claude **desktop app** cannot run this — it has no way to install or see plugins.
> Use `claude` in PowerShell. That is the only place the commands exist.

## Use

Drop an MP4 into `01_intake/` and say:

```
run it claude seo
```

Type the name plainly — **no angle brackets, no quotes**. The name does not have to be
right either: case, dashes, missing extensions and typos are all fine, so `run it clade seo`
finds `Claude SEO.mp4`. If two files are genuinely close, it asks rather than guessing.

**If "run it" ever gets misunderstood** — Claude starts searching Notion, Drive or the web
instead of building — use the explicit command instead:

```
/reel-factory:reel-run claude seo
```

That does exactly the same thing but leaves nothing to interpretation. It is worth
reaching for whenever your video's name sounds like a document, a company or a topic
rather than a video, since those readings compete with the plain one.

Then it analyses the video, plans the edit, builds the draft, and verifies its own work in
a loop until the checks pass. You open the result in CapCut and polish.

When you have polished it, tell it what you changed:

```
/reel-factory:reel-learn
```

That is the loop that makes the next build better. Use it every time.

---

## What the installer sets up for you

You do not need to install any of this by hand — `install.ps1` does it. This is here so you
know what is on your machine, and what to do if a piece ever breaks.

| | |
|---|---|
| **CapCut desktop** | Any modern version. If CapCut is blocked in your region: paid VPN, desktop app, one server, never switched mid-session. |
| **Claude Code CLI** | Installed for you. You log in once with your own subscription. The Claude *desktop app* alone cannot install plugins — it has no `claude` CLI and no `/plugin` command — which is why the installer sets up the terminal CLI. |
| **Node.js** + `capcut-cli` | `npm i -g capcut-cli` |
| **Python 3** + `faster-whisper`, `pillow` | `pip install faster-whisper pillow` |
| **ffmpeg** | `winget install Gyan.FFmpeg` |
| **Poppins** | Ships with the kit and is registered for you automatically. |
| **MADE Awelier** | Ships with the kit and is registered for you automatically, under the exact family name CapCut needs (`MADE Awelier PERSONAL USE`). |

**Windows only for now.** The scripts have POSIX branches so they do not crash on a Mac,
but macOS is not supported yet.

If anything is missing or broken later, `/reel-factory:reel-setup` names it precisely, and
re-running the installer line fixes most of it.

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
commands/               /reel-factory:reel-setup, /reel-factory:reel-run, /reel-factory:reel-learn
scripts/                doctor, setup, fuzzy input matching, placement laws,
                        verification, Tenor sourcing, post-session repair
kit/                    SFX bank (23), meme bank (37), logos, graphics,
                        CZ_TEMPLATE, donor JSONs, the 43-sticker annotation kit,
                        the brand bible and the accumulated learnings
```

`scripts/house_layout.py` is worth knowing about: every constant in it was measured off a
draft Cindy finished by hand. It is the difference between the output looking like hers and
looking like a robot's.
