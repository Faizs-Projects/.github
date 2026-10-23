#!/usr/bin/env python3
"""Tests for the brand-signal extractor and the skill files around it."""

from __future__ import annotations

import gzip
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = Path(__file__).resolve().with_name("extract_brand_signals.py")

spec = importlib.util.spec_from_file_location("extract_brand_signals", SCRIPT)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)

FIXTURE = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Hearth &amp; Rye</title>
  <meta name="description" content="Wood-fired pies and natural wine.">
  <meta name="theme-color" content="#0B3D2E">
  <meta property="og:image" content="/images/og.jpg">
  <link rel="stylesheet" href="/assets/site.css">
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Nunito+Sans">
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "Restaurant",
    "name": "Hearth & Rye",
    "servesCuisine": "Pizza",
    "url": "https://hearthandrye.example/",
    "telephone": "+1-312-555-0100",
    "priceRange": "$$",
    "slogan": "Fire, flour, and a long table.",
    "sameAs": ["https://www.instagram.com/hearthandrye/"],
    "address": {
      "@type": "PostalAddress",
      "streetAddress": "12 Lake St",
      "addressLocality": "Chicago",
      "addressRegion": "IL",
      "postalCode": "60601"
    },
    "aggregateRating": {
      "@type": "AggregateRating",
      "ratingValue": "4.6",
      "reviewCount": "128"
    }
  }
  </script>
