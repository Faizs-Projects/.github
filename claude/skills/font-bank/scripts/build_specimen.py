#!/usr/bin/env python3
"""Write specimen/index.html from bank/bank.json."""

import html
import sys
from pathlib import Path

from banklib import ROOT, families_by_id, load, stack

SPECIMEN = ROOT / "specimen" / "index.html"


def face_css(family):
    filename = family["file"].rsplit("/", 1)[-1]
    return "\n".join(
        [
            "@font-face {",
            f"  font-family: \"{family['family']}\";",
            f"  src: url(\"../bank/files/{filename}\") format(\"woff2\");",
            f"  font-weight: {family['weightMin']} {family['weightMax']};",
            "  font-style: normal;",
            "  font-display: swap;",
            "}",
        ]
    )


def render(bank):
    families = families_by_id(bank)
    faces = "\n\n".join(face_css(family) for family in bank["families"])
    articles = []
    for pairing in bank["pairings"]:
        display = families[pairing["display"]]
        body = families[pairing["body"]]
        scale = pairing["scale"]
        industries = ", ".join(pairing["industries"])
        used = ""
        if pairing.get("usedOn"):
            used = f'  <p class="used">Used on {html.escape(pairing["usedOn"])}.</p>'
        files = html.escape(display["file"])
        if body["id"] != display["id"]:
            files += " and " + html.escape(body["file"])
        style = (
            f"--display: {stack(display)}; --body: {stack(body)}; "
            f"--size: {scale['displaySize']}; --lh: {scale['displayLineHeight']}; "
            f"--track: {scale['displayTracking']}; --wght: {scale['displayWeight']};"
        )
        articles.append(
            "\n".join(
                [
                    "<article",
                    f'  id="{html.escape(pairing["id"])}"',
                    f'  style="{html.escape(style, quote=True)}"',
                    ">",
                    f'  <p class="industries">{html.escape(industries)}</p>',
                    f"  <h2>{html.escape(pairing['name'])}</h2>",
                    f'  <p class="display">{html.escape(pairing["sampleDisplay"])}</p>',
                    f'  <p class="read">{html.escape(pairing["sampleBody"])}</p>',
                    f'  <p class="why">{html.escape(pairing["why"])}</p>',
                    *([used] if used else []),
                    '  <dl class="facts">',
                    f'    <div><dt>Display</dt><dd>{html.escape(display["family"])} {display["weightMin"]}–{display["weightMax"]}</dd></div>',
                    f'    <div><dt>Body</dt><dd>{html.escape(body["family"])} {body["weightMin"]}–{body["weightMax"]}</dd></div>',
                    f"    <div><dt>Files</dt><dd>{files}</dd></div>",
                    "    <div><dt>License</dt><dd>OFL-1.1, weight axis only</dd></div>",
                    "  </dl>",
                    "</article>",
                ]
            )
        )
    avoid_rows = []
    for row in bank["avoid"]:
        names = ", ".join(row["families"])
        avoid_rows.append(
            f"<li><strong>{html.escape(names)}.</strong> {html.escape(row['why'])}</li>"
        )
    chrome_display = stack(families["newsreader"])
    chrome_body = stack(families["figtree"])
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Font bank</title>
  <style>
    {faces}

    :root {{
      --paper: #f3efe6;
      --ink: #1c1612;
      --muted: #5c5148;
      --rule: rgba(28, 22, 18, 0.16);
      --chrome-display: {chrome_display};
      --chrome-body: {chrome_body};
    }}

    * {{ box-sizing: border-box; }}

    body {{
      margin: 0;
      background: var(--paper);
      color: var(--ink);
      font-family: var(--chrome-body);
      font-size: 1.0625rem;
      line-height: 1.5;
      letter-spacing: 0;
    }}

    header, main, .avoid {{
      width: min(880px, calc(100% - 40px));
      margin-inline: auto;
    }}

    header {{
      padding: 64px 0 24px;
    }}

    .kicker {{
      margin: 0 0 12px;
      font-size: 0.75rem;
      font-weight: 650;
      letter-spacing: 0.16em;
      text-transform: uppercase;
      color: var(--muted);
    }}

    h1 {{
      margin: 0;
      font-family: var(--chrome-display);
      font-weight: 520;
      font-size: clamp(3rem, 8vw, 5.5rem);
      line-height: 0.92;
      letter-spacing: -0.03em;
      font-synthesis: none;
    }}

    .lede {{
      max-width: 38rem;
      margin: 20px 0 0;
      color: var(--muted);
    }}

    article {{
      padding: 40px 0;
      border-top: 1px solid var(--rule);
    }}

    .industries {{
      margin: 0 0 8px;
      font-size: 0.75rem;
      font-weight: 650;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      color: var(--muted);
    }}

    h2, .display {{
      font-family: var(--display);
      font-weight: var(--wght);
      letter-spacing: var(--track);
      line-height: var(--lh);
      font-synthesis: none;
    }}

    h2 {{
      margin: 0;
      font-size: clamp(1.6rem, 3vw, 2rem);
    }}

    .display {{
      margin: 20px 0 0;
      font-size: var(--size);
    }}

    .read {{
      max-width: 36rem;
      margin: 20px 0 0;
      font-family: var(--body);
      font-weight: 400;
      font-size: 1.0625rem;
      line-height: 1.5;
    }}

    .why, .used {{
      max-width: 38rem;
      margin: 16px 0 0;
      color: var(--muted);
    }}

    .facts {{
      display: grid;
      gap: 8px 24px;
      margin: 24px 0 0;
    }}

    .facts div {{
      display: grid;
      grid-template-columns: 6.5rem 1fr;
      gap: 12px;
    }}

    dt {{
      margin: 0;
      color: var(--muted);
    }}

    dd {{
      margin: 0;
    }}

    .avoid {{
      padding: 40px 0 80px;
      border-top: 1px solid var(--rule);
    }}

    .avoid h2 {{
      margin: 0 0 12px;
      font-family: var(--chrome-display);
      font-weight: 560;
      font-size: clamp(2rem, 4vw, 2.75rem);
      letter-spacing: -0.02em;
      line-height: 1;
    }}

    .avoid ul {{
      margin: 16px 0 0;
      padding: 0;
      list-style: none;
    }}

    .avoid li {{
      max-width: 38rem;
      margin-top: 14px;
    }}
  </style>
</head>
<body>
  <header>
    <p class="kicker">Cool half</p>
    <h1>Font bank</h1>
    <p class="lede">{html.escape(bank["note"])}</p>
  </header>
  <main>
    {chr(10).join(articles)}
  </main>
  <section class="avoid" id="avoid">
    <h2>Leave these out</h2>
    <p class="lede">These are the other half. They are named so a page does not reach for them. The files are not in the bank.</p>
    <ul>
      {chr(10).join(avoid_rows)}
    </ul>
  </section>
</body>
</html>
"""


def main():
    bank = load()
    SPECIMEN.parent.mkdir(parents=True, exist_ok=True)
    SPECIMEN.write_text(render(bank))
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    raise SystemExit(main())
