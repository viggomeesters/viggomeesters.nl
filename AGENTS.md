# Agent Notes

## Project

This repository is a static personal site for `viggomeesters.com` (repo name still `viggomeesters.nl`), deployed on Vercel and linked to `github.com/viggomeesters/viggomeesters.nl`.

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
- Preserve absolute public URLs as `https://viggomeesters.com/...`.
- When adding a public page, update all of these together:
  - the page canonical URL,
  - `sitemap.xml`,
  - internal links that should expose it,
  - `scripts/check-site.mjs` expectations if needed.
- Do not commit `.vercel/`; it is local Vercel link metadata and is ignored.
- Do not expose `variant-*.html` as public canonical content.

## viggomeesters-site-upkeep

Use this repo-local process when asked to refresh, audit, add to, or otherwise
keep `viggomeesters.com` up to date. This is the repo-specific skill/procedure;
keep it here instead of creating a detached global skill unless the user
explicitly asks for one.

### Start

1. Read `AGENTS.md`, `package.json`, `scripts/check-site.mjs`, `sitemap.xml`,
   and the HTML files relevant to the requested change.
2. Check whether `.go-workflow/config.yaml` exists. If it does, follow the
   repo-local go-workflow route before editing. If it does not, proceed directly.
3. Run `git status --short` and preserve unrelated user changes.
4. Run `npm run check` as the baseline.

### Page Classes

- Homepage: `index.html`; identity, profile, project links, social links.
- Project pages: `agent-brain/`, `raycast-life-os/`.
- Agent workflow timeline pages: `agent-workflow/` and `agent-workflow/*/`.
- Project pages: `sap-agent-context/`, `mega-vault-viewer/`, `obsidian-plugins/`.
- Methodology pages: `methodologies/`, `helicopter-to-detail/`,
  `knowledge-pyramid/`, `funnel-analysis/`.
- SEO/evergreen pages: `beste-kattenvoer/`, `beste-kattenbrokken/`.
- Uses/tooling page: `uses/`.
- Obsidian portfolio page: `obsidian-plugins/`.
- Archived variants: `variant-*.html`; audit only, never expose as canonical
  content, sitemap entries, or normal navigation.

### Freshness Audit

For upkeep tasks, scan the relevant page class for:

- old years, stale dates, and sitemap `lastmod` drift;
- claims using words like `latest`, `current`, `best`, `new`, or year labels;
- outdated tool, product, price, employer, project, or external-link details;
- broken or missing internal links, canonical URLs, meta descriptions, OG/Twitter
  text, and JSON-LD dates where present;
- SEO pages whose recommendations, prices, products, or external references may
  have changed.

Browse and cite current sources before changing time-sensitive facts, product
recommendations, prices, availability, laws, standards, software/tool details, or
anything framed as current. Do not browse for stable personal copy unless the
task needs external verification.

### Edit Rules

- Keep changes small and in the relevant HTML/config file.
- When adding a public page, update the page canonical URL, `sitemap.xml`,
  relevant internal links, and `scripts/check-site.mjs` expectations together.
- When materially changing a public page, update only that page's sitemap
  `lastmod`; do not bulk-touch dates.
- Keep public canonical URLs on `https://viggomeesters.com/...`.
- Keep `robots.txt` and `vercel.json` protections for `variant-*` pages intact.
- Avoid adding scripts, dependencies, shared tooling, or a build step unless the
  repeated maintenance problem is concrete and the user agrees.

### Validation

- Always run `npm run check`.
- For visual/layout changes, run `npm run serve` and inspect
  `http://localhost:4173` in a browser at desktop and mobile widths.
- For content-only HTML changes, browser QA is optional unless the changed area
  could affect layout.
- Commit only scoped repo changes. Deploy with `npm run deploy:prod` only when
  the user explicitly asks for production deployment.

### Useful Prompts

- `Run viggomeesters-site-upkeep freshness audit for the public pages.`
- `Update the uses page using viggomeesters-site-upkeep.`
- `Add a public page using viggomeesters-site-upkeep and keep sitemap/canonical in sync.`
- `Prepare viggomeesters.com for deploy; do not deploy yet.`

## Deployment

The Vercel project is `viggos-projects-eac4720a/viggomeesters.nl`.

Custom domains are configured in Vercel, but DNS must point to Vercel:

```text
A viggomeesters.com 76.76.21.21
A www.viggomeesters.com 76.76.21.21
```

The canonical hostname is `viggomeesters.com`; `www.viggomeesters.com`, `viggomeesters.nl`, and `www.viggomeesters.nl` should redirect to the apex domain.
