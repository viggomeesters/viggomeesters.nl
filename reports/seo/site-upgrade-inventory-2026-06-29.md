# Site Upgrade Inventory — viggomeesters.com

Generated: 2026-06-29

Source context:
- Vision: `docs/product-vision.md`
- AW plan: `system/agent-workflow/plans/20260629-225520-plan-viggomeesters-site-seo-usefulness-upgrade.json`
- Baseline files: `reports/seo/baseline.json`, `reports/seo/baseline.md`

## Executive read

- The site is structurally crawlable: public pages equal sitemap entries.
- Public pages: 234; sitemap entries: 234.
- SEO audit issue occurrences: 283; after the first project-page fix, `/vault-layer/` has no SEO issues and is classified under `project_pages`.
- Remaining issue buckets are generated skill-registry snippet-length issues; handle that as a registry template/metadata decision, not 191 manual edits.
- Freshness-risk terms exist on non-skill pages; source-check before changing current/best/latest/product recommendation claims.
- Homepage project cards currently do not directly route to GitHub when matched by `tile card` blocks; first-party project-page pattern is preserved.

## Page-class inventory

| Class | Pages | SEO issues | Missing JSON-LD | Thin |
|---|---:|---:|---:|---:|
| skills_registry | 191 | 248 | 191 | 0 |
| agent_workflow | 6 | 0 | 6 | 0 |
| guides_articles | 5 | 0 | 5 | 0 |
| homepage | 1 | 0 | 1 | 0 |
| methodologies | 7 | 0 | 7 | 0 |
| personal_knowledge_system | 8 | 0 | 8 | 0 |
| project_pages | 5 | 0 | 5 | 0 |
| seo_evergreen | 2 | 0 | 0 | 0 |
| signal_dashboards | 2 | 0 | 2 | 0 |
| tech_stack | 7 | 0 | 7 | 0 |

## Top SEO issue buckets

| Issue | Count |
|---|---:|
| short_description | 101 |
| short_title | 93 |
| long_description | 54 |
| duplicate_description | 35 |

## Priority non-skill pages

| Route | Class | Words | JSON-LD | Issues |
|---|---|---:|---:|---|
| / | homepage | 262 | 0 | none |
| /agent-brain/ | personal_knowledge_system | 395 | 0 | none |
| /agent-workflow-loop/ | agent_workflow | 292 | 0 | none |
| /agent-workflow/ | agent_workflow | 331 | 0 | none |
| /agent-workflow/2025-december-github-copilot-vscode/ | agent_workflow | 282 | 0 | none |
| /agent-workflow/2026-february-claude-code-life-os-x/ | agent_workflow | 269 | 0 | none |
| /agent-workflow/2026-january-claude-code-agent-brain/ | agent_workflow | 267 | 0 | none |
| /agent-workflow/2026-may-hermes-codex-viggo-agent-skills/ | agent_workflow | 252 | 0 | none |
| /cli-agents-guide/ | guides_articles | 1621 | 0 | none |
| /database-types-agent-first-systems/ | guides_articles | 801 | 0 | none |
| /foci-fear-of-choosing-incorrectly/ | guides_articles | 1150 | 0 | none |
| /funnel-analysis/ | methodologies | 1020 | 0 | none |

## Freshness/source-check scan

- Non-skill pages with current/best/latest/year/recommendation-like terms: 43.
- Treat these as review candidates, not automatic edit targets. Time-sensitive facts require fresh source checks before copy changes.

| Route | Class |
|---|---|
| /agent-brain/ | personal_knowledge_system |
| /agent-workflow/2025-december-github-copilot-vscode/ | agent_workflow |
| /agent-workflow/2026-february-claude-code-life-os-x/ | agent_workflow |
| /agent-workflow/2026-january-claude-code-agent-brain/ | agent_workflow |
| /agent-workflow/2026-may-hermes-codex-viggo-agent-skills/ | agent_workflow |
| /agent-workflow/ | agent_workflow |
| /agent-workflow-loop/ | agent_workflow |
| /beste-kattenbrokken/ | seo_evergreen |
| /beste-kattenvoer/ | seo_evergreen |
| /cli-agents-guide/ | guides_articles |
| /database-types-agent-first-systems/ | guides_articles |
| /foci-fear-of-choosing-incorrectly/ | guides_articles |
| /funnel-analysis/ | methodologies |
| /guides/ | guides_articles |
| /helicopter-to-detail/ | methodologies |
| / | homepage |
| /jsonl-agent-first-data-structures/ | guides_articles |
| /jsonl-vault-spike/ | project_pages |
| /knowledge-pyramid/ | methodologies |
| /mega-vault-viewer/ | project_pages |
| /methodologies/ | methodologies |
| /obsidian-plugins/ | project_pages |
| /personal-knowledge-system/agent-interfaces/ | personal_knowledge_system |
| /personal-knowledge-system/ | personal_knowledge_system |
| /personal-knowledge-system/markdown-vault/ | personal_knowledge_system |
| … | 18 more |

## Direct-GitHub homepage card guard

- No direct GitHub links found in homepage `tile card` blocks. Project-card first click remains first-party.

## Recommended next loop slices

1. Project page pattern pass: compare `/jsonl-vault-spike/`, `/vault-layer/`, `/sap-agent-context/`, `/mega-vault-viewer/`, `/obsidian-plugins/` for consistent status, boundary, CTA, and metadata.
2. Skills registry decision: either accept short generated registry snippets as intentional, or add registry-specific structured metadata/check exceptions instead of manually editing generated pages.
3. Freshness-source pass for evergreen/SEO pages only after source checks; do not bulk-touch sitemap dates.

## Vision alignment / non-goals

- Supports visitor-first project context before GitHub.
- Does not introduce framework/build/runtime architecture.
- Does not fake freshness or bulk-change dates.
- Keeps private vault/agent internals out of public copy; current guard remains enforced by `npm run check`.
