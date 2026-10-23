---
name: brand-kit
description: Research one existing restaurant, cafe, bar, or bakery and return a brand kit grounded in its website, social profiles, reviews, and observed colors. Use when the user runs /brand-kit with a restaurant name, or asks for a restaurant brand kit, brand research, brand colors, or a sourced summary of how a food business presents itself.
argument-hint: "[restaurant name]"
allowed-tools: WebSearch WebFetch Read Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/extract_brand_signals.py *)
---

# Brand kit

Build a sourced brand kit for the existing food business named in the arguments. Report the brand they already use. Copy facts from pages you open and from the extractor JSON.

Restaurant: $ARGUMENTS

## Start

Read `${CLAUDE_SKILL_DIR}/references/output-template.md` before writing the reply.

If the restaurant line above is empty, ask which restaurant to research and stop.

Treat the whole argument as the query. A city or neighborhood in it is there to pick the location. Extra wording such as "focus on colors" does not change the deliverable: always return the full kit.

## Lock the business

Search the web for the official website and a maps or review listing that names the same business.

Proceed when the site and one independent listing agree on the name and the city. State that matched location in the kit.

When two different businesses remain plausible, list up to three candidates with city, cuisine, and URL, ask which one, and stop. Do not fill the template.

A chain with no location named gets a brand-level kit from the corporate site. Leave location-specific ratings as Not found and say in Gaps that scores differ by restaurant. A chain plus a city is that location: use the shared visual identity and that location's reviews.

Cafes, bakeries, bars, and food trucks are in scope when that is what was named. When the matching site is a different kind of business, go back to the candidate list.

## Gather

Open the official homepage, then the about, menu, and contact or location pages linked from it. Stop at four pages on the official site.

Run the extractor on the confirmed homepage URL:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/extract_brand_signals.py "https://the-official-homepage"
```

The script prints one JSON object. It reads static HTML and linked stylesheets. It does not run JavaScript.

Use the JSON this way:

- `palette[].hex` and `palette[].rgb` are the only color values that go in the kit. `neutral: true` means the color is black, white, gray, or a near-gray. Prefer a 6-digit hex. `framework_colors` are Bootstrap defaults set aside by the script; ignore them unless `palette` is empty.
- `css_variables` are the site's own tokens. Prefer a token that matches a palette hex when you name where the color was observed.
- `origins` may include `theme-color`, `css-variable`, `declaration`, and `svg`.
- `fonts` are families the CSS actually declares. The script drops generic families, icon fonts, fallbacks that sit behind a more specific family, and Arial or Helvetica when a more specific family is also present.
- `social_links` are candidates from the page and from schema `sameAs`. Keep a profile only after the URL matches this business.
- `json_ld` can supply the official name, cuisine, price range, phone, address, hours, menu URL, logo, and `sameAs`.
- An `aggregateRating` inside `json_ld` is a row in Reviews with platform "Website schema" and source "Page". It is not a Google rating.
- When `ok` is false, put `error` in Gaps and continue from pages you can open. Leave color cells as Not found.
- When `warnings` says no colors were found, the page is a script shell or blocked the fetch. Say that in the color paragraph and in Gaps.

Open each kept social profile. Record the handle, the URL, and the bio. Record a follower count only when the digits are visible on that page, and quote the count as shown.

For reviews, open Google and Yelp when a listing exists, plus one more platform the site points to (TripAdvisor, OpenTable, Resy, The Infatuation, Eater, or Michelin). Read the visible review text. In the Source column, write "Page" when the rating was on the review page, or "Search snippet" when it was only in a search result. A snippet rating stays labeled that way.

## Write the kit

Fill the template. The reply starts at its H1 and has no preface. Keep every heading, in order. Unknown cells say Not found.

Identity, address, hours, phone, and price come from the official site or its schema. When the schema and a page disagree, use the page and note the disagreement in Gaps.

The sheet follows the usual one-page brand guideline: logo versions, a named palette, type roles, brand elements, and applications. Social profiles and reviews come after that. Do not draw a fake board, and do not invent print colors.

Logo rows are versions you could see. Primary is the main wordmark. Secondary is a stacked, horizontal, or one-color version when a second version is on the site. Submark is an icon or monogram without the full name, when one exists. A version you did not see is Not found. Describe what the mark looks like and where it appears. Write a clearance or misuse rule only when the restaurant published one.

Colors:

- Name a swatch with the brand's own name when they published one. Otherwise use a short descriptive name and add "(descriptive)", such as "Deep burgundy (descriptive)".
- Build the table from colors you can see on the page or in the logo. Start with the highest-weight palette entries. Leave low-weight one-off declarations out of the table.
- Primary is the logo, header, or theme-color, preferring a non-neutral token.
- Background and Text are the page colors behind and in the copy.
- Accent is a saturated color used on buttons, links, or highlights.
- When the role is unclear, label the row Observed.
- The Observed on cell names the evidence, such as `theme-color` or `CSS variable --flame` or `homepage header`.
- RGB is copied from the extractor. Do not convert a hex yourself, and do not add CMYK or Pantone values.

Typography uses the extractor's families. Primary is the heading face, Secondary is the body face, and Complementary is a third face when one was declared. When headings and body cannot be told apart, put the families you found on Primary and write Not found for the roles you could not see.

Brand elements are patterns, illustrations, mascots, or icons that actually appear. Applications describe the real website, menu, social posts, and place (sign, dining room, packaging, uniform). Skip a surface you did not see.

Voice adjectives come from copy you read. The draft line is one sentence in that voice, and the template's "draft, not a published slogan" sentence stays. When the opened pages have too little copy to hear a voice, write Not found for the tone and the draft.

Quotes are contiguous excerpts under 30 words. An ellipsis is allowed only at the ends. Each quote names the platform and the reviewer name or date when they were shown.

Menu bullets are dishes named on a page you opened, each with the page. Application cells describe photographs and objects that were actually on the pages you opened.

Sources lists every URL that contributed, with what it supplied. Gaps lists anything the kit marks Not found that a reader would expect, including a blocked fetch, a script-only site, or a menu that did not load.

The research date is the UTC calendar date in `fetched_at`. When the extractor did not run, use today's date.
