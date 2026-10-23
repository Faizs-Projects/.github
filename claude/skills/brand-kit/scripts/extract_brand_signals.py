#!/usr/bin/env python3
"""Extract colors, fonts, social links, and schema from a restaurant website.

Prints one JSON object to stdout. Exit 0 when the page was fetched, even if the
palette is thin. Exit 1 when the URL was refused or the fetch failed.

The script reads static HTML and linked stylesheets. It does not run JavaScript.
"""

from __future__ import annotations

import argparse
import gzip
import ipaddress
import json
import re
import socket
import sys
import urllib.error
import urllib.request
from html.parser import HTMLParser
from typing import Iterable
from urllib.parse import parse_qsl, urlencode, urljoin, urlsplit, urlunsplit

MAX_HTML_BYTES = 2_000_000
MAX_CSS_BYTES = 1_500_000
DEFAULT_TIMEOUT = 20.0
DEFAULT_STYLESHEETS = 6
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)

FONT_CSS_HOSTS = {
    "fonts.googleapis.com",
    "use.typekit.net",
    "p.typekit.net",
    "fast.fonts.net",
    "cloud.typography.com",
}

GENERICS = {
    "serif",
    "sans-serif",
    "monospace",
    "cursive",
    "fantasy",
    "system-ui",
    "ui-sans-serif",
    "ui-serif",
    "ui-monospace",
    "ui-rounded",
    "emoji",
    "math",
    "fangsong",
    "inherit",
    "initial",
    "unset",
    "revert",
    "revert-layer",
}

ICON_FONT_MARKERS = (
    "font awesome",
    "fontawesome",
    "dashicons",
    "bootstrap-icons",
    "glyphicons",
    "icomoon",
    "material icons",
    "swiper-icons",
)
EXACT_ICON_FONTS = {"slick"}

FRAMEWORK_FONTS = {
    "arial",
    "helvetica",
    "helvetica neue",
    "times new roman",
    "times",
    "courier new",
    "courier",
    "verdana",
    "tahoma",
    "trebuchet ms",
    "lucida grande",
    "lucida sans",
    "segoe ui",
}

# Saturated defaults from Bootstrap. Grays and black and white stay in the palette
# because restaurants use them as real text and background colors.
FRAMEWORK_COLORS = {
    "#337ab7",
    "#5cb85c",
    "#5bc0de",
    "#f0ad4e",
    "#d9534f",
    "#007bff",
    "#28a745",
    "#dc3545",
    "#ffc107",
    "#17a2b8",
    "#6f42c1",
    "#6610f2",
    "#d63384",
    "#fd7e14",
    "#20c997",
    "#0d6efd",
    "#198754",
    "#0dcaf0",
    "#286090",
    "#204d74",
    "#449d44",
    "#398439",
    "#31b0d5",
    "#269abc",
    "#ec971f",
    "#d58512",
    "#c9302c",
    "#ac2925",
    "#4d90fe",
}

SKIP_COLOR_WORDS = {
    "none",
    "currentcolor",
    "transparent",
    "inherit",
    "initial",
    "unset",
    "revert",
    "auto",
}

NAMED_COLORS = {
    "aliceblue": "#f0f8ff",
    "antiquewhite": "#faebd7",
    "aqua": "#00ffff",
    "azure": "#f0ffff",
    "beige": "#f5f5dc",
    "bisque": "#ffe4c4",
    "black": "#000000",
    "blanchedalmond": "#ffebcd",
    "blue": "#0000ff",
    "brown": "#a52a2a",
    "burlywood": "#deb887",
    "chocolate": "#d2691e",
    "coral": "#ff7f50",
    "cornsilk": "#fff8dc",
    "crimson": "#dc143c",
    "darkblue": "#00008b",
    "darkgreen": "#006400",
    "darkred": "#8b0000",
    "dimgray": "#696969",
    "dimgrey": "#696969",
    "floralwhite": "#fffaf0",
    "fuchsia": "#ff00ff",
    "ghostwhite": "#f8f8ff",
    "gold": "#ffd700",
    "gray": "#808080",
    "green": "#008000",
    "grey": "#808080",
    "honeydew": "#f0fff0",
    "hotpink": "#ff69b4",
    "indigo": "#4b0082",
    "ivory": "#fffff0",
    "khaki": "#f0e68c",
    "lavender": "#e6e6fa",
    "lightgray": "#d3d3d3",
    "lightgrey": "#d3d3d3",
    "lime": "#00ff00",
    "linen": "#faf0e6",
    "maroon": "#800000",
    "mintcream": "#f5fffa",
    "navy": "#000080",
    "oldlace": "#fdf5e6",
    "olive": "#808000",
    "orange": "#ffa500",
    "pink": "#ffc0cb",
    "plum": "#dda0dd",
    "purple": "#800080",
    "red": "#ff0000",
    "salmon": "#fa8072",
    "seashell": "#fff5ee",
    "sienna": "#a0522d",
    "silver": "#c0c0c0",
    "snow": "#fffafa",
    "tan": "#d2b48c",
    "teal": "#008080",
    "tomato": "#ff6347",
    "violet": "#ee82ee",
    "wheat": "#f5deb3",
    "white": "#ffffff",
    "whitesmoke": "#f5f5f5",
    "yellow": "#ffff00",
}

