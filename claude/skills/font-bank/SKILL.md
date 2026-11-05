---
name: font-bank
description: Pick a self-hosted display and body pairing from the font bank by occasion or industry. Use when the user runs /font-bank, asks for a type pairing, a font for a mood (high end, chill, local, thick, thin, sharp, soft, bubble, small, and the rest), or which fonts can be used on a paid site.
argument-hint: "[industry or pairing id]"
allowed-tools: Read Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/list_pairings.py *) Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/css_for.py *)
---

# Font bank

A bank of self-hosted type pairings, one for each occasion, with a picture of a sentence in that face.

Every face is the SIL Open Font License 1.1. That license allows use on a paid client site, a menu, a sign, and in print. Keep the license file next to the font. Do not sell the font file by itself. Files are roman and Latin. A variable file is the weight axis only. A static file is one weight. Italics are not included. Do not set `opsz`, `ital`, `SOFT`, `WONK`, or `wdth`.

## Start

Read `${CLAUDE_SKILL_DIR}/bank/bank.json` only if you need the raw records. For a pick, run:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/list_pairings.py --occasion thick
python3 ${CLAUDE_SKILL_DIR}/scripts/list_pairings.py restaurant
```

Occasions: `high-end`, `chill`, `local`, `thick`, `thin`, `sharp`, `soft`, `bubble`, `small`, `handwritten`, `technical`, `vintage`, `sport`, `plain`, `signature`, `sit-down`, `editorial`, `night`, `serious`.

The industry argument is `restaurant`, `cafe`, `bar`, `bakery`, `food-truck`, `dentist`, `lawyer`, or `trade`. With no argument the script prints the whole bank.

Show the matching pairings and let the user pick. Each row has the display face, the body face, the reason, the type scale, and `picture`, a PNG of the sentence.

When `pairings` is empty, say this industry has nothing in the bank. Do not fill the gap with Inter, Poppins, Playfair Display, Bebas Neue, Anton, Lilita One, or Montserrat. Those names are in the avoid list:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/list_pairings.py --half avoid
```

## Use a pairing

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/css_for.py counter-poster
```

Copy the `.woff2` files the comment names, and their license files, into the site next to the CSS. The comment is the copyright line. Keep it with the files.

`counter-poster` is the pairing already used on Taco Nazo, Colonia: Darker Grotesque for the poster, Outfit for the menu.

## Specimen

`specimen/index.html` puts the sentence picture next to each pairing. Open it from this folder. After a bank edit:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/build_pictures.py
python3 ${CLAUDE_SKILL_DIR}/scripts/build_specimen.py
```

## Add a face

Only add a face that is free to self-host. Put the woff2 in `bank/files/<id>.woff2` and the full license in `bank/licenses/<id>.txt`. Add the family and one pairing to `bank/bank.json` with `sha256`, `bytes`, weights, a fallback stack, industries, a sample line, and a reason that names the business it fits. Then:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/build_specimen.py
python3 ${CLAUDE_SKILL_DIR}/scripts/test_font_bank.py
```
