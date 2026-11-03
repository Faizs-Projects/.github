import { readdir, readFile, stat } from "node:fs/promises";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { client } from "../client.js";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const dist = join(root, "dist");
const failures = [];
const fail = (message) => failures.push(message);

const lin = (channel) => {
  const c = channel / 255;
  return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
};

const lum = (hex) => {
  const value = parseInt(hex.slice(1), 16);
  const r = lin((value >> 16) & 255);
  const g = lin((value >> 8) & 255);
  const b = lin(value & 255);
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
};

const contrast = (a, b) => {
  const [hi, lo] = [lum(a), lum(b)].sort((x, y) => y - x);
  return (hi + 0.05) / (lo + 0.05);
};

const css = await readFile(join(dist, "styles.css"), "utf8");
const token = (name) => {
  const match = css.match(new RegExp(`--${name}:\\s*(#[0-9a-fA-F]{6})`));
  if (!match) fail(`Missing color token --${name}`);
  return match?.[1];
};

const ground = token("ground");
const surface = token("surface");
const ink = token("ink");
const accent = token("accent");
const highlight = token("highlight");
const muted = token("muted");
const quiet = token("quiet");

const pairs = [
  ["ink on surface", ink, surface, 4.5],
  ["muted on surface", muted, surface, 4.5],
  ["surface on accent", surface, accent, 4.5],
  ["ink on highlight", ink, highlight, 4.5],
  ["surface on ground", surface, ground, 4.5],
  ["highlight on ground", highlight, ground, 4.5],
  ["quiet on ground", quiet, ground, 4.5],
];

for (const [label, a, b, minimum] of pairs) {
  if (!a || !b) continue;
  const ratio = contrast(a, b);
  if (ratio < minimum) fail(`${label} is ${ratio.toFixed(2)}:1, needs ${minimum}:1`);
}

const html = await readFile(join(dist, "index.html"), "utf8");
const h1s = html.match(/<h1[\s>]/g) || [];
if (h1s.length !== 1) fail(`Expected exactly one h1, found ${h1s.length}`);
if (!html.includes(client.hero.loudTop)) fail("Hero value prop missing");
if (!html.includes(`tel:${client.phone.tel}`)) fail("Phone link missing");
if (!html.includes(client.address.street)) fail("Street missing");
if (!html.includes(client.order.primary.href)) fail("DoorDash link missing");
if (!html.includes(client.order.secondary.href)) fail("Seamless link missing");
if ((html.split(client.order.primary.href).length - 1) < 4) {
  fail("Primary order link should repeat in the header, ticket, menu close, and dock");
}
if (!html.includes('content="noindex, nofollow"')) fail("Demo page is missing noindex");
if (!html.includes(client.affiliation)) fail("Independent-shop disclaimer missing");
if (!/clamp\(/.test(css)) fail("Type scale is missing clamp()");
if (!css.includes("prefers-reduced-motion")) fail("Reduced motion is not handled");

for (const needle of ["1978", "Ensenada", "La Puente", "taconazo.com", "lorem ipsum", "TODO", "FIXME"]) {
  if (html.toLowerCase().includes(needle.toLowerCase())) fail(`Unexpected copy: ${needle}`);
}

for (const category of client.menu) {
  for (const item of category.items) {
    if (!html.includes(item.name)) fail(`Menu item missing from the page: ${item.name}`);
  }
}

const walk = async (dir) => {
  const entries = await readdir(dir, { withFileTypes: true });
  let total = 0;
  for (const entry of entries) {
    const path = join(dir, entry.name);
    if (entry.isDirectory()) total += await walk(path);
    else total += (await stat(path)).size;
  }
  return total;
};

const bytes = await walk(dist);
if (bytes > 400_000) fail(`Dist is ${bytes} bytes. Budget is 400kb so a phone can load it fast.`);

const robots = await readFile(join(dist, "robots.txt"), "utf8");
if (!/Disallow:\s*\//.test(robots)) fail("robots.txt does not hide the demo");

if (failures.length) {
  console.error(failures.map((item) => `- ${item}`).join("\n"));
  process.exit(1);
}

console.log(`Preflight passed. ${pairs.length} contrast pairs, one h1, dist ${bytes} bytes.`);
