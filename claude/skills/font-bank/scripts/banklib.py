"""Shared reads for the font bank."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK_PATH = ROOT / "bank" / "bank.json"


def load():
    return json.loads(BANK_PATH.read_text())


def families_by_id(bank):
    return {family["id"]: family for family in bank["families"]}


def css_name(family_name):
    return '"' + family_name.replace('"', "") + '"'


def stack(family):
    return css_name(family["family"]) + ", " + family["fallback"]


def normalize_industry(value):
    return value.strip().lower().replace("_", "-").replace(" ", "-")
