# Vision Brief — viggomeesters.com Site Upgrade

## North Star
viggomeesters.com should become a consistently maintained, useful public map of Viggo’s projects, systems, methods, and writing, where every indexed page earns its place for a visitor and can be trusted as current enough to act on.

## Wedge
A proof-first personal operating-system website, not a generic portfolio, blog archive, or SEO content farm.

The site should make the route clear before the user clicks: live demos, project context, systems, methodologies, guides, tech stack, and topical SEO pages each have their own job. SEO is a distribution layer for useful pages, not the reason to publish weak pages.

## Target User / Audience
Primary visitors are technical collaborators, future clients/employers, agent-workflow builders, and search visitors who land on a specific guide or SEO page and need to understand quickly whether Viggo’s work is credible, current, and useful.

Painful moments:

- A visitor lands on a page that looks stale, thin, or visually inconsistent.
- A project card sends them straight to GitHub without context.
- A guide ranks or gets shared but does not answer the search intent well enough.
- A future agent wants to update the site but cannot tell which pages need freshness checks, source checks, or style cleanup.

## Core Promise
Every public page has a clear job, current-enough information, consistent visual language, and a next step that helps the visitor keep moving.

## Product Principles
- Visitor-first, not repo-first: first clicks should explain the thing before sending people into implementation details.
- Useful page or no page: every indexed page needs a concrete audience, answer, project boundary, or navigational role.
- Freshness is scoped: update stale claims and time-sensitive pages with evidence; do not bulk-touch dates just to look active.
- SEO follows usefulness: titles, metadata, internal links, schema, and search intent should reinforce pages that already deserve to exist.
- One visual system: dark bento/project-page language stays consistent across page classes, with controlled accents instead of random one-off styles.
- Public-safe by default: no private vault contents, local-only paths, client details, credentials, or agent runbook internals leak into public copy.
- Static stays static until pain is proven: add generators/checks only for repeated maintenance problems, not as default architecture creep.

## Non-Goals
- Do not turn the site into a broad blog CMS or content farm.
- Do not rewrite every page at once without a page-class audit and measurable reason.
- Do not chase SEO theater such as fake freshness, keyword stuffing, or thin programmatic pages.
- Do not introduce a framework, build system, database, or analytics stack unless the maintenance or measurement gap is concrete.
- Do not expose private Life OS/vault details, agent runbooks, raw skill contents, client specifics, or local environment paths.
- Do not make every page visually identical; consistency means shared hierarchy, tokens, and quality bar, not sameness.
- Do not publish “current/best/latest” claims without source checks or a dated review note.

## Load-Bearing Assumptions
| Assumption | Fails if | Cheapest evidence | Kill / pivot criterion |
|---|---|---|---|
| Visitors benefit from first-party project pages before GitHub. | Click paths or manual review show the intermediate pages add no clarity and feel like friction. | Review project-page sessions manually after adding a few pages; compare homepage card clarity and GitHub CTA placement. | If project pages only repeat GitHub README text, collapse them or make them richer with status, screenshots, examples, and boundaries. |
| SEO improvement comes from intent-fit and freshness, not more pages. | Search pages remain thin, outdated, or non-ranking despite metadata fixes. | Run a page-class SEO audit: title/meta, H1, intent match, internal links, schema, freshness risk, and current-source checks for time-sensitive pages. | If a page cannot answer a real query or navigational need, merge, noindex, or remove it from prominent navigation. |
| The static-site model is still enough for maintenance. | Updating page classes repeatedly requires copy-paste CSS, duplicated page shells, or error-prone sitemap edits. | Track repeated edits during the first upgrade pass and count duplicated mechanics. | If the same structure is patched across 5+ pages, add a small generator or shared template script while preserving static output. |
| Consistent style can be achieved by page-class templates. | Visual checks show drift between project pages, systems pages, guides, and SEO pages. | Screenshot representative pages at desktop/mobile and score them against shared typography, spacing, card, CTA, and metadata rules. | If drift remains high after manual cleanup, define page-class templates and a visual checklist before more content work. |
| “Up-to-date” can be maintained with scoped freshness rules. | Agents bulk-change dates, miss external facts, or leave old claims in SEO pages. | Add/check freshness markers: sitemap `lastmod`, visible reviewed dates where useful, stale-word scan, and source-backed update notes for time-sensitive pages. | If freshness cannot be verified cheaply, narrow the page scope or mark the page as archival instead of current. |

## First Proof
Before a broad rebuild, prove one full maintenance loop on a representative slice:

- Audit 8–12 pages across homepage, project, system, methodology, guide, SEO, and tech-stack classes.
- For each page, record: purpose, audience, freshness risk, SEO intent, metadata quality, internal-link role, visual consistency, and next-step clarity.
- Fix the highest-confidence issues in that slice.
- Add or tighten automated checks only where the audit found repeatable failures.
- Verify with `npm run check`, `npm run check:seo` if available, browser checks on desktop/mobile, and live/local proof.

Success criterion: the sample pages are all current-enough, visually coherent, internally linked, and have a clear visitor next step without expanding scope into a full redesign.

## First Build Slices
1. **Site inventory and page-class audit** — Generate a current route inventory with page type, title/meta, visible H1, sitemap `lastmod`, public-copy guard status, and thin/stale-risk flags.
2. **SEO and freshness baseline** — Run `npm run check`, `npm run check:seo`, external-link probes where relevant, and a stale-claim scan for `latest`, `current`, `best`, year labels, prices, tools, and external recommendations.
3. **Project-page upgrade slice** — Bring all public project cards/pages to the same pattern: human-readable context first, GitHub/live app as secondary CTA, status/boundary/current-source notes where useful.
4. **Guide/SEO slice** — Review guide and Dutch SEO pages for search intent, source freshness, titles/meta, structured data where appropriate, and visible reviewed-date semantics.
5. **Visual consistency slice** — Define and apply page-class style rules for project, hub, methodology, guide, SEO, and generated pages; verify desktop/mobile screenshots for representative pages.
6. **Internal-link and navigation slice** — Make sure homepage shelves, hubs, project pages, and guides route visitors intentionally without duplicate navigation or dead-end pages.
7. **Maintenance checks slice** — Add lightweight checks only for repeated issues: missing canonical/meta, stale visible years, public-copy leakage, broken internal links, sitemap drift, direct-GitHub project cards, and pages below the minimum useful-content threshold.

## Open Questions
- Should SEO optimization prioritize public technical pages around agent workflows/knowledge systems, or Dutch consumer SEO pages like kattenvoer first?
- Should every “current” page show a visible “reviewed” date, or should freshness live only in sitemap/source history except for time-sensitive pages?
- Which analytics source should decide success: Vercel Web Analytics, Search Console, manual live checks, or a lightweight local report?
- Should generated skills pages stay indexed as-is, be partially noindexed, or be treated as a public registry with stronger hub/search UX?
- Do project pages need screenshots/demo media, or is concise context plus CTA enough for the next pass?

## Next Planning Boundary
Run `go-plan viggomeesters.com SEO + usefulness upgrade` using this Vision Brief as source context.

The plan should not start with a full redesign. It should create a bounded audit-and-upgrade loop: inventory, sample proof, then page-class slices with verification after each slice.