KEEP_SCHEMA_TYPES = {
    "Restaurant",
    "FoodEstablishment",
    "Bakery",
    "BarOrPub",
    "CafeOrCoffeeShop",
    "Brewery",
    "Winery",
    "IceCreamShop",
    "FastFoodRestaurant",
    "Distillery",
    "LocalBusiness",
    "Organization",
    "WebSite",
    "Menu",
    "FoodService",
}

COLOR_PROPS = {
    "color",
    "background",
    "background-color",
    "background-image",
    "border",
    "border-color",
    "border-top",
    "border-right",
    "border-bottom",
    "border-left",
    "border-top-color",
    "border-right-color",
    "border-bottom-color",
    "border-left-color",
    "outline",
    "outline-color",
    "fill",
    "stroke",
    "stop-color",
    "accent-color",
    "caret-color",
    "column-rule",
    "column-rule-color",
    "text-decoration",
    "text-decoration-color",
    "box-shadow",
    "text-shadow",
}

HEX_RE = re.compile(r"#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{4}|[0-9a-fA-F]{3})\b")
RGB_RE = re.compile(
    r"rgba?\(\s*([0-9.]+%?)\s*,\s*([0-9.]+%?)\s*,\s*([0-9.]+%?)"
    r"(?:\s*,\s*([0-9.]+%?))?\s*\)",
    re.I,
)
RGB_MODERN_RE = re.compile(
    r"rgba?\(\s*([0-9.]+%?)\s+([0-9.]+%?)\s+([0-9.]+%?)"
    r"(?:\s*/\s*([0-9.]+%?))?\s*\)",
    re.I,
)
HSL_RE = re.compile(
    r"hsla?\(\s*([0-9.]+)\s*,\s*([0-9.]+)%\s*,\s*([0-9.]+)%"
    r"(?:\s*,\s*([0-9.]+%?))?\s*\)",
    re.I,
)
HSL_MODERN_RE = re.compile(
    r"hsla?\(\s*([0-9.]+)\s+([0-9.]+)%\s+([0-9.]+)%"
    r"(?:\s*/\s*([0-9.]+%?))?\s*\)",
    re.I,
)
DECL_RE = re.compile(r"([A-Za-z_-][\w-]*)\s*:\s*([^;{}]+)")
IMPORT_RE = re.compile(
    r"""@import\s+(?:url\(\s*)?['"]([^'"]+)['"](?:\s*\))?"""
    r"""|@import\s+url\(\s*([^)'"\s]+)\s*\)"""
    r"""|@import\s+([^;\s'"]+)""",
    re.I,
)
COMMENT_RE = re.compile(r"/\*.*?\*/", re.S)
URL_RE = re.compile(r"""url\(\s*(?:"[^"]*"|'[^']*'|[^)]*)\)""", re.I)
FONT_RE = re.compile(r"font-family\s*:\s*([^;{}]+)", re.I)
CHARSET_RE = re.compile(r"""charset=["']?\s*([\w.-]+)""", re.I)

SOCIAL_HOSTS = (
    ("instagram.com", "instagram"),
    ("facebook.com", "facebook"),
    ("fb.com", "facebook"),
    ("tiktok.com", "tiktok"),
    ("twitter.com", "x"),
    ("x.com", "x"),
    ("youtube.com", "youtube"),
    ("youtu.be", "youtube"),
    ("linkedin.com", "linkedin"),
    ("pinterest.com", "pinterest"),
    ("yelp.com", "yelp"),
    ("opentable.com", "opentable"),
    ("resy.com", "resy"),
    ("doordash.com", "doordash"),
    ("ubereats.com", "ubereats"),
    ("grubhub.com", "grubhub"),
)


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        raise urllib.error.HTTPError(req.full_url, code, msg, headers, fp)

    http_error_301 = http_error_302
    http_error_303 = http_error_302
    http_error_307 = http_error_302
    http_error_308 = http_error_302


def host_key(hostname: str | None) -> str:
    host = (hostname or "").lower().rstrip(".")
    if host.startswith("www."):
        return host[4:]
    return host


def with_scheme(url: str) -> str:
    text = url.strip()
    if text.startswith("//"):
        return "https:" + text
    parts = urlsplit(text)
    if not parts.scheme:
        return "https://" + text
    return text


def reject_reason(url: str) -> str | None:
    """Return why a URL must not be fetched, or None when it is a public http(s) URL."""
    parts = urlsplit(url)
    if parts.scheme not in {"http", "https"}:
        return "Only http and https URLs can be fetched."
    host = parts.hostname
    if not host:
        return "URL has no host."
    host = host.lower().rstrip(".")
    if host in {"localhost", "localhost.localdomain"} or host.endswith((".local", ".internal", ".localhost")):
        return "Refusing a local hostname."
    try:
        literal = ipaddress.ip_address(host)
    except ValueError:
        literal = None
    if literal is not None:
        if not literal.is_global:
            return "Refusing a non-public address."
        return None
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror:
        return "Could not resolve the host."
    if not infos:
        return "Could not resolve the host."
    for info in infos:
        address = ipaddress.ip_address(info[4][0])
        if not address.is_global:
            return "Refusing a host that resolves to a non-public address."
    return None


def _channel(token: str) -> float:
    text = token.strip()
    if text.endswith("%"):
        return max(0.0, min(100.0, float(text[:-1]))) / 100.0 * 255.0
    return max(0.0, min(255.0, float(text)))


