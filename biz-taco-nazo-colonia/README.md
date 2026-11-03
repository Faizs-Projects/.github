# Taco Nazo — Colonia

Demo site for the independent taqueria at 1331 St Georges Ave, Colonia, NJ. It is not a location of the Southern California Taco Nazo chain (`taconazo.com`), and it is not affiliated with Taco Nazo Corp.

The page has one job: start an order. Pickup and delivery go to the DoorDash store they already use. Seamless is the second link. The phone is `(732) 943-2006`. Nothing on this site takes a payment.

## Build

```bash
npm run build
node scripts/preflight.js
python3 -m http.server 4173 --directory dist
```

Facts live in `client.js`. `scripts/build.js` renders `dist/`. The page is `noindex` and `robots.txt` disallows crawlers, because this is a pitch demo.

Fonts are self-hosted (OFL): [Darker Grotesque](https://fonts.google.com/specimen/Darker+Grotesque) and [Outfit](https://fonts.google.com/specimen/Outfit).

## Deploy

Cloudflare Pages, project output directory `dist`, with the `_headers` file that sends `X-Robots-Tag: noindex`. This environment has no Cloudflare token, so the preview was not published from here.

## Repository

This site belongs in `Faizs-Projects/biz-taco-nazo-colonia` on branch `first-build`, with the topic `business-website`. The GitHub app on this run can only see `Faizs-Projects/.github` and cannot create repositories (`createRepository` is not permitted), so the files are on `first-build` in that profile repo until the real repo exists. Do not merge this into the organization profile.

```bash
gh repo create Faizs-Projects/biz-taco-nazo-colonia --private --clone=false
gh repo edit Faizs-Projects/biz-taco-nazo-colonia --add-topic business-website
git subtree split --prefix=biz-taco-nazo-colonia -b taco-nazo-site
git push git@github.com:Faizs-Projects/biz-taco-nazo-colonia.git taco-nazo-site:first-build
```
