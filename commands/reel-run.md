---
description: Build a reel from a video in 01_intake
argument-hint: "[video name — partial and misspelled is fine]"
---

Build a reel from `$ARGUMENTS`.

Plain **"run it &lt;name&gt;"** in conversation does the same thing — this command exists so
the editor has something to discover in the menu.

## 1. Resolve which file they mean

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/resolve_input.py" "$ARGUMENTS"
```

- **MATCH** → say which file you picked, then continue.
- **AMBIGUOUS** → show the candidates and **ask**. Never pick the newest and hope; a
  wrong guess costs an hour of build time.
- **No files** → tell them the intake folder is empty.

## 2. Run the pipeline

Follow the `reel-factory` skill. Stages 0 through 5, in order, loading each reference
file as that stage needs it. The stage table is in the skill; the detail is in
`reference/05-pipeline.md`.

Non-negotiables while building — these are in the skill too, repeated because they are
the ones that ruin a build:

- **CapCut closed** for every write. Check the process list first, every time.
- **Never invent an SFX filename.** Bank only.
- **Write the canonical timeline file**, then copy it over the mirror; require
  `diverged: false`.
- **Track-order enforcement is the literal last write.**
- **No captions** — she runs auto-captions herself.
- **Claude draws every fabricated asset with Pillow.** No OpenAI, ChatGPT, Remotion or
  Hyperframes.

## 3. Do not stop until verification is clean

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/verify_build.py" "<draft dir>"
```

Fix every finding and re-run. **Loop until it prints zero failures.** A summary claim is
not evidence — read the printed evidence yourself.

## 4. Hand over

Write `05_output/<name>/NOTES.md` with: the build stats, anything left for the editor to
record, the uncertainty list (what you could not see and they should check first), the
brand-word caption fix list, and the polish checklist.

Then tell them, in the chat, the three things worth checking first.
