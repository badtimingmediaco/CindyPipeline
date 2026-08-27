# Deploying and maintaining this

For whoever owns the repo. Editors do not need this file — they need `README.md`.

---

## Publishing it the first time

The repo is ~29 MB of content. That is comfortably inside a normal git repo; no LFS, no
release assets, nothing special.

1. Create a **public** repo. It lives at **`badtimingmediaco/CindyPipeline`**.
   Do NOT tick "Add README", ".gitignore" or "license" — this checkout already has all
   three, and an initialised remote would reject the push.
2. Point this checkout at it and push:

```bash
git remote add origin https://github.com/badtimingmediaco/CindyPipeline.git
```

```bash
git push -u origin main
```

3. **If the repo ever moves**, four places must change together or `claude plugin install`
   clones the wrong location: the `repo` field in `.claude-plugin/marketplace.json`, the
   `repository` field in *both* manifests, and the install command in `README.md`.

Then have one editor run through `README.md` start to finish on a clean machine before
you send it to the other three.

### Two names, deliberately

The repo is **`CindyPipeline`**; the *marketplace* is **`cindy-reel-factory`** (the `name`
field in `marketplace.json`). That is why the second install command reads
`reel-factory@cindy-reel-factory` and not the repo name. Renaming the marketplace would
break every editor who has already added it — leave it alone.

Note too that the repo name collides with the working folder: `CindyPipeline` on GitHub is
the **tool**, while `Documents\CindyPipeline` on an editor's machine is their **workspace**.
Nobody clones the repo by hand — the plugin installer puts it under `~/.claude/plugins` —
but say this out loud if an editor looks confused.

## Shipping an update

Editors update by re-running the same one-liner they installed with:

```powershell
irm https://raw.githubusercontent.com/badtimingmediaco/CindyPipeline/main/install.ps1 | iex
```

**`claude plugin install` alone will NOT update them.** It is a no-op when the plugin is
already present, so an editor who re-ran only that would sit on their first-installed
version forever. The installer therefore runs `marketplace update` and `plugin update`
too. `plugin update` needs the fully qualified `reel-factory@cindy-reel-factory` - the
bare plugin name reports "not found".

Updates need a Claude Code restart to take effect.

**Editors are told automatically.** The plugin ships a SessionStart hook
(`hooks/check_update.py`) that checks the published version at most once a day and prints
a one-line notice with the update command when they are behind. So you do not have to
chase anyone - but they still have to run the command, and restart.

Why it notifies instead of self-updating: running `claude plugin update` from inside a
live session rewrites the plugin cache that same session is reading from, and the new
version would not apply until a restart regardless. The editor would be told nothing while
their files changed underneath them. A notice they can act on is safer and clearer.

The hook fails silently on every path - offline, blocked, malformed response - and stamps
its throttle file BEFORE the network call, so a hanging request cannot make every session
retry.

**Wait ~5 minutes after pushing before telling anyone to re-run.** The installer is fetched
from `raw.githubusercontent.com`, which serves a cached copy for a few minutes after a push
- measured at ~200 seconds. An editor who runs the one-liner immediately after you push a
fix gets the OLD script, silently, and reports that your fix did not work. Confirm the new
content is live before you tell them:

```bash
curl -s "https://raw.githubusercontent.com/badtimingmediaco/CindyPipeline/main/install.ps1?cb=$(date +%s)" | grep -c "<something new>"
```

### Your side of an update

Bump `version` in `.claude-plugin/plugin.json` (and the `version:` line in
`skills/reel-factory/SKILL.md`, which should match), then:

```bash
git add -A && git commit -m "..." && git push
```

Bump the version whenever the change is worth an editor noticing — a new rule, a changed
default, a fixed bug that altered output. The version is what `plugin update` compares, so
a push without a bump may not reach anyone.

**The kit is copied into each editor's pipeline, not symlinked.** A plugin update refreshes
their *cache*; the folder they actually build in is only updated when `setup.py` runs. Since
5.2.0 `install.ps1` runs it for them, so re-pasting the install line is the whole update —
they do not have to remember `/reel-factory:reel-setup`. Two halves, deliberately different:

- **`kit/state` → `_state` is force-refreshed.** Engine code, meme catalog, SFX map,
  sticker kit, brand bible, learnings. Nobody customises these; what happens instead is
  drift, and a machine on a six-week-old catalog quietly builds worse videos than the one
  beside it while reporting itself up to date.
- **The banks are additive.** New memes, logos and SFX land; anything the editor added or
  changed is left alone. `--force` is the only way to overwrite one of theirs.

### Before you push: check for drift

Fixes get made in the live pipeline first — mid-build, straight into `_state/`. Nothing
carries them back here, and nothing announces when the two have parted. By 5.2.0 the gap
had reached six engine modules, five scripts and three learning files.

```bash
python tools/sync_from_pipeline.py
```

Report only. `--apply` copies live → plugin; review the diff before committing. Run it as
the first step of every release, not the last.

## What is deliberately NOT in here

- **CapCut's effect cache** — the Markerist font, the torn-paper effect, the caption
  assets. Machine-local, downloaded by CapCut itself. No kit can ship these; opening
  `CZ_TEMPLATE` once while online is the only way, and it is the one manual step.
- **`paths.json`** — machine-specific, regenerated by the doctor, gitignored.
- **`crypto_key_store.dat`** — machine-bound, gitignored, CapCut regenerates it.

## This repo is public and names her

That was a deliberate call. Everything here is world-readable: the spec, the placement
laws, the template, the brand assets, and the accumulated learnings — which quote her
hand-written notes and record how she thinks about edits.

