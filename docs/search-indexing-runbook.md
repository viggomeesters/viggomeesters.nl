# Search indexing runbook

This runbook tracks the parts of `viggomeesters.com` discovery that cannot be forced by code.

## Current automated setup

- Canonical site: `https://viggomeesters.com/`
- `robots.txt` points to `https://viggomeesters.com/sitemap.xml`.
- `sitemap.xml` is public and contains all generated public pages.
- Homepage includes `Person` and `WebSite` JSON-LD.
- IndexNow is configured with a root `{key}.txt` verification file.
- `npm run submit:indexnow` submits all sitemap URLs to IndexNow.
- Hermes cron `viggomeesters.com search index monitor` checks search visibility every two days for eight runs.

## Manual property setup

Search Console and Bing Webmaster Tools require an authenticated browser session or API credentials. Do not fake this from repo code.

### Google Search Console

1. Open <https://search.google.com/search-console>.
2. Add a URL-prefix property: `https://viggomeesters.com/`.
3. Choose HTML file or DNS verification.
4. If Google gives an HTML file token, add that exact file to the repo root, run `npm run check`, push, then click Verify.
5. Submit sitemap: `https://viggomeesters.com/sitemap.xml`.

### Bing Webmaster Tools

1. Open <https://www.bing.com/webmasters>.
2. Add site: `https://viggomeesters.com/`.
3. Either import from Google Search Console after Google verification, or use Bing's HTML/XML/DNS verification method.
4. Submit sitemap: `https://viggomeesters.com/sitemap.xml`.
5. IndexNow is already configured; use `npm run submit:indexnow` after meaningful public page changes.

## Monitoring queries

Track these queries until indexed:

- `site:viggomeesters.com`
- `"viggomeesters.com"`
- `"Viggo Meesters" "viggomeesters.com"`
- `"Viggo Meesters"`

Expected early state: crawlable but not yet ranked. Treat no-result states as index/authority lag unless robots, sitemap, canonical, or live status fail.

## Authority signals

Owned public surfaces should point to the first-party site when relevant:

- GitHub profile website should be `https://viggomeesters.com/` when the GitHub token has `user` scope.
- Public repository homepage URLs should point to first-party project pages.
- Public repository READMEs should include a short `Project page:` link when there is a matching first-party page.

## Evidence checklist

Before saying indexing setup is healthy:

```bash
npm run check
npm run check:seo
npm run submit:indexnow
curl -I https://viggomeesters.com/
curl -I https://viggomeesters.com/sitemap.xml
curl -I https://viggomeesters.com/robots.txt
```

Report ranking as external/async. Never promise a #1 result.