def _alpha(token: str | None) -> float:
    if token is None or token == "":
        return 1.0
    text = token.strip()
    if text.endswith("%"):
        return max(0.0, min(100.0, float(text[:-1]))) / 100.0
    return max(0.0, min(1.0, float(text)))


def _rgb_hex(red: float, green: float, blue: float, alpha: float = 1.0) -> str | None:
    if alpha < 0.02:
        return None

    def byte(value: float) -> int:
        return max(0, min(255, int(round(value))))

    hex6 = f"#{byte(red):02x}{byte(green):02x}{byte(blue):02x}"
    if alpha >= 0.999:
        return hex6
    return hex6 + f"{byte(alpha * 255):02x}"


def _hsl_to_hex(hue: float, sat_pct: float, light_pct: float, alpha: float) -> str | None:
    hue = hue % 360
    sat = max(0.0, min(100.0, sat_pct)) / 100.0
    light = max(0.0, min(100.0, light_pct)) / 100.0
    chroma = (1 - abs(2 * light - 1)) * sat
    hue_sector = hue / 60.0
    cross = chroma * (1 - abs(hue_sector % 2 - 1))
    match = light - chroma / 2
    sector = int(hue_sector)
    channels = (
        (chroma, cross, 0.0),
        (cross, chroma, 0.0),
        (0.0, chroma, cross),
        (0.0, cross, chroma),
        (cross, 0.0, chroma),
        (chroma, 0.0, cross),
    )[sector]
    red, green, blue = (channel + match for channel in channels)
    return _rgb_hex(red * 255, green * 255, blue * 255, alpha)


def normalize_hex(token: str) -> str | None:
    text = token.strip()
    if not text.startswith("#"):
        return None
    digits = text[1:]
    if not re.fullmatch(r"[0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8}", digits):
        return None
    if len(digits) in {3, 4}:
        digits = "".join(char * 2 for char in digits)
    red = int(digits[0:2], 16)
    green = int(digits[2:4], 16)
    blue = int(digits[4:6], 16)
    alpha = int(digits[6:8], 16) / 255.0 if len(digits) == 8 else 1.0
    return _rgb_hex(red, green, blue, alpha)


def normalize_color(token: str) -> str | None:
    text = token.strip().lower()
    if not text or text in SKIP_COLOR_WORDS:
        return None
    if text.startswith("#"):
        return normalize_hex(text)
    for pattern, kind in (
        (RGB_RE, "rgb"),
        (RGB_MODERN_RE, "rgb"),
        (HSL_RE, "hsl"),
        (HSL_MODERN_RE, "hsl"),
    ):
        match = pattern.fullmatch(text)
        if not match:
            continue
        try:
            if kind == "rgb":
                return _rgb_hex(
                    _channel(match.group(1)),
                    _channel(match.group(2)),
                    _channel(match.group(3)),
                    _alpha(match.group(4)),
                )
            return _hsl_to_hex(
                float(match.group(1)),
                float(match.group(2)),
                float(match.group(3)),
                _alpha(match.group(4)),
            )
        except ValueError:
            return None
    return NAMED_COLORS.get(text)


def rgb_string(hex_value: str) -> str:
    red = int(hex_value[1:3], 16)
    green = int(hex_value[3:5], 16)
    blue = int(hex_value[5:7], 16)
    if len(hex_value) == 9:
        alpha = int(hex_value[7:9], 16) / 255.0
        alpha_text = f"{alpha:.2f}".rstrip("0").rstrip(".")
        return f"rgba({red}, {green}, {blue}, {alpha_text})"
    return f"rgb({red}, {green}, {blue})"


def is_neutral(hex_value: str) -> bool:
    red = int(hex_value[1:3], 16)
    green = int(hex_value[3:5], 16)
    blue = int(hex_value[5:7], 16)
    return max(red, green, blue) - min(red, green, blue) <= 18


def _colors_in(value: str, named: bool) -> list[str]:
    found: list[str] = []
    for match in HEX_RE.finditer(value):
        hex_value = normalize_hex(match.group(0))
        if hex_value:
            found.append(hex_value)
    for pattern, kind in (
        (RGB_RE, "rgb"),
        (RGB_MODERN_RE, "rgb"),
        (HSL_RE, "hsl"),
        (HSL_MODERN_RE, "hsl"),
    ):
        for match in pattern.finditer(value):
            try:
                if kind == "rgb":
                    hex_value = _rgb_hex(
                        _channel(match.group(1)),
                        _channel(match.group(2)),
                        _channel(match.group(3)),
                        _alpha(match.group(4)),
                    )
                else:
                    hex_value = _hsl_to_hex(
                        float(match.group(1)),
                        float(match.group(2)),
                        float(match.group(3)),
                        _alpha(match.group(4)),
                    )
            except ValueError:
                continue
            if hex_value:
                found.append(hex_value)
    if named:
        cleaned = re.sub(r"!important", "", value, flags=re.I).strip()
        single = NAMED_COLORS.get(cleaned.lower())
        if single:
            found.append(single)
        else:
            for word in re.findall(r"[A-Za-z]+", value):
                hex_value = NAMED_COLORS.get(word.lower())
                if hex_value:
                    found.append(hex_value)
    return found


