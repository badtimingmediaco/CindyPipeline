# Drawing cards and graphics yourself

> Part of the Cindy Zhu Reel Factory spec (v3.0). Loaded on demand by the
> `reel-factory` skill - see SKILL.md for the routing table.

**Claude draws every fabricated asset in this build, with Pillow.** There is no
image-generation module: no OpenAI, no ChatGPT, no Remotion, no Hyperframes. Those may
return in a later version; today, reaching for one is out of scope.

This file exists because two rounds were spent learning what does NOT work here. Read
the failures before the recipe - they are the reason the recipe is shaped this way.

---

## 1. THE HARVEST LADDER — fabricate last, not first

For every beat that needs a visual, work down this ladder and stop at the first rung
that yields something real. Fabricating is rung 3, not rung 1.

1. **The owner's own assets** — a screenshot, export or recording they already have.
   Always the strongest, always first.
2. **A real public capture** — headless-Chrome screenshot of the tool's own public page,
   optionally given a slow push-in to read as a recording. Real UI beats drawn UI.
3. **A house-style card you draw** — the content rendered in her brand, per §3 below.
   For prompts, replies, formulas and specs this is not a fallback at all: her own reels
   render Claude prompts as styled message cards rather than UI screenshots, so a card
   *is* the on-brand fulfilment of that beat.
4. **A placeholder card** telling the owner exactly what to record — only for a beat that
   genuinely needs their logged-in session.

A build that ships nothing for the owner to record is the goal. A build that is all
placeholders has skipped the ladder.

## 2. WHAT WAS REJECTED, AND WHY IT MATTERS

Two full rounds of "replace the memes with better graphics" were rejected outright:

- **Remotion-rendered UI mocks** — React components rendered to MP4, invented windows,
  invented cursors, invented dashboards. Verdict: *"very mid."*
- **Generated art cards + a manual asset-request loop** — Claude listing every beat that
  needed art, the owner generating each image elsewhere and dropping them in a folder.
  Verdict: *"super bad … remove this process entirely from future runs."*

Read this correctly. **It is not "the owner dislikes screenshots or graphics"** — her own
hand-finished edits are full of both. What failed was *the automation choosing that
direction by itself* and filling a reel with invented interfaces. Invented UI reads as
fake, and fake is worse than a meme.

**So: never invent a user interface.** Draw content — prompts, replies, lists, numbers,
labels, diagrams — in her brand. Do not draw a fake app window around it.

**Before rebuilding a reel whose visual direction was rejected, ASK what the target
should look like.** Two rounds were spent inferring it and both missed.

## 3. THE RECIPE

Every fabricated card:

- **Renders at ~1015px wide**, the house centre-band width, so displayed scale stays near
  1:1 and the type stays readable at phone size. A 1440-wide capture shrinks to 0.59x and
  becomes unreadable — crop or render to ~1000–1100px wide, never wider.
- **Ends with a 78px transparent strip at the bottom.** The pairing law puts the paper
  label *across* the asset's bottom edge, so any card whose content runs to its own edge
  loses its last row underneath the label. Fix it at the source, in the render — not by
  nudging the label afterwards. Real captures get the same treatment: crop to include
  whitespace under the content.
- **Uses her palette** — cream `#faf7f2`, coral `#e8856a`, ink for body text.
- **Is measured with PIL before placement**, against the material's real `font.ttf`
  (path in `content.styles[0].font.path`). Do not estimate widths; see `01-layout.md`
  for the calibration constants.

Placement comes from `_state/house_layout.py` — `card_geom()` for the centre band,
`meme_geom()` for the top band. Never hand-type a scale or a transform.

## 4. NUMBERS AND BRANDS

**Fake the numbers, never the brand.** Invented view counts, follower counts, percentages
and timings are fine and expected — the owner's explicit call. The *identity* on screen
must be real: real product names, real handles, her real palette. A card showing a
plausible-but-invented 1.2M views on a real channel is right; a card showing a
made-up product or a competitor's logo you drew from memory is not.

## 5. MOTION

- Cards on screen **longer than ~1.5s** may take a slow push-in so they do not read as
  frozen. `ffmpeg zoompan`, on the order of `z='1.0+0.0002*on'` — barely perceptible.
- **Under ~1.5s, stay still.** Motion on a flash cut reads as a wobble.
- Motion is optional polish. A static card is never wrong; a wobbling one is.

## 6. VERIFY AT FULL RESOLUTION

Judge every card against a **1080x1920 composite**, never a contact sheet. Downscaled
preview tiles caused three correctly-centred cards to be reported as off-frame and
"bleeding off the edge" when every one of them sat at x=0.000.

**Verify layout numerically, or at full resolution. Never by eye from a thumbnail.**