</head>
<body>
  <h1>Hearth &amp; Rye</h1>
  <a href="https://www.instagram.com/hearthandrye/">Instagram</a>
  <a href="https://www.facebook.com/sharer/sharer.php?u=https%3A%2F%2Fhearthandrye.example">Share</a>
  <a href="https://twitter.com/intent/tweet?text=Hi">Tweet</a>
  <img src="/logo.svg" alt="Hearth & Rye logo">
  <svg><path fill="#C45A2A" d="M0 0h1v1H0z"></path></svg>
  <style>
    :root { --ink: #1A1A1A; --flame: rgb(196, 90, 42); --space: 16px; }
    body { background: #F6F1E7; color: white; font-family: "Source Serif 4", Georgia, serif; }
    a { color: hsl(0, 100%, 50%); }
  </style>
</body>
</html>
"""

SITE_CSS = """
@import url("/assets/extra.css");
.btn { background-color: #0B3D2E; font-family: "Nunito Sans", sans-serif; }
"""

BASE = "https://hearthandrye.example/"


class ExtractorTests(unittest.TestCase):
    def test_fixture_pulls_brand_signals(self) -> None:
        report = mod.analyze(
            FIXTURE,
            BASE,
            {"https://hearthandrye.example/assets/site.css": SITE_CSS},
        )
        hexes = {row["hex"]: row for row in report["palette"]}
        self.assertIn("#0b3d2e", hexes)
        self.assertIn("theme-color", hexes["#0b3d2e"]["origins"])
        self.assertEqual(hexes["#0b3d2e"]["rgb"], "rgb(11, 61, 46)")
        self.assertFalse(hexes["#0b3d2e"]["neutral"])
        self.assertIn("#c45a2a", hexes)
        self.assertIn("svg", hexes["#c45a2a"]["origins"])
        self.assertIn("css-variable", hexes["#c45a2a"]["origins"])
        self.assertTrue(hexes["#1a1a1a"]["neutral"])
        self.assertTrue(hexes["#ffffff"]["neutral"])
        self.assertIn("#ff0000", hexes)
        self.assertNotIn("#main", [row["hex"] for row in report["palette"]])

        families = [row["family"] for row in report["fonts"]]
        self.assertEqual(families, ["Nunito Sans", "Source Serif 4"])

        self.assertEqual(
            report["social_links"],
            [{"platform": "instagram", "url": "https://www.instagram.com/hearthandrye"}],
        )
        self.assertEqual(report["logo_urls"], ["https://hearthandrye.example/logo.svg"])
        self.assertEqual(report["og"]["image"], "https://hearthandrye.example/images/og.jpg")
        self.assertEqual(report["title"], "Hearth & Rye")
        self.assertEqual(report["headings"], ["Hearth & Rye"])
        self.assertEqual(report["meta_description"], "Wood-fired pies and natural wine.")
        self.assertEqual(report["theme_color"], "#0b3d2e")

        schema = report["json_ld"][0]
        self.assertEqual(schema["name"], "Hearth & Rye")
        self.assertEqual(schema["servesCuisine"], "Pizza")
        self.assertEqual(schema["telephone"], "+1-312-555-0100")
        self.assertEqual(schema["priceRange"], "$$")
        self.assertIn("Chicago", schema["address"])
        self.assertEqual(schema["aggregateRating"]["ratingValue"], "4.6")
        self.assertEqual(schema["aggregateRating"]["reviewCount"], "128")
        names = [item["name"] for item in report["css_variables"]]
        self.assertIn("--flame", names)
        self.assertNotIn("--space", names)

    def test_selectors_are_not_colors(self) -> None:
        html = """
        <style>
          #main { color: #112233; }
          #fffabc { background: #abcdef; }
        </style>
        """
        report = mod.analyze(html, BASE)
        self.assertEqual(
            sorted(row["hex"] for row in report["palette"]),
            ["#112233", "#abcdef"],
        )

    def test_named_and_modern_colors(self) -> None:
        self.assertEqual(mod.normalize_color("#abc"), "#aabbcc")
        self.assertEqual(mod.normalize_color("#abcf"), "#aabbcc")
        self.assertEqual(mod.normalize_color("navy"), "#000080")
        self.assertEqual(mod.normalize_color("transparent"), None)
        self.assertEqual(mod.normalize_color("rgb(196, 90, 42)"), "#c45a2a")
        self.assertEqual(mod.normalize_color("hsl(120, 100%, 50%)"), "#00ff00")
        self.assertEqual(mod.normalize_color("rgb(0 0 255 / 0.5)"), "#0000ff80")

    def test_stylesheet_links_and_imports(self) -> None:
        links = mod.linked_stylesheets(FIXTURE, BASE)
        self.assertEqual(
            links,
            [
                "https://hearthandrye.example/assets/site.css",
                "https://fonts.googleapis.com/css2?family=Nunito+Sans",
            ],
        )
        self.assertEqual(
            mod.stylesheet_imports(SITE_CSS, "https://hearthandrye.example/assets/site.css"),
            ["https://hearthandrye.example/assets/extra.css"],
        )

    def test_share_links_and_tracking(self) -> None:
        self.assertIsNone(mod.clean_social_url("https://www.facebook.com/sharer/sharer.php?u=1"))
        self.assertIsNone(mod.clean_social_url("https://twitter.com/intent/tweet?text=Hi"))
        self.assertIsNone(mod.clean_social_url("https://instagram.com/"))
        cleaned = mod.clean_social_url("https://www.instagram.com/hearthandrye/?utm_source=site")
        self.assertEqual(cleaned, "https://www.instagram.com/hearthandrye")
        self.assertEqual(
            mod.classify_social("https://maps.google.com/maps?q=hearth"),
            "google-maps",
        )

    def test_public_url_guard(self) -> None:
        self.assertIn("non-public", mod.reject_reason("http://127.0.0.1/menu"))
        self.assertIn("non-public", mod.reject_reason("http://10.1.2.3/"))
        self.assertIn("local", mod.reject_reason("http://localhost/"))
        self.assertIn("non-public", mod.reject_reason("http://[::1]/"))
        self.assertIsNone(mod.reject_reason("https://1.1.1.1/"))
        report = mod.collect("http://127.0.0.1/menu", timeout=1)
        self.assertFalse(report["ok"])
        self.assertIn("non-public", report["error"])

    def test_scheme_and_gzip(self) -> None:
        self.assertEqual(mod.with_scheme("example.com/a"), "https://example.com/a")
        self.assertEqual(mod.with_scheme("//example.com/a"), "https://example.com/a")
        raw = gzip.compress(b"<html><title>Ok</title></html>")
        body, warning = mod._prepare_bytes(raw)
        self.assertEqual(body, b"<html><title>Ok</title></html>")
        self.assertEqual(warning, "")

    def test_skill_contract(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        template = (ROOT / "references" / "output-template.md").read_text(encoding="utf-8")
        self.assertTrue(skill.startswith("---\n"))
        self.assertIn("name: brand-kit", skill)
        self.assertIn("$ARGUMENTS", skill)
        self.assertIn("extract_brand_signals.py", skill)
        self.assertIn("references/output-template.md", skill)
        for heading in (
            "## Logo",
            "## Color palette",
            "## Typography",
            "## Brand elements",
            "## Applications",
            "## Voice",
            "## Socials",
            "## Reviews",
            "## Menu signals",
            "## Sources",
            "## Gaps",
        ):
            self.assertIn(heading, template)

    def test_framework_noise_is_set_aside(self) -> None:
        html = """
        <style>
          body { color: #d9534f; font-family: "Font Awesome 6 Free"), Arial, sans-serif; }
          h1 { color: #720f10; font-family: "IM Fell English", "Helvetica Neue", Arial, serif; }
          .tint { background: #720f10b2; }
        </style>
        """
        report = mod.analyze(html, BASE)
        self.assertEqual([row["hex"] for row in report["palette"]], ["#720f10"])
        self.assertEqual([row["hex"] for row in report["framework_colors"]], ["#d9534f"])
        self.assertEqual([row["family"] for row in report["fonts"]], ["IM Fell English"])


if __name__ == "__main__":
    unittest.main()