def _is_color_prop(prop: str) -> bool:
    name = prop.lower()
    return name in COLOR_PROPS or "color" in name


def _clean_css(css: str) -> str:
    return URL_RE.sub(" ", COMMENT_RE.sub(" ", css))


def _normalize_family(part: str) -> str:
    family = re.sub(r"\s*!important\s*$", "", part.strip(), flags=re.I).strip()
    if len(family) >= 2 and family[0] == family[-1] and family[0] in {"'", '"'}:
        family = family[1:-1]
    family = family.strip().strip("'\"() ")
    return re.sub(r"\s+", " ", family)


def _is_icon_font(name: str) -> bool:
    key = name.lower()
    return key in EXACT_ICON_FONTS or any(marker in key for marker in ICON_FONT_MARKERS)


def font_families(css: str) -> list[dict]:
    """Return the first real family in each font-family declaration.

    Later names in the same declaration are fallbacks, so Georgia in
    `"Source Serif 4", Georgia, serif` is not treated as a brand font.
    Icon fonts are skipped so the next family in the stack can be chosen.
    """
    counts: dict[str, dict] = {}
    for match in FONT_RE.finditer(_clean_css(css)):
        raw = match.group(1).split("!", 1)[0]
        chosen = ""
        for part in raw.split(","):
            family = _normalize_family(part)
            key = family.lower()
            if not family or key in GENERICS or key.startswith("var(") or _is_icon_font(family):
                continue
            chosen = family
            break
        if not chosen:
            continue
        slot = counts.setdefault(chosen.lower(), {"family": chosen, "count": 0})
        slot["count"] += 1
    rows = list(counts.values())
    rows.sort(key=lambda item: (-int(item["count"]), str(item["family"]).lower()))
    return rows


def stylesheet_imports(css: str, base_url: str) -> list[str]:
    imports: list[str] = []
    for match in IMPORT_RE.finditer(COMMENT_RE.sub(" ", css)):
        target = next(group.strip() for group in match.groups() if group)
        if not target or target.startswith("data:"):
            continue
        imports.append(urljoin(base_url, target))
    return imports


def _strip_tracking(url: str) -> str:
    parts = urlsplit(url)
    kept = [
        (key, value)
        for key, value in parse_qsl(parts.query, keep_blank_values=True)
        if not key.lower().startswith("utm_") and key.lower() not in {"fbclid", "gclid", "mc_cid", "mc_eid"}
    ]
    query = urlencode(kept)
    path = parts.path.rstrip("/")
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path, query, ""))


def classify_social(url: str) -> str | None:
    parts = urlsplit(url)
    if parts.scheme not in {"http", "https"}:
        return None
    host = host_key(parts.hostname)
    if not host:
        return None
    for suffix, platform in SOCIAL_HOSTS:
        if host == suffix or host.endswith("." + suffix):
            return platform
    if "tripadvisor." in host:
        return "tripadvisor"
    path = parts.path.lower()
    if host in {"maps.app.goo.gl", "maps.google.com"}:
        return "google-maps"
    if host.endswith("google.com") and path.startswith("/maps"):
        return "google-maps"
    if host == "maps.apple.com":
        return "apple-maps"
    return None


def is_share_link(url: str) -> bool:
    parts = urlsplit(url)
    path = parts.path.lower()
    markers = (
        "/sharer",
        "/sharearticle",
        "/pin/create",
        "/plugins/",
        "/dialog/",
        "/intent",
        "/share.php",
        "/sharer.php",
    )
    if any(marker in path for marker in markers):
        return True
    trimmed = path.rstrip("/")
    if trimmed.endswith("/share") or "/share/" in path:
        return True
    if not trimmed:
        return True
    return False


def clean_social_url(url: str) -> str | None:
    platform = classify_social(url)
    if platform is None or is_share_link(url):
        return None
    return _strip_tracking(url)


class _Palette:
    def __init__(self) -> None:
        self._items: dict[str, dict] = {}

    def add(self, hex_value: str | None, origin: str, bonus: int = 0) -> None:
        if not hex_value:
            return
        item = self._items.setdefault(
            hex_value, {"count": 0, "bonus": 0, "origins": set()}
        )
        item["count"] += 1
        item["bonus"] += bonus
        item["origins"].add(origin)

    def export(self) -> tuple[list[dict], list[dict]]:
        # An 8-digit hex is the same swatch with transparency. Keep the solid color.
        solids = {hex_value for hex_value in self._items if len(hex_value) == 7}
        rows = []
        framework = []
        for hex_value, item in self._items.items():
            if len(hex_value) == 9 and hex_value[:7] in solids:
                continue
            row = {
                "hex": hex_value,
                "rgb": rgb_string(hex_value),
                "weight": min(int(item["count"]), 40) + int(item["bonus"]),
                "count": int(item["count"]),
                "neutral": is_neutral(hex_value),
                "origins": sorted(item["origins"]),
            }
            if hex_value[:7] in FRAMEWORK_COLORS:
                framework.append(row)
            else:
                rows.append(row)
        rows.sort(key=lambda row: (-row["weight"], row["hex"]))
        framework.sort(key=lambda row: (-row["weight"], row["hex"]))
        if not rows:
            return framework[:24], []
        return rows[:24], framework[:12]


