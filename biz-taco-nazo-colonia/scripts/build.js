import { mkdir, readFile, writeFile, copyFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { client } from "../client.js";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const dist = join(root, "dist");

const esc = (value) =>
  String(value).replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  })[char]);

const hrefs = {
  maps: client.mapsUrl,
  doordash: client.order.primary.href,
  seamless: client.order.secondary.href,
};

const cityLine = `${client.address.city}, ${client.address.region} ${client.address.postal}`;

const external = (href, label, className = "") =>
  `<a class="${className}" href="${esc(href)}" target="_blank" rel="noopener noreferrer">${esc(label)}<span class="sr-only"> (opens in a new tab)</span></a>`;

const hoursList = client.hours
  .map(
    (row) =>
      `<li><span>${esc(row.label)}</span><span>${esc(row.display)}</span></li>`,
  )
  .join("");

const trust = client.trust
  .map((item) => external(hrefs[item.hrefKey], item.label))
  .join('<span aria-hidden="true">·</span>');

const plates = client.plates
  .map(
    (plate, index) => `<article class="plate">
      <p class="num">${String(index + 1).padStart(2, "0")}</p>
      <h3 lang="es">${esc(plate.name)}</h3>
      <p>${esc(plate.detail)}</p>
    </article>`,
  )
  .join("");

const menu = client.menu
  .map((category) => {
    const items = category.items
      .map((item) => {
        const lang = item.lang || "es";
        return `<li class="item"><strong lang="${lang}">${esc(item.name)}</strong><span>${esc(item.detail)}</span></li>`;
      })
      .join("");
    const note = category.note ? `<p class="note">${esc(category.note)}</p>` : "";
    return `<section class="cat" aria-labelledby="cat-${esc(category.name).toLowerCase().replace(/[^a-z0-9]+/g, "-")}">
      <h3 id="cat-${esc(category.name).toLowerCase().replace(/[^a-z0-9]+/g, "-")}">${esc(category.name)}</h3>
      ${note}
      <ul>${items}</ul>
    </section>`;
  })
  .join("");

const amenities = client.amenities.map((item) => `<li>${esc(item)}</li>`).join("");

const social = client.social
  .map((item) => `<li>${external(item.href, item.name)}</li>`)
  .join("");

const hoursSchema = client.hours.flatMap((row) =>
  row.days.map((day) => ({
    "@type": "OpeningHoursSpecification",
    dayOfWeek: day,
    opens: row.opens,
    closes: row.closes,
  })),
);

const jsonLd = {
  "@context": "https://schema.org",
  "@type": "Restaurant",
  name: client.name,
  servesCuisine: ["Mexican", "Taqueria"],
  telephone: client.phone.tel,
  address: {
    "@type": "PostalAddress",
    streetAddress: client.address.street,
    addressLocality: client.address.city,
    addressRegion: client.address.region,
    postalCode: client.address.postal,
    addressCountry: client.address.country,
  },
  geo: {
    "@type": "GeoCoordinates",
    latitude: client.geo.lat,
    longitude: client.geo.lng,
  },
  hasMenu: client.order.primary.href,
  openingHoursSpecification: hoursSchema,
  sameAs: client.social.map((item) => item.href),
  potentialAction: {
    "@type": "OrderAction",
    target: client.order.primary.href,
    deliveryMethod: ["http://purl.org/goodrelations/v1#DeliveryModePickUp", "http://purl.org/goodrelations/v1#DeliveryModeOwnFleet"],
  },
};

const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex, nofollow">
  <meta name="description" content="${esc(client.seoDescription)}">
  <meta name="theme-color" content="#F4EFE6">
  <meta property="og:title" content="${esc(client.seoTitle)}">
  <meta property="og:description" content="${esc(client.seoDescription)}">
  <meta property="og:type" content="website">
  <title>${esc(client.seoTitle)}</title>
  <link rel="icon" href="favicon.svg" type="image/svg+xml">
  <link rel="preload" href="fonts/darker-grotesque.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="fonts/outfit.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="styles.css">
  <script type="application/ld+json">${JSON.stringify(jsonLd).replace(/</g, "\\u003c")}</script>