If that ever stops being what you want, the split is: keep `scripts/` and the plugin
scaffolding public, move `kit/` and `skills/reel-factory/reference/` to a private repo,
and have `/reel-factory:reel-setup` pull the kit from there. The install stays two commands.

## When an editor is stuck

Almost every failure is one of these, in rough order of likelihood:

1. **"CapCut drafts folder not found", on Linux paths like `/root/...`.** They are running
   it in a cloud/web Claude Code session, not on their editing machine. CapCut has no Linux
   version and the container is discarded at session end. Setup now refuses up front rather
   than unpacking the kit first. Tell them to install Claude Code on the Windows machine
   where they edit and run it there.
2. **`claude: command not found`, or `/plugin isn't available in this environment`.** They
   are trying to install from the Claude desktop app. It cannot do it — no `claude` CLI, and
   `/plugin` is not offered there either. There is no app-only route. They must install
   Node, then `npm install -g @anthropic-ai/claude-code`, and add the marketplace from
   PowerShell. Node is needed for `capcut-cli` anyway, so nothing is wasted.
3. **"How do I edit in PowerShell?"** They think the terminal replaced CapCut. It did not
   - it replaced the chat window. They still edit in CapCut; Claude just builds the draft
   first. Expect this question from everyone; the README's "How this works day to day"
   table answers it.
4. **`run it <name>` goes hunting in Notion, Drive or the web instead of building.**
   Almost always: the plugin IS installed and loaded, but they never ran
   `/reel-factory:reel-setup`, so no pipeline folder exists and nothing looks like a video
   to match. Have them run setup, then the CapCut template step, then try again. Check
   `claude plugin list` only to rule the plugin out - if reel-factory is missing the
   installer did not finish; if it is listed but its commands do not appear, they must
   fully QUIT Claude Code and reopen, since plugins load only at startup.

   If setup HAS been run and the video IS in 01_intake, the skill simply failed to
   trigger - a competing reading won. This is likeliest when the editor has Notion or
   Drive connected AND the video name reads like a document or a company ("emergent
   analyse stocks" lost to a stocks-research interpretation on a real machine). Tell them
   to use the explicit `/reel-factory:reel-run <name>` command, which leaves nothing to
   interpretation, and to update for the sharpened skill description (v4.5.0+).
5. **`Unknown command`.** Two causes, both cosmetic. Either they typed `/reel-setup`
   instead of `/reel-factory:reel-setup` — every command is namespaced by the plugin — or
   they have not restarted Claude Code since installing. Plugins load once at startup, and
   resuming the same conversation does not reload them; it must be a new session.
6. **`API Error: Connection refused - a firewall or proxy may be blocking it`.** This is
   Claude Code failing to reach Anthropic, not the pipeline. Reinstalling and re-running do
   nothing. **Ask about a VPN first** - this team uses VPNs for CapCut in regions where it
   is blocked, and one that routes or blocks `api.anthropic.com` produces exactly this.
   Have them disable it, or enable it only while CapCut is open and never during a build.
   Then consider corporate/school firewalls and antivirus doing HTTPS inspection. To
   confirm, at the POWERSHELL prompt with Claude closed:
   `curl.exe -s -o NUL -w "%{http_code}" https://api.anthropic.com/v1/models`
7. **Stage 1 stalls, then reports a connection error, but the network is fine.** The
   Whisper weights (~500MB) are downloading inside a tool call and exceeding its timeout.
   Confirm with `curl` that huggingface.co answers - it usually does, which is what makes
   this read as a mystery. Fix: have them close Claude and run the download from the
   POWERSHELL prompt, where nothing times out:
   `python -c "from faster_whisper import WhisperModel; WhisperModel('small.en', device='cpu', compute_type='int8')"`
   Then re-run the build. Setups from v4.6.0 onward pre-download this, so it should only
   affect editors who set up before then. **Do not let the agent substitute a smaller
   model to get past it** - that changes the transcript the entire build is anchored to.
8. **CapCut was open during a write.** The single most common cause of a broken draft.
   Have them close it and run `python _state/post_session_fix.py "<draft folder>"`.
9. **The install failed on SSH.** `README.md` step one — the `insteadOf` line. Claude Code
   clones plugins over SSH even for a public repo, and a machine with no GitHub key fails
   with "Host key verification failed".
10. **A font is missing or misnamed.** Both fonts ship and install automatically, so this
   should be rare - re-running the installer line fixes it. Awelier must end up registered
   as `MADE Awelier PERSONAL USE ...`; if it registered under its FILENAME instead
   (`MADEAwelierPERSONALUSE-Bold`), CapCut will not find the family and the title renders
   wrong. `kit/fonts/fontnames.json` is what prevents that.
11. **The template was never opened in CapCut.** Everything builds, nothing renders styled.
12. **Tenor stopped returning memes.** `python _state/tenor_fetch.py --selftest` says which
   link in the chain broke.

`python _state/doctor.py` catches 1, 8, 10 and 11 outright. It checks the kit, not connectivity, so it catches none of the network failures. Ask for its full output before
theorising.

## The thing worth protecting

`scripts/house_layout.py`. Every constant in it was measured off a draft Cindy finished by
hand — the 430px meme height, the 0.832 top edge, the 1015px card width, the 78px label
strip. That file is the difference between output that looks like hers and output that
looks like a robot's.

When a lesson turns out to be a law, it belongs there or in `verify_build.py`, not only in
a learnings file. A law in a learnings file gets missed; a law in `house_layout.py` cannot
be, and a law in `verify_build.py` can never ship broken silently.