def _parse_css(css: str, palette: _Palette, variables: list[dict]) -> None:
    cleaned = _clean_css(css)
    for match in DECL_RE.finditer(cleaned):
        prop = match.group(1)
        value = match.group(2).strip()
        if prop.startswith("--"):
            colors = _colors_in(value, named=True)
            if colors:
                variables.append(
                    {
                        "name": prop,
                        "value": re.sub(r"\s+", " ", value)[:80],
                        "hex": colors[0],
                    }
                )
                for hex_value in colors:
                    palette.add(hex_value, "css-variable", bonus=14)
            continue
        for hex_value in _colors_in(value, named=_is_color_prop(prop)):
            palette.add(hex_value, "declaration")


def _font_rows(blobs: Iterable[str]) -> list[dict]:
    counts: dict[str, dict] = {}
    for blob in blobs:
        for row in font_families(blob):
            key = row["family"].lower()
            if _is_icon_font(key):
                continue
            slot = counts.setdefault(key, {"family": row["family"], "count": 0})
            slot["count"] += int(row["count"])
    rows = list(counts.values())
    distinctive = [row for row in rows if row["family"].lower() not in FRAMEWORK_FONTS]
    if distinctive:
        rows = distinctive
    rows.sort(key=lambda item: (-item["count"], item["family"].lower()))
    return rows


class _PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.meta: list[tuple[str, str, str]] = []
        self.stylesheets: list[str] = []
        self.inline_css: list[str] = []
        self.links: list[str] = []
        self.images: list[str] = []
        self.svg_colors: list[str] = []
        self.json_ld: list[str] = []
        self.headings: list[str] = []
        self._capture: str | None = None
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._start(tag, attrs)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._start(tag, attrs, empty=True)

    def _start(self, tag: str, attrs: list[tuple[str, str | None]], empty: bool = False) -> None:
        attr = {key.lower(): value or "" for key, value in attrs}
        style = attr.get("style", "")
        if style:
            self.inline_css.append(style)
        for name in ("fill", "stroke", "color"):
            if attr.get(name):
                self.svg_colors.append(attr[name])
        if tag == "link" and "stylesheet" in attr.get("rel", "").lower() and attr.get("href"):
            self.stylesheets.append(attr["href"])
        elif tag == "meta":
            key = (attr.get("name") or attr.get("property") or attr.get("itemprop") or "").lower()
            content = attr.get("content", "")
            if key and content:
                self.meta.append((key, content, attr.get("media", "")))
        elif tag == "a" and attr.get("href"):
            self.links.append(attr["href"])
        elif tag == "img":
            blob = " ".join(attr.get(name, "") for name in ("src", "alt", "class", "id")).lower()
            if "logo" in blob and attr.get("src"):
                self.images.append(attr["src"])
        if empty or self._capture:
            return
        if tag == "script" and "ld+json" in attr.get("type", "").lower():
            self._capture = "jsonld"
            self._parts = []
        elif tag == "style":
            self._capture = "style"
            self._parts = []
        elif tag == "title":
            self._capture = "title"
            self._parts = []
        elif tag == "h1" and len(self.headings) < 5:
            self._capture = "h1"
            self._parts = []

    def handle_data(self, data: str) -> None:
        if self._capture:
            self._parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        expected = {"jsonld": "script", "style": "style", "title": "title", "h1": "h1"}
        if not self._capture or expected.get(self._capture) != tag:
            return
        text = "".join(self._parts).strip()
        kind = self._capture
        self._capture = None
        self._parts = []
        if not text:
            return
        if kind == "jsonld":
            self.json_ld.append(text)
        elif kind == "style":
            self.inline_css.append(text)
        elif kind == "title" and not self.title:
            self.title = re.sub(r"\s+", " ", text)
        elif kind == "h1":
            heading = re.sub(r"\s+", " ", text)
            if heading:
                self.headings.append(heading)


def _meta_value(meta: list[tuple[str, str, str]], key: str) -> str:
    for name, content, _media in meta:
        if name == key:
            return content.strip()
    return ""


def _absolute(base_url: str, href: str) -> str | None:
    if not href:
        return None
    text = href.strip()
    if not text or text.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
        return None
    return urljoin(base_url, text)


def linked_stylesheets(html: str, base_url: str) -> list[str]:
    parser = _PageParser()
    try:
        parser.feed(html)
        parser.close()
    except Exception:
        pass
    urls = []
    seen = set()
    for href in parser.stylesheets:
        absolute = _absolute(base_url, href)
        if absolute and absolute not in seen:
            seen.add(absolute)
            urls.append(absolute)
    return urls


def _as_url(value) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    if isinstance(value, list):
        for item in value:
            found = _as_url(item)
            if found:
                return found
    if isinstance(value, dict):
        return _as_url(value.get("url") or value.get("contentUrl") or value.get("@id"))
    return None


def _as_text(value) -> str | None:
    if isinstance(value, str):
        text = value.strip()
        return text or None
    if isinstance(value, list):
        parts = [part for part in (_as_text(item) for item in value) if part]
        return ", ".join(parts) or None
    if isinstance(value, (int, float)):
        return str(value)
    return None


