# -*- coding: utf-8 -*-
"""Cards for The AI Sandwich, drawn with Pillow in her palette.

The editing guide routes its visuals through ChatGPT prompts and screen captures of
external PDFs. Neither is available: OpenAI is banned by project rule, and the captures
reference sources that are not in this cut's audio. So every visual here is drawn.

House rules (reference/08-cards.md):
  * 1015px wide - the centre-band width, so displayed scale stays near 1:1
  * a 78px TRANSPARENT strip at the bottom, because the pairing law puts the paper label
    across the asset's bottom edge and would otherwise eat the last row
  * her palette; no invented UI chrome, no fake brand
  * one card per spoken clause - a card is a unit of ATTENTION, not of information

Every card emits a region manifest so annotations follow the art instead of being frozen
as float literals against one revision of it.
"""
import json
import os

from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))), "04_assets", "graphics")
os.makedirs(OUT, exist_ok=True)

W = 1015
STRIP = 78
CREAM = (250, 247, 242, 255)
INK = (34, 30, 28, 255)
MUTE = (128, 120, 114, 255)
CORAL = (232, 133, 106, 255)
CORAL_SOFT = (245, 214, 203, 255)
CHAR = (58, 53, 50, 255)
GREEN = (74, 154, 106, 255)
RED = (206, 74, 62, 255)
LINE = (226, 219, 210, 255)

F = os.path.join(os.environ["LOCALAPPDATA"], "Microsoft", "Windows", "Fonts")
REG = {}


def font(weight, size):
    return ImageFont.truetype(os.path.join(F, "Poppins-%s.ttf" % weight), size)


def reg(name, box):
    REG[name] = [round(v) for v in box]
    return box


def card(h, w=W):
    REG.clear()
    im = Image.new("RGBA", (w, h + STRIP), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=34, fill=CREAM)
    reg("card", [0, 0, w, h])
    return im, d


def head(d, text, y=44, colour=INK, size=44, weight="Bold"):
    d.text((56, y), text, font=font(weight, size), fill=colour)
    reg("head", [56, y, 56 + d.textlength(text, font=font(weight, size)), y + size + 8])


def save(im, name):
    body_h = REG["card"][3]
    for k, box in REG.items():
        if k != "card" and box[3] > body_h:
            raise SystemExit(
                "%s: region %r ends at y=%d but the card body ends at %d - it would be "
                "drawn into the 78px label gutter and covered by the paper label."
                % (name, k, box[3], body_h))
    im.save(os.path.join(OUT, "%s.png" % name))
    json.dump(dict(REG), open(os.path.join(OUT, "%s.regions.json" % name), "w",
                              encoding="utf-8"), indent=1, sort_keys=True)
    print("  %-20s %dx%d  (%d regions)" % (name, im.size[0], im.size[1], len(REG)))


def cross(d, cx, cy, col=RED, r=15):
    """Draw the mark, never type it - Poppins has no cross glyph and renders tofu."""
    d.line([(cx - r, cy - r), (cx + r, cy + r)], fill=col, width=7)
    d.line([(cx - r, cy + r), (cx + r, cy - r)], fill=col, width=7)


def tick(d, cx, cy, col=GREEN, r=19):
    d.line([(cx - r, cy), (cx - r * 0.25, cy + r * 0.7)], fill=col, width=7)
    d.line([(cx - r * 0.25, cy + r * 0.7), (cx + r, cy - r * 0.75)], fill=col, width=7)


# ============================== 1. what AI does not get the final say on
im, d = card(430)
head(d, "AI doesn't get the final say on:")
items = ["What actually looks good", "What's true", "What's on brand",
         "What's worth keeping"]
y = 132
for i, t in enumerate(items, 1):
    cross(d, 80, y + 22)
    d.text((124, y), t, font=font("Medium", 36), fill=INK)
    reg("item_%d" % i, [56, y, 124 + d.textlength(t, font=font("Medium", 36)), y + 52])
    y += 72
save(im, "sw_criteria")


