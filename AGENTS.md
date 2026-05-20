# Agent Notes

## Project

This repository is a static personal site for `viggomeesters.nl`, deployed on Vercel and linked to `github.com/viggomeesters/viggomeesters.nl`.

There is no framework and no build step. The production output is the repository root.

## Structure

- `index.html`: homepage.
- `*/index.html`: public subpages.
- `variant-*.html`: archived design variants. Keep them out of sitemap and search indexing.
- `og-image.png`, `profile.jpg`: root-level image assets.
- `sitemap.xml`, `robots.txt`, `vercel.json`: deploy and crawler configuration.
- `scripts/check-site.mjs`: dependency-free site quality checks for agents and humans.

## Local Commands

- `npm run check`: run all repo checks.
- `npm run serve`: serve the static site at `http://localhost:4173`.
- `npm run deploy:prod`: deploy the linked Vercel project to production.

## Editing Rules

- Keep the site static unless the task explicitly asks for a framework.
- Prefer small, direct edits to the relevant HTML file over introducing shared tooling.
- Preserve absolute public URLs as `https://viggomeesters.nl/...`.
- When adding a public page, update all of these together:
  - the page canonical URL,
  - `sitemap.xml`,
  - internal links that should expose it,
  - `scripts/check-site.mjs` expectations if needed.
- Do not commit `.vercel/`; it is local Vercel link metadata and is ignored.
- Do not expose `variant-*.html` as public canonical content.

## Deployment

The Vercel project is `viggos-projects-eac4720a/viggomeesters.nl`.

Custom domains are configured in Vercel, but DNS must point to Vercel:

```text
A viggomeesters.nl 76.76.21.21
A www.viggomeesters.nl 76.76.21.21
```

The canonical hostname is `viggomeesters.nl`; `www.viggomeesters.nl` should redirect to the apex domain.