def _format_address(value) -> str | None:
    if isinstance(value, str):
        return value.strip() or None
    if isinstance(value, list):
        parts = [_format_address(item) for item in value]
        joined = "; ".join(part for part in parts if part)
        return joined or None
    if not isinstance(value, dict):
        return None
    country = value.get("addressCountry")
    if isinstance(country, dict):
        country = country.get("name") or country.get("addressCountry")
    pieces = [
        value.get("streetAddress"),
        value.get("addressLocality"),
        value.get("addressRegion"),
        value.get("postalCode"),
        country,
    ]
    return ", ".join(str(piece).strip() for piece in pieces if isinstance(piece, str) and piece.strip()) or None


def _format_hours(node: dict) -> str | None:
    raw = node.get("openingHours")
    text = _as_text(raw)
    if text:
        return text
    spec = node.get("openingHoursSpecification")
    if isinstance(spec, dict):
        spec = [spec]
    if not isinstance(spec, list):
        return None
    lines = []
    for item in spec:
        if not isinstance(item, dict):
            continue
        days = item.get("dayOfWeek")
        if isinstance(days, list):
            day_text = ", ".join(str(day).rstrip("/").split("/")[-1] for day in days)
        elif isinstance(days, str):
            day_text = days.rstrip("/").split("/")[-1]
        else:
            day_text = ""
        opens = item.get("opens") or ""
        closes = item.get("closes") or ""
        span = "-".join(part for part in (str(opens), str(closes)) if part)
        line = " ".join(part for part in (day_text, span) if part)
        if line:
            lines.append(line)
    return "; ".join(lines) or None


def _schema_types(node: dict) -> set[str]:
    raw = node.get("@type")
    if isinstance(raw, list):
        return {str(item) for item in raw}
    if isinstance(raw, str):
        return {raw}
    return set()


def _simplify_schema(node: dict) -> dict | None:
    types = _schema_types(node)
    useful = bool(
        types & KEEP_SCHEMA_TYPES
        or node.get("servesCuisine")
        or node.get("address")
        or node.get("sameAs")
        or node.get("aggregateRating")
    )
    if not useful:
        return None
    rating = node.get("aggregateRating")
    rating_out = None
    if isinstance(rating, dict):
        rating_out = {
            "ratingValue": _as_text(rating.get("ratingValue")),
            "reviewCount": _as_text(rating.get("reviewCount") or rating.get("ratingCount")),
            "bestRating": _as_text(rating.get("bestRating")),
        }
        if not any(rating_out.values()):
            rating_out = None
    same_as = node.get("sameAs")
    if isinstance(same_as, str):
        same_as = [same_as]
    if not isinstance(same_as, list):
        same_as = []
    description = _as_text(node.get("description"))
    if description and len(description) > 600:
        description = description[:597].rstrip() + "..."
    simplified = {
        "@type": sorted(types),
        "name": _as_text(node.get("name")),
        "alternateName": _as_text(node.get("alternateName")),
        "slogan": _as_text(node.get("slogan")),
        "description": description,
        "url": _as_url(node.get("url")),
        "telephone": _as_text(node.get("telephone")),
        "email": _as_text(node.get("email")),
        "priceRange": _as_text(node.get("priceRange")),
        "servesCuisine": _as_text(node.get("servesCuisine")),
        "menu": _as_url(node.get("menu") or node.get("hasMenu")),
        "image": _as_url(node.get("image")),
        "logo": _as_url(node.get("logo")),
        "address": _format_address(node.get("address")),
        "openingHours": _format_hours(node),
        "aggregateRating": rating_out,
        "sameAs": [item for item in (_as_url(entry) or _as_text(entry) for entry in same_as) if item],
    }
    if not any(value not in (None, [], "") for key, value in simplified.items() if key != "@type"):
        return None
    return {key: value for key, value in simplified.items() if value not in (None, [], "")}


def _iter_schema(data) -> Iterable[dict]:
    if isinstance(data, list):
        for item in data:
            yield from _iter_schema(item)
        return
    if not isinstance(data, dict):
        return
    graph = data.get("@graph")
    if isinstance(graph, list):
        for item in graph:
            yield from _iter_schema(item)
        return
    yield data


def _schema_from_blocks(blocks: list[str], warnings: list[str]) -> list[dict]:
    nodes: list[dict] = []
    for block in blocks:
        try:
            parsed = json.loads(block)
        except json.JSONDecodeError:
            warnings.append("One JSON-LD block did not parse.")
            continue
        for node in _iter_schema(parsed):
            simplified = _simplify_schema(node)
            if simplified:
                nodes.append(simplified)
            if len(nodes) >= 8:
                return nodes
    return nodes


