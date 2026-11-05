#!/usr/bin/env python3
"""Print font-bank pairings as one JSON object.

Examples:
  python3 list_pairings.py
  python3 list_pairings.py restaurant
  python3 list_pairings.py --occasion thick
  python3 list_pairings.py --id counter-poster
  python3 list_pairings.py --half avoid
"""

import argparse
import json
import sys

from banklib import families_by_id, load, normalize_industry


def attach(pairing, families):
    row = dict(pairing)
    row["displayFamily"] = families[pairing["display"]]
    row["bodyFamily"] = families[pairing["body"]]
    return row


def main(argv):
    parser = argparse.ArgumentParser(description="List font-bank pairings.")
    parser.add_argument("industry", nargs="?", help="restaurant, cafe, bar, bakery, dentist, lawyer, trade")
    parser.add_argument("--id", dest="pairing_id", help="One pairing id")
    parser.add_argument("--occasion", help="high-end, chill, local, thick, thin, sharp, soft, bubble, small")
    parser.add_argument("--half", choices=("cool", "avoid"), default="cool")
    args = parser.parse_args(argv)

    bank = load()
    families = families_by_id(bank)

    if args.half == "avoid":
        payload = {"ok": True, "half": "avoid", "avoid": bank["avoid"]}
        json.dump(payload, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0

    rows = bank["pairings"]
    industry = None
    occasion = None
    if args.pairing_id:
        rows = [row for row in rows if row["id"] == args.pairing_id]
        if not rows:
            payload = {"ok": False, "error": f"No pairing named {args.pairing_id}."}
            json.dump(payload, sys.stdout, indent=2)
            sys.stdout.write("\n")
            return 1
    else:
        if args.industry:
            industry = normalize_industry(args.industry)
            rows = [
                row
                for row in rows
                if industry in {normalize_industry(name) for name in row["industries"]}
            ]
        if args.occasion:
            occasion = normalize_industry(args.occasion)
            rows = [
                row
                for row in rows
                if normalize_industry(row.get("occasion", "")) == occasion
            ]

    payload = {
        "ok": True,
        "half": "cool",
        "industry": industry,
        "occasion": occasion,
        "pairings": [attach(row, families) for row in rows],
    }
    if (industry or occasion) and not rows:
        payload["note"] = (
            "Nothing in the bank matches that industry or occasion. "
            "Say so. Do not fill the gap with a face from the avoid list."
        )
        payload["avoid"] = bank["avoid"]
    json.dump(payload, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
    raise SystemExit(main(sys.argv[1:]))
