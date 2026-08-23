---
description: Capture what the editor changed by hand after a delivery, into the learnings
argument-hint: "[what you changed, or leave blank to be asked]"
---

Capture what the editor changed by hand so the next build starts closer.

This is the loop that makes the tool improve. Run it after a delivery, once they have
opened the draft in CapCut and fixed things.

## 1. Ask, if they have not already said

If `$ARGUMENTS` is empty, ask — briefly, and about specifics rather than in general:

- What did you move, resize or delete?
- Anything that landed in the wrong place, or covered your face or the mic?
- Any meme that did not fit the beat?
- Anything you had to type in by hand?
- Anything that was simply wrong?

One round. Do not interrogate them.

## 2. Work out WHY, not just what

A learning that records the change is nearly useless; a learning that records the rule
behind it is what stops the mistake recurring.

- "moved the card up 60px" → *why* — it was covering the mic at this framing.
- "swapped the meme at 12s" → *why* — it matched the keyword, not the beat's subtext.

If the why is not clear from what they said, ask that one follow-up. If a number is
involved, **measure it off the draft** rather than accepting an estimate — the placement
laws in `house_layout.py` are only trustworthy because every constant in them was read
off a real finished edit.

## 3. Write the entry

Append to `_state/learnings/<YYYY-MM-DD>-<topic>.md`:

```markdown
## <date> — <what round this was>

- **<the rule, stated as a rule>** — what happened, the measured numbers, and the fix.
```

Dated, append-only, one file per round. Never rewrite an old entry: a wrong lesson that
was later corrected is itself worth keeping.

## 4. Promote anything durable

If the lesson is a *law* rather than a one-off — a measurement, a placement rule, a hard
ban — then also:

- add or correct the constant in `_state/house_layout.py`, with a comment saying it was
  measured, and from which draft;
- add the check to `_state/verify_build.py` so it can never ship again silently;
- update the relevant `reference/*.md`.

A law that lives only in a learnings file will be missed. A law encoded in
`house_layout.py` or `verify_build.py` cannot be.

## 5. Say what you changed

Tell the editor which files you touched and what the next build will now do differently.

**These learnings stay local to this machine by default.** If it is a law the whole team
should have, say so explicitly and let them decide whether to push it to the shared repo
— four editors' preferences silently colliding in one file helps nobody.