def analyze(html: str, base_url: str, stylesheets: dict[str, str] | None = None) -> dict:
    """Build the brand-signal report for HTML and any already-fetched stylesheets."""
    parser = _PageParser()
    warnings: list[str] = []
    try:
        parser.feed(html)
        parser.close()
    except Exception as exc:
        warnings.append(f"HTML parsing stopped early: {exc.__class__.__name__}")
    sheets = stylesheets or {}
    palette = _Palette()
    variables: list[dict] = []
    css_blobs = list(parser.inline_css) + list(sheets.values())
    for blob in css_blobs:
        _parse_css(blob, palette, variables)

    theme_colors = []
    for key, content, media in parser.meta:
        if key != "theme-color":
            continue
        hex_value = normalize_color(content)
        if not hex_value:
            continue
        theme_colors.append({"hex": hex_value, "media": media})
        palette.add(hex_value, "theme-color", bonus=40)
    for token in parser.svg_colors:
        palette.add(normalize_color(token), "svg", bonus=8)

    socials = []
    seen_social = set()
    for href in parser.links:
        absolute = _absolute(base_url, href)
        if not absolute:
            continue
        platform = classify_social(absolute)
        cleaned = clean_social_url(absolute)
        if not platform or not cleaned:
            continue
        path = urlsplit(cleaned).path.lower()
        key = (platform, host_key(urlsplit(cleaned).hostname), path)
        if key in seen_social:
            continue
        seen_social.add(key)
        socials.append({"platform": platform, "url": cleaned})

    schema = _schema_from_blocks(parser.json_ld, warnings)
    for node in schema:
        for href in node.get("sameAs", []):
            platform = classify_social(href)
            cleaned = clean_social_url(href)
            if not platform or not cleaned:
                continue
            path = urlsplit(cleaned).path.lower()
            key = (platform, host_key(urlsplit(cleaned).hostname), path)
            if key in seen_social:
                continue
            seen_social.add(key)
            socials.append({"platform": platform, "url": cleaned})

    logos = []
    for href in parser.images:
        absolute = _absolute(base_url, href)
        if absolute and absolute not in logos:
            logos.append(absolute)
    for node in schema:
        for key in ("logo", "image"):
            absolute = _absolute(base_url, node.get(key, "")) if isinstance(node.get(key), str) else node.get(key)
            if isinstance(absolute, str) and absolute not in logos and key == "logo":
                logos.append(absolute)

    palette, framework_colors = palette.export()
    deduped_vars = []
    seen_vars = set()
    for variable in variables:
        marker = (variable["name"], variable["hex"])
        if marker in seen_vars:
            continue
        seen_vars.add(marker)
        deduped_vars.append(variable)

    description = _meta_value(parser.meta, "description") or _meta_value(parser.meta, "og:description")
    return {
        "final_url": base_url,
        "title": parser.title,
        "meta_description": description,
        "og": {
            "title": _meta_value(parser.meta, "og:title"),
            "description": _meta_value(parser.meta, "og:description"),
            "image": _absolute(base_url, _meta_value(parser.meta, "og:image")) or "",
            "site_name": _meta_value(parser.meta, "og:site_name"),
        },
        "headings": parser.headings,
        "theme_color": theme_colors[0]["hex"] if theme_colors else "",
        "theme_colors": theme_colors,
        "json_ld": schema,
        "fonts": _font_rows(css_blobs),
        "social_links": socials,
        "logo_urls": logos[:8],
        "palette": palette,
        "framework_colors": framework_colors,
        "css_variables": deduped_vars[:40],
        "stylesheets_fetched": list(sheets),
        "warnings": warnings,
    }


def _decode_body(raw: bytes, content_type: str) -> str:
    charset = "utf-8"
    match = CHARSET_RE.search(content_type)
    sniffed = False
    if not match:
        preview = raw[:2048].decode("ascii", errors="ignore")
        match = CHARSET_RE.search(preview)
        sniffed = match is not None
    if match:
        charset = match.group(1)
    try:
        return raw.decode(charset, errors="replace")
    except LookupError:
        if sniffed:
            return raw.decode("utf-8", errors="replace")
        return raw.decode("utf-8", errors="replace")


def _prepare_bytes(raw: bytes) -> tuple[bytes, str]:
    warning = ""
    if raw[:2] == b"\x1f\x8b":
        try:
            raw = gzip.decompress(raw)
        except gzip.BadGzipFile:
            warning = "Response looked gzip-compressed but did not decompress."
    return raw, warning


def fetch(url: str, timeout: float = DEFAULT_TIMEOUT, limit: int = MAX_HTML_BYTES):
    reason = reject_reason(url)
    if reason:
        return {
            "ok": False,
            "url": url,
            "final_url": url,
            "status": None,
            "content_type": "",
            "text": "",
            "truncated": False,
            "error": reason,
            "warning": "",
        }
    opener = urllib.request.build_opener(_NoRedirect())
    current = url
    for _hop in range(6):
        reason = reject_reason(current)
        if reason:
            return {
                "ok": False,
                "url": url,
                "final_url": current,
                "status": None,
                "content_type": "",
                "text": "",
                "truncated": False,
                "error": reason,
                "warning": "",
            }
        request = urllib.request.Request(
            current,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "text/html,application/xhtml+xml,text/css;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            },
        )
        try:
            with opener.open(request, timeout=timeout) as response:
                status = getattr(response, "status", 200)
                content_type = response.headers.get("Content-Type", "")
                raw = response.read(limit + 1)
                truncated = len(raw) > limit
                raw = raw[:limit]
                raw, warning = _prepare_bytes(raw)
                return {
                    "ok": True,
                    "url": url,
                    "final_url": current,
                    "status": status,
                    "content_type": content_type,
                    "text": _decode_body(raw, content_type),
                    "truncated": truncated,
                    "error": None,
                    "warning": warning,
                }
        except urllib.error.HTTPError as exc:
            location = exc.headers.get("Location") if exc.headers else None
            if exc.code in {301, 302, 303, 307, 308} and location:
                current = urljoin(current, location)
                exc.close()
                continue
            error = f"HTTP {exc.code}"
            exc.close()
            return {
                "ok": False,
                "url": url,
                "final_url": current,
                "status": exc.code,
                "content_type": "",
                "text": "",
                "truncated": False,
                "error": error,
                "warning": "",
            }
        except urllib.error.URLError as exc:
            return {
                "ok": False,
                "url": url,
                "final_url": current,
                "status": None,
                "content_type": "",
                "text": "",
                "truncated": False,
                "error": str(getattr(exc, "reason", exc)),
                "warning": "",
            }
        except (TimeoutError, socket.timeout):
            return {
                "ok": False,
                "url": url,
                "final_url": current,
                "status": None,
                "content_type": "",
                "text": "",
                "truncated": False,
                "error": "timed out",
                "warning": "",
            }
    return {
        "ok": False,
        "url": url,
        "final_url": current,
        "status": None,
        "content_type": "",
        "text": "",
        "truncated": False,
        "error": "too many redirects",
        "warning": "",
    }


