# Worked examples

Read these before writing your first spec. They are not runnable on your machine — the
source videos are not in the kit — but they are the real files two shipped reels were
built from, comments and all.

| | |
|---|---|
| `example_spec.json` | An annotated spec showing every field the validator accepts. Start here. |
| `ai_sandwich/spec.json` | A complete real spec: 29 beats, 12 cards, the title replacement map, the SFX schedule. Note the `_why` keys — the engine ignores them, and they are the reason a later reader can tell a deliberate choice from an accident. |
| `ai_sandwich/make_cards.py` | The companion card-drawing script: 12 cards with Pillow, plus the gutter assertion that fails the script rather than shipping a card whose text touches its edge. |

Two things to take from the pair:

**The spec carries choices, never geometry.** There is no `x`, `y` or `scale` anywhere in
`ai_sandwich/spec.json` — the validator would reject it. Bands, clause timings, which
asset and which words; the engine solves the rest from the artefacts on every build.

**Cards are drawn by a script that checks itself.** `make_cards.py` writes a
`.regions.json` beside every PNG naming the areas a mark can be fitted to. That is what
lets an annotation say "circle the score" instead of naming a coordinate that goes stale
the moment the card is redrawn.