# ============================== 2-4. the sandwich decks
def deck(name, title, layers, h, note=None, bar_h=54, gap=12):
    im, d = card(h)
    head(d, title)
    top = 128
    for i, (label, who) in enumerate(layers):
        y = top + i * (bar_h + gap)
        fill = CORAL if who == "you" else CHAR
        d.rounded_rectangle([56, y, W - 56, y + bar_h], radius=max(8, bar_h // 3),
                            fill=fill)
        if label:
            d.text((92, y + bar_h / 2 - 20), label, font=font("SemiBold", 30), fill=CREAM)
        reg("layer_%d" % (i + 1), [56, y, W - 56, y + bar_h])
    if note:
        ny = top + len(layers) * (bar_h + gap) + 8
        d.text((56, ny), note, font=font("SemiBoldItalic", 30), fill=MUTE)
        reg("note", [56, ny, W - 56, ny + 40])
    save(im, name)


deck("sw_deck_2", "The AI Sandwich",
     [("YOU  set the standard", "you"), ("AI  builds", "ai"), ("YOU  check it", "you")],
     400, note="Human on both sides.")
deck("sw_deck_3", "Better: a triple-decker",
     [("YOU", "you"), ("AI", "ai"), ("YOU", "you"), ("AI", "ai"), ("YOU", "you")],
     532, note="Judgment between every pass.")
deck("sw_deck_50", "Or honestly, a 50-decker",
     [("", "you" if i % 2 == 0 else "ai") for i in range(17)],
     645, note="Keep sandwiching yourself in.", bar_h=20, gap=6)


# ============================== 5-8. the loop, one card per clause
def loop_card(name, who, action):
    im, d = card(230)
    badge = CORAL if who == "YOU" else CHAR
    bw = 168
    d.rounded_rectangle([56, 52, 56 + bw, 130], radius=22, fill=badge)
    tw = d.textlength(who, font=font("Bold", 42))
    d.text((56 + (bw - tw) / 2, 66), who, font=font("Bold", 42), fill=CREAM)
    reg("badge", [56, 52, 56 + bw, 130])
    d.text((56 + bw + 34, 60), action, font=font("SemiBold", 44), fill=INK)
    reg("action", [56 + bw + 34, 60,
                   56 + bw + 34 + d.textlength(action, font=font("SemiBold", 44)), 120])
    save(im, name)


loop_card("sw_loop_1", "YOU", "Set the outcome")
loop_card("sw_loop_2", "AI", "Builds")
loop_card("sw_loop_3", "YOU", "Check the work")
loop_card("sw_loop_4", "AI", "Revises")

# ============================== 9. pulling it back on course
im, d = card(390)
head(d, "Pull it back on course")
cy = 236
d.line([(70, cy), (330, cy)], fill=CHAR, width=9)
for i in range(9):                       # the drift, drawn as a dashed climb
    x = 330 + i * 34
    d.line([(x, cy - i * 7), (x + 20, cy - (i + 1) * 7)], fill=MUTE, width=7)
d.text((646, 120), "off course", font=font("MediumItalic", 30), fill=MUTE)
reg("drift", [330, 140, 660, cy])
d.line([(330, cy), (700, cy)], fill=CORAL, width=9)
d.polygon([(700, cy - 20), (742, cy), (700, cy + 20)], fill=CORAL)
d.ellipse([316, cy - 14, 344, cy + 14], fill=CORAL)
reg("correction", [316, cy - 24, 742, cy + 24])
d.text((56, 296), "Your judgment, applied between passes.",
       font=font("Medium", 32), fill=INK)
reg("caption", [56, 296, W - 56, 340])
save(im, "sw_course")

# ============================== 10. eval
im, d = card(300)
head(d, "eval")
DEF = "= a repeatable test"
d.text((56, 118), DEF, font=font("SemiBold", 46), fill=CORAL)
reg("definition", [56, 118, 56 + d.textlength(DEF, font=font("SemiBold", 46)), 176])
d.line([56, 202, W - 56, 202], fill=LINE, width=2)
d.text((56, 220), "Run it again and you get the same answer.",
       font=font("Medium", 30), fill=MUTE)
save(im, "sw_eval")

# ============================== 11. progressive autonomy
im, d = card(400)
head(d, "Progressive autonomy")
d.text((56, 112), "The agent earns more freedom on that task.",
       font=font("Medium", 30), fill=MUTE)
base, top_y, bw2 = 340, 150, 150
for i, (v, lb) in enumerate(zip([0.35, 0.55, 0.75, 1.0],
                                ["pass 1", "pass 2", "pass 3", "pass 4"])):
    x = 90 + i * 215
    h2 = (base - top_y) * v
    col = CORAL if i == 3 else CORAL_SOFT
    d.rounded_rectangle([x, base - h2, x + bw2, base], radius=16, fill=col)
    tw = d.textlength(lb, font=font("Medium", 26))
    d.text((x + (bw2 - tw) / 2, base + 12), lb, font=font("Medium", 26), fill=MUTE)
    reg("bar_%d" % (i + 1), [x, base - h2, x + bw2, base])
save(im, "sw_autonomy")

# ============================== 12. what to keep vs automate
im, d = card(420)
head(d, "What to keep, what to automate")
mid = W // 2
d.line([(mid, 128), (mid, 388)], fill=LINE, width=2)
d.text((56, 132), "Keep human", font=font("Bold", 34), fill=CORAL)
d.text((mid + 40, 132), "Automate", font=font("Bold", 34), fill=CHAR)
for i, t in enumerate(["Taste", "Standards", "Final sign-off"]):
    y = 200 + i * 62
    tick(d, 78, y + 16)
    d.text((116, y), t, font=font("Medium", 32), fill=INK)
    reg("human_%d" % (i + 1), [56, y, mid - 20, y + 44])
for i, t in enumerate(["Drafting", "Reformatting", "Repeatable checks"]):
    y = 200 + i * 62
    d.text((mid + 40, y), t, font=font("Medium", 32), fill=MUTE)
    reg("auto_%d" % (i + 1), [mid + 40, y, W - 56, y + 44])
save(im, "sw_split")

print("\nAll cards carry the 78px label gutter and a region manifest.")
