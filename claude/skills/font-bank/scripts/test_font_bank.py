#!/usr/bin/env python3
"""Checks for the font bank: files, licenses, pairings, CSS, specimen."""

import hashlib
import html
import json
import unittest

from banklib import BANK_PATH, ROOT, families_by_id, load
from build_specimen import SPECIMEN, render
from css_for import render as render_css
from list_pairings import main as list_main


class FontBankTests(unittest.TestCase):
    def setUp(self):
        self.bank = load()
        self.families = families_by_id(self.bank)

    def test_every_file_matches_its_hash_and_is_woff2(self):
        for family in self.bank["families"]:
            path = ROOT / "bank" / family["file"]
            data = path.read_bytes()
            self.assertEqual(data[:4], b"wOF2", family["id"])
            self.assertEqual(len(data), family["bytes"], family["id"])
            self.assertEqual(hashlib.sha256(data).hexdigest(), family["sha256"], family["id"])
            self.assertTrue(family["axes"] == ["wght"] or family["axes"] == [])
            self.assertEqual(family["license"], "OFL-1.1")
            self.assertEqual(family["style"], "normal")

    def test_every_license_is_the_open_font_license(self):
        for family in self.bank["families"]:
            text = (ROOT / "bank" / family["licenseFile"]).read_text()
            self.assertIn("SIL Open Font License", text, family["id"])
            self.assertTrue(text.startswith(family["copyright"]), family["id"])

    def test_pairings_point_at_real_families(self):
        self.assertGreaterEqual(len(self.bank["pairings"]), 1)
        for pairing in self.bank["pairings"]:
            self.assertEqual(pairing["half"], "cool")
            self.assertIn(pairing["display"], self.families)
            self.assertIn(pairing["body"], self.families)
            self.assertTrue(pairing["why"])
            self.assertTrue(pairing["occasion"])
            self.assertTrue(pairing["picture"])
            self.assertTrue(pairing["industries"])
            scale = pairing["scale"]
            self.assertIn("clamp(", scale["displaySize"])
            self.assertGreater(scale["displayWeight"], 0)

    def test_avoid_list_is_not_shipped_as_a_cool_pairing(self):
        shipped = {family["family"] for family in self.bank["families"]}
        avoided = {name for row in self.bank["avoid"] for name in row["families"]}
        self.assertTrue(avoided)
        self.assertFalse(shipped & avoided)

    def test_restaurant_returns_three_cool_pairings(self):
        payload = self._list(["restaurant"])
        ids = [row["id"] for row in payload["pairings"]]
        self.assertEqual(ids[:3], ["counter-poster", "dining-room", "menu-editorial"])
        self.assertIn("displayFamily", payload["pairings"][0])
        self.assertEqual(payload["pairings"][0]["displayFamily"]["family"], "Darker Grotesque")

    def test_dentist_returns_the_practice_pairing(self):
        payload = self._list(["lawyer"])
        ids = [row["id"] for row in payload["pairings"]]
        self.assertIn("practice", ids)
        self.assertIn("small", ids)

    def test_unknown_industry_stays_empty(self):
        payload = self._list(["aquarium"])
        self.assertEqual(payload["pairings"], [])
        self.assertIn("avoid", payload)
        self.assertTrue(payload["note"])

    def test_one_pairing_by_id(self):
        payload = self._list(["--id", "night-sign"])
        self.assertEqual(len(payload["pairings"]), 1)
        self.assertEqual(payload["pairings"][0]["displayFamily"]["family"], "Syne")

    def test_missing_id_fails(self):
        payload = self._list(["--id", "not-a-pairing"], expect=1)
        self.assertFalse(payload["ok"])

    def test_css_names_the_files_and_the_scale(self):
        pairing = next(row for row in self.bank["pairings"] if row["id"] == "counter-poster")
        css = render_css(pairing, self.families)
        self.assertIn('font-family: "Darker Grotesque"', css)
        self.assertIn('url("darker-grotesque.woff2")', css)
        self.assertIn('url("outfit.woff2")', css)
        self.assertIn("clamp(3.4rem, 8vw, 6.25rem)", css)
        self.assertIn("OFL-1.1", css)
        self.assertIn("Do not set opsz", css)
        self.assertNotIn("font-variation-settings", css)

    def test_requested_occasions_are_in_the_bank(self):
        found = {pairing["occasion"] for pairing in self.bank["pairings"]}
        for occasion in (
            "high-end",
            "chill",
            "local",
            "thick",
            "thin",
            "sharp",
            "soft",
            "bubble",
            "small",
        ):
            self.assertIn(occasion, found)
        payload = self._list(["--occasion", "bubble"])
        self.assertEqual([row["id"] for row in payload["pairings"]], ["bubble"])
        self.assertEqual(payload["pairings"][0]["displayFamily"]["license"], "OFL-1.1")

    def test_food_truck_with_a_space_matches(self):
        payload = self._list(["food truck"])
        self.assertEqual([row["id"] for row in payload["pairings"]], ["counter-poster"])

    def test_specimen_is_what_the_builder_writes(self):
        self.assertEqual(SPECIMEN.read_text(), render(self.bank))
        text = SPECIMEN.read_text()
        self.assertEqual(text.count("<h1>"), 1)
        for pairing in self.bank["pairings"]:
            self.assertIn(f'id="{pairing["id"]}"', text)
            self.assertIn(html.escape(pairing["sampleDisplay"]), text)
            self.assertIn(f'../bank/{pairing["picture"]}', text)
            picture = ROOT / "bank" / pairing["picture"]
            self.assertEqual(picture.read_bytes()[:8], b"\x89PNG\r\n\x1a\n", pairing["id"])
            self.assertGreater(picture.stat().st_size, 4000, pairing["id"])
        for family in self.bank["families"]:
            self.assertIn(f'url("../bank/files/{family["id"]}.woff2")', text)
        self.assertIn("Leave these out", text)
        self.assertTrue(BANK_PATH.is_file())

    def _list(self, argv, expect=0):
        from io import StringIO
        from contextlib import redirect_stdout

        buf = StringIO()
        with redirect_stdout(buf):
            code = list_main(argv)
        self.assertEqual(code, expect)
        return json.loads(buf.getvalue())


if __name__ == "__main__":
    unittest.main()