def _looks_like_html(page: dict) -> bool:
    content_type = page["content_type"].lower()
    if "html" in content_type or "xml" in content_type:
        return True
    sample = page["text"][:1500].lower()
    return "<html" in sample or "<!doctype html" in sample or "<style" in sample or "theme-color" in sample


def _looks_like_css(page: dict) -> bool:
    content_type = page["content_type"].lower()
    if any(token in content_type for token in ("html", "json", "javascript", "image/")):
        return False
    if "text/css" in content_type or page["final_url"].lower().split("?", 1)[0].endswith(".css"):
        return True
    sample = page["text"][:1500].lower()
    if "<html" in sample or "<!doctype html" in sample:
        return False
    return "{" in page["text"] and ":" in page["text"]


def _stylesheet_rank(page_url: str, sheet_url: str) -> int:
    host = host_key(urlsplit(sheet_url).hostname)
    page_host = host_key(urlsplit(page_url).hostname)
    if host == page_host:
        return 0
    if host in FONT_CSS_HOSTS:
        return 1
    return 2


def _failure(url: str, error: str, status: int | None = None, final_url: str | None = None) -> dict:
    return {
        "ok": False,
        "input_url": url,
        "final_url": final_url,
        "http_status": status,
        "error": error,
    }


def collect(url: str, timeout: float = DEFAULT_TIMEOUT, max_stylesheets: int = DEFAULT_STYLESHEETS) -> dict:
    requested = with_scheme(url)
    from datetime import datetime, timezone

    page = fetch(requested, timeout=timeout, limit=MAX_HTML_BYTES)
    if not page["ok"]:
        return _failure(requested, page["error"] or "fetch failed", page["status"], page["final_url"])
    fetched_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    warnings = []
    if page["warning"]:
        warnings.append(page["warning"])
    if page["truncated"]:
        warnings.append("Homepage HTML was truncated.")
    if not _looks_like_html(page):
        return {
            "ok": True,
            "input_url": requested,
            "final_url": page["final_url"],
            "fetched_at": fetched_at,
            "http_status": page["status"],
            "content_type": page["content_type"],
            "title": "",
            "meta_description": "",
            "og": {"title": "", "description": "", "image": "", "site_name": ""},
            "headings": [],
            "theme_color": "",
            "theme_colors": [],
            "json_ld": [],
            "fonts": [],
            "social_links": [],
            "logo_urls": [],
            "palette": [],
            "framework_colors": [],
            "css_variables": [],
            "stylesheets_fetched": [],
            "warnings": warnings + [f"Response is {page['content_type'] or 'not HTML'}; no brand signals extracted."],
        }

    queue: list[str] = []
    seen = set()

    def enqueue(candidate: str) -> None:
        if len(queue) >= max_stylesheets or candidate in seen:
            return
        if reject_reason(candidate):
            return
        seen.add(candidate)
        queue.append(candidate)

    for href in sorted(linked_stylesheets(page["text"], page["final_url"]), key=lambda item: _stylesheet_rank(page["final_url"], item)):
        enqueue(href)

    sheets: dict[str, str] = {}
    index = 0
    while index < len(queue):
        href = queue[index]
        index += 1
        css_page = fetch(href, timeout=timeout, limit=MAX_CSS_BYTES)
        if not css_page["ok"]:
            warnings.append(f"Stylesheet failed: {href} ({css_page['error']})")
            continue
        if not _looks_like_css(css_page):
            warnings.append(f"Skipped non-CSS response: {href}")
            continue
        sheets[css_page["final_url"]] = css_page["text"]
        for imported in stylesheet_imports(css_page["text"], css_page["final_url"]):
            enqueue(imported)

    report = analyze(page["text"], page["final_url"], sheets)
    report["ok"] = True
    report["input_url"] = requested
    report["fetched_at"] = fetched_at
    report["http_status"] = page["status"]
    report["content_type"] = page["content_type"]
    report["warnings"] = warnings + report["warnings"]
    if not report["palette"]:
        report["warnings"].append("No colors were found in static HTML or linked CSS.")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Extract colors, fonts, social links, and schema from a restaurant website."
    )
    parser.add_argument("url", help="Homepage URL of the restaurant")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    parser.add_argument("--max-stylesheets", type=int, default=DEFAULT_STYLESHEETS)
    args = parser.parse_args(argv)
    report = collect(args.url, timeout=args.timeout, max_stylesheets=args.max_stylesheets)
    json.dump(report, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