</head>
<body id="top">
  <a class="skip" href="#order">Skip to ordering</a>
  <header class="site-header">
    <div class="wrap">
      <a class="brand" href="#top">${esc(client.name)}<span>${esc(client.place)}</span></a>
      <nav class="nav" aria-label="Primary">
        <a href="#menu">Menu</a>
        <a href="#visit">Visit</a>
        <a href="#order">Order</a>
      </nav>
      <div class="header-actions">
        <a class="header-phone" href="tel:${esc(client.phone.tel)}">${esc(client.phone.display)}</a>
        ${external(client.order.primary.href, "Order", "btn btn-ink")}
      </div>
    </div>
  </header>
  <main>
    <div class="hero wrap">
      <p class="kicker">${esc(client.hero.kicker)}</p>
      <h1>
        <span class="loud">${esc(client.hero.loudTop)}</span>
        <span class="whisper">${esc(client.hero.whisper)}</span>
        <span class="loud">${esc(client.hero.loudBottom)}</span>
      </h1>
      <p class="lede">${esc(client.hero.lede)}</p>
      <aside class="ticket" id="order" aria-label="Order and contact">
        <p class="ticket-kicker">Start an order</p>
        <p class="ticket-title">Order</p>
        <p class="ticket-detail">${esc(client.order.primary.detail)}</p>
        ${external(client.order.primary.href, client.order.primary.label, "btn btn-ink")}
        <p>${external(client.order.secondary.href, client.order.secondary.label)}</p>
        <p class="ticket-rating">${external(client.order.primary.href, client.trust[1].label)}</p>
        <hr class="tear">
        <p class="ticket-kicker">Call the counter</p>
        <a class="ticket-phone" href="tel:${esc(client.phone.tel)}">${esc(client.phone.display)}</a>
        <p>${esc(client.specialsNote)}</p>
        <address>
          ${esc(client.address.street)}<br>
          ${esc(cityLine)}
        </address>
        <p class="hours-line">${client.hours.map((row) => `${esc(row.label)} ${esc(row.display)}`).join("<br>")}</p>
        ${external(client.mapsUrl, "Directions", "btn btn-line")}
      </aside>
      <p class="meta">${trust}</p>
    </div>

    <section class="section" id="plates" aria-labelledby="plates-title">
      <div class="wrap">
        <div class="section-head">
          <p class="kicker">${esc(client.platesKicker)}</p>
          <h2 id="plates-title">${esc(client.platesTitle)}</h2>
        </div>
        <div class="plates">${plates}</div>
      </div>
    </section>

    <section class="section tight-top" id="menu" aria-labelledby="menu-title">
      <div class="wrap">
        <div class="section-head">
          <p class="kicker">${esc(client.menuKicker)}</p>
          <h2 id="menu-title">${esc(client.menuTitle)}</h2>
          <p>${esc(client.menuNote)}</p>
        </div>
        <div class="board">${menu}</div>
      </div>
    </section>

    <div class="order-row wrap">
      <p>${esc(client.orderRow)}</p>
      ${external(client.order.primary.href, client.order.primary.label, "btn btn-ink")}
      <a class="btn btn-line" href="tel:${esc(client.phone.tel)}">Call ${esc(client.phone.display)}</a>
    </div>

    <section class="band" id="visit" aria-labelledby="visit-title">
      <div class="wrap visit-grid">
        <div>
          <p class="kicker">${esc(client.visitKicker)}</p>
          <h2 id="visit-title">${esc(client.visitTitle)}</h2>
          <ul class="hours">${hoursList}</ul>
          <p class="note">${esc(client.hoursNote)}</p>
        </div>
        <div class="visit-action">
          <a class="phone-xl" href="tel:${esc(client.phone.tel)}">${esc(client.phone.display)}</a>
          <address>
            ${esc(client.name)}<br>
            ${esc(client.address.street)}<br>
            ${esc(cityLine)}
          </address>
          ${external(client.mapsUrl, "Get directions", "btn btn-lime")}
          <ul class="facts">${amenities}</ul>
        </div>
      </div>
    </section>
  </main>
  <footer class="site-footer">
    <div class="wrap">
      <ul class="footer-links">
        <li>${external(client.order.primary.href, client.order.primary.name)}</li>
        <li>${external(client.order.secondary.href, client.order.secondary.name)}</li>
        ${social}
        <li><a href="tel:${esc(client.phone.tel)}">${esc(client.phone.display)}</a></li>
        <li>${external(client.mapsUrl, "Map")}</li>
      </ul>
      <p class="fine">${esc(client.affiliation)}</p>
      <p class="fine">${esc(client.demoNote)}</p>
    </div>
  </footer>
  <div class="dock" hidden role="region" aria-label="Order or call">
    ${external(client.order.primary.href, "Order", "btn btn-lime")}
    <a class="btn btn-ghost" href="tel:${esc(client.phone.tel)}">Call</a>
  </div>
  <script>
    (function () {
      var dock = document.querySelector(".dock");
      var ticket = document.getElementById("order");
      if (!dock || !ticket || !("IntersectionObserver" in window)) return;
      var observer = new IntersectionObserver(function (entries) {
        dock.hidden = entries[0].isIntersecting;
      }, { rootMargin: "0px 0px -80px 0px", threshold: 0 });
      observer.observe(ticket);
    })();
  </script>
</body>
</html>
`;

await mkdir(join(dist, "fonts"), { recursive: true });
await writeFile(join(dist, "index.html"), html);
await copyFile(join(root, "styles", "site.css"), join(dist, "styles.css"));
await copyFile(join(root, "fonts", "darker-grotesque.woff2"), join(dist, "fonts", "darker-grotesque.woff2"));
await copyFile(join(root, "fonts", "outfit.woff2"), join(dist, "fonts", "outfit.woff2"));
await copyFile(join(root, "static", "favicon.svg"), join(dist, "favicon.svg"));
await writeFile(join(dist, "robots.txt"), "User-agent: *\nDisallow: /\n");
await writeFile(
  join(dist, "_headers"),
  "/*\n  X-Robots-Tag: noindex, nofollow\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n",
);

const css = await readFile(join(root, "styles", "site.css"), "utf8");
if (!css.includes("clamp(")) {
  throw new Error("Display type scale is missing clamp().");
}

console.log(`Built ${join(dist, "index.html")} (${html.length} bytes)`);
