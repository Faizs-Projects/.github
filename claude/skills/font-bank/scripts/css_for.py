#!/usr/bin/env python3
"""Print the @font-face block and the type scale for one pairing.

Copy the named .woff2 files and their license files next to the CSS.
"""

import argparse
import sys

from banklib import families_by_id, load, stack, weight_css


def render(pairing, families):
    display = families[pairing["display"]]
    body = families[pairing["body"]]
    scale = pairing["scale"]
    blocks = []
    seen = set()
    for family in (display, body):
        if family["id"] in seen:
            continue
        seen.add(family["id"])
        filename = family["file"].rsplit("/", 1)[-1]
        blocks.append(
            "\n".join(
                [
                    "@font-face {",
                    f"  font-family: \"{family['family']}\";",
                    f"  src: url(\"{filename}\") format(\"woff2\");",
                    f"  font-weight: {weight_css(family)};",
                    "  font-style: normal;",
                    "  font-display: swap;",
                    "}",
                ]
            )
        )
    files = []
    for family in (display, body):
        filename = family["file"].rsplit("/", 1)[-1]
        license_name = family["licenseFile"].rsplit("/", 1)[-1]
        files.append(f"{filename} ({license_name}, {family['license']}, {family['copyright']})")
    header = [
        f"/* {pairing['name']} — {pairing['id']}",
        "   Copy these files next to this CSS:",
    ]
    header.extend(f"   - {line}" for line in files)
    header.append("   OFL-1.1, free for paid client work. Keep the license file with the font.")
    header.append("   Variable files are the weight axis only. Do not set opsz, ital, SOFT, WONK, or wdth.")
    header.append("*/")
    rules = "\n\n".join(blocks)
    usage = "\n".join(
        [
            ":root {",
            f"  --font-display: {stack(display)};",
            f"  --font-body: {stack(body)};",
            "}",
            "",
            "h1, h2, h3 {",
            "  font-family: var(--font-display);",
            f"  font-weight: {scale['displayWeight']};",
            f"  font-size: {scale['displaySize']};",
            f"  line-height: {scale['displayLineHeight']};",
            f"  letter-spacing: {scale['displayTracking']};",
            "  font-synthesis: none;",
            "}",
            "",
            "body {",
            "  font-family: var(--font-body);",
            f"  font-weight: {scale['bodyWeight']};",
            f"  font-size: {scale['bodySize']};",
            f"  line-height: {scale['bodyLineHeight']};",
            f"  letter-spacing: {scale['bodyTracking']};",
            "}",
        ]
    )
    return "\n".join(header) + "\n\n" + rules + "\n\n" + usage + "\n"


def main(argv):
    parser = argparse.ArgumentParser(description="Print CSS for one font-bank pairing.")
    parser.add_argument("pairing_id")
    args = parser.parse_args(argv)
    bank = load()
    families = families_by_id(bank)
    match = next((row for row in bank["pairings"] if row["id"] == args.pairing_id), None)
    if match is None:
        sys.stderr.write(f"No pairing named {args.pairing_id}.\n")
        return 1
    sys.stdout.write(render(match, families))
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
    raise SystemExit(main(sys.argv[1:]))
