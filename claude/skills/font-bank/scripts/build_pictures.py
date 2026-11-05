#!/usr/bin/env python3
"""Draw a sentence picture for every pairing.

Each PNG is the bank card: the occasion, the sentence in the display face,
and the second line in the body face. Fonts are the OFL files already in
bank/files.
"""

import sys
import tempfile
from pathlib import Path

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

from banklib import ROOT, families_by_id, load

PICTURES = ROOT / "bank" / "pictures"
LABEL_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
PAPER = (243, 239, 230)
INK = (28, 22, 18)
MUTED = (92, 81, 72)
CONTENT = 1100
PAD = 56


def load_face(family, size, weight):
    source = ROOT / "bank" / family["file"]
    font = TTFont(source)
    font.flavor = None
    handle = tempfile.NamedTemporaryFile(suffix=".ttf", delete=False)
    font.save(handle)
    handle.close()
    face = ImageFont.truetype(handle.name, size)
    if "fvar" in font and hasattr(face, "set_variation_by_axes"):
        values = []
        for axis in font["fvar"].axes:
            if axis.axisTag == "wght":
                values.append(float(max(axis.minValue, min(axis.maxValue, weight))))
            else:
                values.append(float(axis.defaultValue))
        face.set_variation_by_axes(values)
    return face, handle.name


def wrap(text, face, width):
    lines = []
    current = ""
    for word in text.split():
        trial = word if not current else current + " " + word
        if face.getlength(trial) <= width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [""]


def line_box(face, text):
    box = face.getbbox(text)
    return box[0], box[1], box[2], box[3]


def draw_pairing(pairing, families):
    display = families[pairing["display"]]
    body = families[pairing["body"]]
    size = int(pairing.get("pictureSize", 96))
    temps = []
    try:
        while size >= 28:
            body_size = max(22, int(size * 0.32))
            display_face, display_tmp = load_face(display, size, pairing["scale"]["displayWeight"])
            body_face, body_tmp = load_face(body, body_size, pairing["scale"]["bodyWeight"])
            temps.extend([display_tmp, body_tmp])
            display_lines = wrap(pairing["sampleDisplay"], display_face, CONTENT)
            body_lines = wrap(pairing["sampleBody"], body_face, CONTENT)
            too_wide = any(line_box(display_face, line)[2] - line_box(display_face, line)[0] > CONTENT for line in display_lines)
            too_wide = too_wide or any(
                line_box(body_face, line)[2] - line_box(body_face, line)[0] > CONTENT for line in body_lines
            )
            if not too_wide:
                break
            size -= 4
        label_face = ImageFont.truetype(LABEL_FONT, 22)
        label = f"{pairing['occasion']}  ·  {display['family']}"
        blocks = [("label", label_face, [label], MUTED)]
        blocks.append(("gap", None, [""], INK))
        blocks.append(("text", display_face, display_lines, INK))
        blocks.append(("gap", None, [""], INK))
        blocks.append(("text", body_face, body_lines, INK))

        measured = []
        cursor = PAD
        for kind, face, lines, fill in blocks:
            if kind == "gap":
                cursor += 18
                measured.append((kind, None, [], fill, cursor))
                continue
            drawn = []
            for line in lines:
                left, top, right, bottom = line_box(face, line)
                drawn.append((line, left, top, right, bottom))
                cursor += (bottom - top) + 8
            measured.append((kind, face, drawn, fill, cursor))
        height = cursor + PAD
        image = Image.new("RGB", (CONTENT + PAD * 2, height), PAPER)
        draw = ImageDraw.Draw(image)
        y = PAD
        for kind, face, drawn, fill, _end in measured:
            if kind == "gap":
                y += 18
                continue
            for line, left, top, right, bottom in drawn:
                draw.text((PAD - min(0, left), y - top), line, font=face, fill=fill)
                y += (bottom - top) + 8
        out = PICTURES / f"{pairing['id']}.png"
        image.save(out, "PNG")
        return out
    finally:
        for path in temps:
            Path(path).unlink(missing_ok=True)


def main():
    bank = load()
    families = families_by_id(bank)
    PICTURES.mkdir(parents=True, exist_ok=True)
    for pairing in bank["pairings"]:
        path = draw_pairing(pairing, families)
        print(f"{pairing['id']} {path.stat().st_size}")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    raise SystemExit(main())
