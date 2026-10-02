## Faiz Projects

A small studio in Chicago. Two kinds of work live here, and they are kept apart by the
repo prefix — GitHub has no folders inside an organization, so `biz-` and `re-` do that job.

---

### `biz-` — business websites

Redesigns for small and medium businesses: dental and med spa, law and accounting,
home-service trades, restaurants, fitness, local retail.

Fast, accessible, conversion-focused, and designed for *that* business rather than
templated. One repo per client, so any single site can be worked on or handed over without
touching the others.

**[`biz-template`](https://github.com/Faizs-Projects/biz-template)** — the master template
every client site is cloned from. Astro, static output, design tokens, no framework.

```
gh repo create Faizs-Projects/biz-<client> --template Faizs-Projects/biz-template --private --clone
gh repo edit  Faizs-Projects/biz-<client> --add-topic business-website
```

→ [all business repos](https://github.com/orgs/Faizs-Projects/repositories?q=topic%3Abusiness-website)

---

### `re-` — property pages

Single-property listing pages for real estate agents. One page, one property, sent to
buyers and taken down when the house sells.

Each page is a deliberate dead end: no navigation, no links to other listings, nothing to
click but the agent's contact details. A buyer sent one address sees that house and nothing
else.

**[`re-template`](https://github.com/Faizs-Projects/re-template)** — reserved, not built
yet. Its README records the design decisions already made.

→ [all property repos](https://github.com/orgs/Faizs-Projects/repositories?q=topic%3Areal-estate)

---

### Conventions

| | |
|---|---|
| **Prefix** | `biz-` for business sites · `re-` for property pages |
| **Topics** | `business-website` · `real-estate` · `template` |
| **Visibility** | Private by default. Only this profile repo is public. |
| **Handover** | Each client or listing is its own repo, so it transfers on its own |
| **Stack** | Astro, static output, plain CSS with design tokens, GSAP for motion |

Every repo carries a `CLAUDE.md` with the studio's rules — design standards, the
new-client workflow, and a pre-flight checklist that has to pass before anything reaches a
client.

*Sort this page by **Name** rather than Last pushed and the two groups cluster on their own.*
