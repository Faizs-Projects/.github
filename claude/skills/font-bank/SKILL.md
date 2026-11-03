---
name: font-bank
description: Pick a self-hosted display and body pairing from the font bank, or look up the faces to leave out. Use when the user runs /font-bank, asks for a type pairing, a font bank, or which Google Fonts to self-host for a restaurant, cafe, bar, bakery, dentist, lawyer, or trade.
argument-hint: "[industry or pairing id]"
allowed-tools: Read Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/list_pairings.py *) Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/css_for.py *)
---

# Font bank

A bank of self-hosted type pairings, in the same shape as the other banks: a cool half to pick from, and a named list of faces that read as a template.

The files live in this skill. Each face is a roman variable woff2, Latin subset, weight axis only, under the SIL Open Font License. The license file sits next to the font. Italics are not included. Do not set `opsz`, `ital`, `SOFT`, `WONK`, or `wdth` on these files.

## Start

Read `${CLAUDE_SKILL_DIR}/bank/bank.json` only if you need the raw records. For a pick, run:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/list_pairings.py restaurant
```

The argument is the industry: `restaurant`, `cafe`, `bar`, `bakery`, `food-truck`, `dentist`, `lawyer`, or `trade`. With no argument the script prints the whole cool half.

Show two or three pairings from that result and let the user pick. Each row already has the display face, the body face, the reason, and the type scale.

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

`specimen/index.html` sets each pairing in its own files. Open it from this folder. Rebuild it after a bank edit:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/build_specimen.py
```

## Add a face

Only add a face that is free to self-host. Put the woff2 in `bank/files/<id>.woff2` and the full license in `bank/licenses/<id>.txt`. Add the family and one pairing to `bank/bank.json` with `sha256`, `bytes`, weights, a fallback stack, industries, a sample line, and a reason that names the business it fits. Then:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/build_specimen.py
python3 ${CLAUDE_SKILL_DIR}/scripts/test_font_bank.py
```
