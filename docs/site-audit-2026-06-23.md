# Site audit go-loop ledger — 2026-06-23

## Baseline

- Repo: `/home/viggo/github/viggomeesters.nl`
- Canonical: `https://viggomeesters.com`
- Latest refresh: Cluster E validation passed with `npm run check`.

## Completed clusters

### Cluster 1 — taxonomy fix: Tech Stack vs Personal Knowledge System

- Removed `/tech-stack/knowledge-system/`; updated `/tech-stack/`; made `/personal-knowledge-system/` the component map.

### Cluster 2 — thin hub/detail pass: Guides + Tech Stack

- Enriched `/guides/`, `/tech-stack/`, and all 5 tech-stack detail pages with boundaries and maintenance rules.

### Cluster 3 — Personal Knowledge System detail pages

- Enriched all 5 component detail pages with `Maintenance rule` and `Proof signal` cards.

### Cluster A — project pages

- Enriched project pages with status/proof, boundary, next-action, and current Personal Knowledge System terminology.

### Cluster B — methodology pages

- Enriched thin methodology pages with use/steps/example/failure/output/taxonomy sections and added hub guardrails.

### Cluster C — Agent Workflow pages

- Added a timeline reading guide, taxonomy boundary, and evidence standard to `/agent-workflow/`.
- Added `Stage interpretation` sections to all 4 stage pages.
- Added `Page role` notes to the 3 thinner stage pages.

### Cluster D — homepage, routes, docs, and variants

- Audited homepage taxonomy and route labels.
- Cleaned stale public `Life OS` visible labels in `/uses/` and homepage variant files while preserving legacy URLs/repo names where they are the actual address.

### Cluster E — generated Skills template

- Audited `/skills/`, sample detail pages, and `scripts/generate-skills-pages.py`.
- Fixed the generator to remove obsolete generated skill detail pages that are no longer in the active Hermes registry.
- Regenerated skills from the active enabled registry: 185 skills across 18 categories.
- Updated homepage Skills badge from 183 to 185.
- Verified public `skills-data.json` still excludes private `path` fields and search metadata remains present.

## Review stack verdict for completed clusters

- Audit: all requested clusters have been processed; generated Skills are handled through the generator/template only.
- Recheck: remaining thin pages are mostly deliberately compact hubs/details, not broken taxonomy or stale generated pages.
- Devil: no private SKILL.md runbooks or local paths were published; stale generated pages were pruned instead of manually curated.
- Judge: pass for Cluster E; loop complete for this pass.

## Page class counts

- generated-skill: 185
- homepage: 1
- hub: 6
- methodology: 7
- other: 2
- project: 5
- seo-dutch: 2
- system-detail: 9
- tech-stack-detail: 5

## Remaining thin non-generated pages

- `/guides/` — hub, 988 chars, Practical writing, outside the systems grid.
- `/` — homepage, 1405 chars, Viggo Meesters
- `/personal-knowledge-system/agent-interfaces/` — system-detail, 1108 chars, Agent interfaces
- `/personal-knowledge-system/markdown-vault/` — system-detail, 994 chars, Markdown vault
- `/personal-knowledge-system/schema-and-frontmatter/` — system-detail, 1000 chars, Schema & frontmatter
- `/personal-knowledge-system/system-folder/` — system-detail, 994 chars, system/ folder
- `/personal-knowledge-system/validation-and-indexing/` — system-detail, 997 chars, Validation & indexes
- `/tech-stack/ai-agents/` — tech-stack-detail, 1044 chars, AI Agents
- `/tech-stack/developer-tools/` — tech-stack-detail, 1011 chars, Developer Tools
- `/tech-stack/hardware/` — tech-stack-detail, 1197 chars, Hardware
- `/tech-stack/hosting-automation/` — tech-stack-detail, 1064 chars, Hosting & Automation
- `/tech-stack/` — hub, 1274 chars, Granular stack, easy to maintain.
- `/tech-stack/software/` — tech-stack-detail, 1061 chars, Software

## Findings index

| Status | Class | Route | Chars | Flags | Notes |
|---|---:|---|---:|---|---|
| ok | project | `/agent-brain/` | 2945 |  | Hermes + Personal Knowledge System |
| ok | system-detail | `/agent-workflow/2025-december-github-copilot-vscode/` | 1861 |  | From typing code to steering autocomplete. |
| ok | system-detail | `/agent-workflow/2026-february-claude-code-life-os-x/` | 1853 | legacy URL/name | From repo sessions to a vault-backed operating layer. |
| ok | system-detail | `/agent-workflow/2026-january-claude-code-agent-brain/` | 1814 |  | From editor helper to repo-operating agent. |
| ok | system-detail | `/agent-workflow/2026-may-hermes-codex-viggo-agent-skills/` | 1822 |  | From one agent session to a command bus with procedural memory. |
| ok | hub | `/agent-workflow/` | 2109 |  | From editor helper to routed agent cockpit. |
| ok | methodology | `/agent-workflow-loop/` | 1864 |  | Agent Workflow Loop |
| ok | seo-dutch | `/beste-kattenbrokken/` | 13897 |  | Beste Kattenbrokken 2026 |
| ok | seo-dutch | `/beste-kattenvoer/` | 13909 |  | Beste Kattenvoer 2026 |
| ok | other | `/cli-agents-guide/` | 10353 |  | CLI Agents + Obsidian: A Practical Guide |
| ok | methodology | `/funnel-analysis/` | 6118 |  | Funnel Analysis |
| thin | hub | `/guides/` | 988 | thin | Practical writing, outside the systems grid. |
| ok | methodology | `/helicopter-to-detail/` | 4453 |  | Helicopter to Detail |
| thin | homepage | `/` | 1405 | thin | Viggo Meesters |
| ok | methodology | `/knowledge-pyramid/` | 6339 |  | Knowledge Pyramid |
| ok | project | `/mega-vault-viewer/` | 1875 |  | A local-first viewer for large Markdown vaults. |
| ok | hub | `/methodologies/` | 1930 |  | Methodologies |
| ok | project | `/obsidian-plugins/` | 3531 |  | Small plugins for making vaults more inspectable. |
| thin | system-detail | `/personal-knowledge-system/agent-interfaces/` | 1108 | thin | Agent interfaces |
| ok | hub | `/personal-knowledge-system/` | 2055 |  | The operating map of the system. |
| thin | system-detail | `/personal-knowledge-system/markdown-vault/` | 994 | thin | Markdown vault |
| thin | system-detail | `/personal-knowledge-system/schema-and-frontmatter/` | 1000 | thin | Schema &amp; frontmatter |
| thin | system-detail | `/personal-knowledge-system/system-folder/` | 994 | thin | system/ folder |
| thin | system-detail | `/personal-knowledge-system/validation-and-indexing/` | 997 | thin | Validation &amp; indexes |
| ok | methodology | `/proof-first-delivery/` | 1803 |  | Proof-first Delivery |
| ok | project | `/raycast-life-os/` | 2403 | legacy URL/name | Personal Knowledge System starter |
| ok | project | `/sap-agent-context/` | 1960 |  | SAP context that agents can actually use. |
| skip-generated | generated-skill | `/skills/agent-cli-delegation/` | 609 |  | agent-cli-delegation |
| skip-generated | generated-skill | `/skills/agent-correction-loop/` | 642 |  | agent-correction-loop |
| skip-generated | generated-skill | `/skills/agent-prompt-intelligence/` | 632 |  | agent-prompt-intelligence |
| skip-generated | generated-skill | `/skills/agent-workflow-lite/` | 432 |  | agent-workflow-lite |
| skip-generated | generated-skill | `/skills/agent-workflow-lite-execution/` | 590 |  | agent-workflow-lite-execution |
| skip-generated | generated-skill | `/skills/agent-workflow-lite-planning/` | 601 |  | agent-workflow-lite-planning |
| skip-generated | generated-skill | `/skills/agent-workflow-loop/` | 625 |  | agent-workflow-loop |
| skip-generated | generated-skill | `/skills/airtable/` | 403 |  | airtable |
| skip-generated | generated-skill | `/skills/architecture-diagram/` | 430 |  | architecture-diagram |
| skip-generated | generated-skill | `/skills/arxiv/` | 383 |  | arxiv |
| skip-generated | generated-skill | `/skills/ascii-art/` | 390 |  | ascii-art |
| skip-generated | generated-skill | `/skills/ascii-video/` | 403 |  | ascii-video |
| skip-generated | generated-skill | `/skills/audio-to-obsidian-vault/` | 593 |  | audio-to-obsidian-vault |
| skip-generated | generated-skill | `/skills/audiocraft-audio-generation/` | 446 |  | audiocraft-audio-generation |
| skip-generated | generated-skill | `/skills/audit/` | 390 |  | audit |
| skip-generated | generated-skill | `/skills/aw-lite-loop-runtime/` | 619 |  | aw-lite-loop-runtime |
| skip-generated | generated-skill | `/skills/baoyu-article-illustrator/` | 445 |  | baoyu-article-illustrator |
| skip-generated | generated-skill | `/skills/baoyu-comic/` | 403 |  | baoyu-comic |
| skip-generated | generated-skill | `/skills/baoyu-infographic/` | 411 |  | baoyu-infographic |
| skip-generated | generated-skill | `/skills/bertus-command-bus/` | 413 |  | bertus-command-bus |
| skip-generated | generated-skill | `/skills/bertus-email-gateway-ops/` | 525 |  | bertus-email-gateway-ops |
| skip-generated | generated-skill | `/skills/better/` | 377 |  | better |
| skip-generated | generated-skill | `/skills/blogwatcher/` | 403 |  | blogwatcher |
| skip-generated | generated-skill | `/skills/brainstorm/` | 389 |  | brainstorm |
| skip-generated | generated-skill | `/skills/calendar-invite-email/` | 422 |  | calendar-invite-email |
| skip-generated | generated-skill | `/skills/caveman/` | 380 |  | caveman |
| skip-generated | generated-skill | `/skills/claude-design/` | 408 |  | claude-design |
| skip-generated | generated-skill | `/skills/codebase-inspection/` | 454 |  | codebase-inspection |
| skip-generated | generated-skill | `/skills/comfyui/` | 546 |  | comfyui |
| skip-generated | generated-skill | `/skills/compact-agent-output/` | 571 |  | compact-agent-output |
| skip-generated | generated-skill | `/skills/computer-use/` | 341 |  | computer-use |
| skip-generated | generated-skill | `/skills/consumption-kruidvat/` | 605 |  | consumption-kruidvat |
| skip-generated | generated-skill | `/skills/consumption-notenshop/` | 597 |  | consumption-notenshop |
| skip-generated | generated-skill | `/skills/data-audit/` | 512 |  | data-audit |
| skip-generated | generated-skill | `/skills/debug/` | 390 |  | debug |
| skip-generated | generated-skill | `/skills/debugging-hermes-tui-commands/` | 480 |  | debugging-hermes-tui-commands |
| skip-generated | generated-skill | `/skills/design-md/` | 398 |  | design-md |
| skip-generated | generated-skill | `/skills/devil/` | 390 |  | devil |
| skip-generated | generated-skill | `/skills/devil-review/` | 411 |  | devil-review |
| skip-generated | generated-skill | `/skills/document-photo-to-vault/` | 731 |  | document-photo-to-vault |
| skip-generated | generated-skill | `/skills/dogfood/` | 382 |  | dogfood |
| skip-generated | generated-skill | `/skills/dspy/` | 376 |  | dspy |
| skip-generated | generated-skill | `/skills/evaluating-llms-harness/` | 427 |  | evaluating-llms-harness |
| skip-generated | generated-skill | `/skills/excalidraw/` | 396 |  | excalidraw |
| skip-generated | generated-skill | `/skills/external-service-automation/` | 586 |  | external-service-automation |
| skip-generated | generated-skill | `/skills/fo-generation-quality-gates/` | 419 |  | fo-generation-quality-gates |
| skip-generated | generated-skill | `/skills/frontend/` | 375 |  | frontend |
| skip-generated | generated-skill | `/skills/frontend-product-ui/` | 504 |  | frontend-product-ui |
| skip-generated | generated-skill | `/skills/frontend-slides/` | 593 |  | frontend-slides |
| skip-generated | generated-skill | `/skills/generated-document-review/` | 557 |  | generated-document-review |
| skip-generated | generated-skill | `/skills/gif-search/` | 382 |  | gif-search |
| skip-generated | generated-skill | `/skills/github-operations/` | 606 |  | github-operations |
| skip-generated | generated-skill | `/skills/go-goal/` | 396 |  | go-goal |
| skip-generated | generated-skill | `/skills/go-loop/` | 396 |  | go-loop |
| skip-generated | generated-skill | `/skills/go-now/` | 393 |  | go-now |
| skip-generated | generated-skill | `/skills/go-plan/` | 396 |  | go-plan |
| skip-generated | generated-skill | `/skills/go-task/` | 396 |  | go-task |
| skip-generated | generated-skill | `/skills/go-workflow/` | 587 |  | go-workflow |
| skip-generated | generated-skill | `/skills/go-workflow-antislop/` | 456 |  | go-workflow-antislop |
| skip-generated | generated-skill | `/skills/go-workflow-audit/` | 535 |  | go-workflow-audit |
| skip-generated | generated-skill | `/skills/go-workflow-better/` | 538 |  | go-workflow-better |
| skip-generated | generated-skill | `/skills/go-workflow-build/` | 456 |  | go-workflow-build |
| skip-generated | generated-skill | `/skills/go-workflow-cancel/` | 516 |  | go-workflow-cancel |
| skip-generated | generated-skill | `/skills/go-workflow-devil/` | 459 |  | go-workflow-devil |
| skip-generated | generated-skill | `/skills/go-workflow-docs-ledger/` | 479 |  | go-workflow-docs-ledger |
| skip-generated | generated-skill | `/skills/go-workflow-git/` | 537 |  | go-workflow-git |
| skip-generated | generated-skill | `/skills/go-workflow-interview/` | 527 |  | go-workflow-interview |
| skip-generated | generated-skill | `/skills/go-workflow-plan/` | 475 |  | go-workflow-plan |
| skip-generated | generated-skill | `/skills/go-workflow-release/` | 535 |  | go-workflow-release |
| skip-generated | generated-skill | `/skills/go-workflow-route-claim/` | 494 |  | go-workflow-route-claim |
| skip-generated | generated-skill | `/skills/go-workflow-setup/` | 460 |  | go-workflow-setup |
| skip-generated | generated-skill | `/skills/go-workflow-ship/` | 450 |  | go-workflow-ship |
| skip-generated | generated-skill | `/skills/go-workflow-verify/` | 465 |  | go-workflow-verify |
| skip-generated | generated-skill | `/skills/godmode/` | 391 |  | godmode |
| skip-generated | generated-skill | `/skills/google-workspace/` | 427 |  | google-workspace |
| skip-generated | generated-skill | `/skills/grill-me/` | 383 |  | grill-me |
| skip-generated | generated-skill | `/skills/grill-with-docs/` | 420 |  | grill-with-docs |
| skip-generated | generated-skill | `/skills/hardening-pass/` | 401 |  | hardening-pass |
| skip-generated | generated-skill | `/skills/heartmula/` | 389 |  | heartmula |
| skip-generated | generated-skill | `/skills/hermes-agent/` | 421 |  | hermes-agent |
| skip-generated | generated-skill | `/skills/hermes-agent-skill-authoring/` | 479 |  | hermes-agent-skill-authoring |
| skip-generated | generated-skill | `/skills/hermes-operations-runbook/` | 574 |  | hermes-operations-runbook |
| skip-generated | generated-skill | `/skills/hermes-s6-container-supervision/` | 628 |  | hermes-s6-container-supervision |
| skip-generated | generated-skill | `/skills/himalaya/` | 374 |  | himalaya |
| skip-generated | generated-skill | `/skills/huggingface-hub/` | 411 |  | huggingface-hub |
| skip-generated | generated-skill | `/skills/humanizer/` | 387 |  | humanizer |
| skip-generated | generated-skill | `/skills/ideation/` | 384 |  | ideation |
| skip-generated | generated-skill | `/skills/improve/` | 380 |  | improve |
| ok | hub | `/skills/` | 28919 |  | Skills as reusable operating knowledge. |
| skip-generated | generated-skill | `/skills/job-application-package/` | 572 |  | job-application-package |
| skip-generated | generated-skill | `/skills/jupyter-live-kernel/` | 428 |  | jupyter-live-kernel |
| skip-generated | generated-skill | `/skills/kanban-codex-lane/` | 562 |  | kanban-codex-lane |
| skip-generated | generated-skill | `/skills/kanban-workflows/` | 575 |  | kanban-workflows |
| skip-generated | generated-skill | `/skills/landing-page-redesign/` | 580 |  | landing-page-redesign |
| skip-generated | generated-skill | `/skills/life-os-custom-harness/` | 495 | legacy URL/name | life-os-custom-harness |
| skip-generated | generated-skill | `/skills/life-os-hermes-workflow/` | 904 | legacy URL/name | life-os-hermes-workflow |
| skip-generated | generated-skill | `/skills/life-os-memory-pipeline/` | 593 | legacy URL/name | life-os-memory-pipeline |
| skip-generated | generated-skill | `/skills/life-os-task/` | 538 | legacy URL/name | life-os-task |
| skip-generated | generated-skill | `/skills/linear/` | 396 |  | linear |
| skip-generated | generated-skill | `/skills/llama-cpp/` | 389 |  | llama-cpp |
| skip-generated | generated-skill | `/skills/llm-wiki/` | 393 |  | llm-wiki |
| skip-generated | generated-skill | `/skills/local-service-website-design/` | 596 |  | local-service-website-design |
| skip-generated | generated-skill | `/skills/loop/` | 387 |  | loop |
| skip-generated | generated-skill | `/skills/manim-video/` | 395 |  | manim-video |
| skip-generated | generated-skill | `/skills/maps/` | 388 |  | maps |
| skip-generated | generated-skill | `/skills/master-tactician/` | 692 |  | master-tactician |
| skip-generated | generated-skill | `/skills/mem-ui-design/` | 478 |  | mem-ui-design |
| skip-generated | generated-skill | `/skills/minecraft-modpack-server/` | 433 |  | minecraft-modpack-server |
| skip-generated | generated-skill | `/skills/nano-pdf/` | 401 |  | nano-pdf |
| skip-generated | generated-skill | `/skills/native-mcp/` | 389 |  | native-mcp |
| skip-generated | generated-skill | `/skills/next/` | 371 |  | next |
| skip-generated | generated-skill | `/skills/next-improvements/` | 410 |  | next-improvements |
| skip-generated | generated-skill | `/skills/notion/` | 396 |  | notion |
| skip-generated | generated-skill | `/skills/obliteratus/` | 392 |  | obliteratus |
| skip-generated | generated-skill | `/skills/obsidian/` | 401 |  | obsidian |
| skip-generated | generated-skill | `/skills/obsidian-plugin-portfolio/` | 619 |  | obsidian-plugin-portfolio |
| skip-generated | generated-skill | `/skills/ocr-and-documents/` | 422 |  | ocr-and-documents |
| skip-generated | generated-skill | `/skills/openhue/` | 395 |  | openhue |
| skip-generated | generated-skill | `/skills/p5js/` | 374 |  | p5js |
| skip-generated | generated-skill | `/skills/pixel-art/` | 389 |  | pixel-art |
| skip-generated | generated-skill | `/skills/plan/` | 471 |  | plan |
| skip-generated | generated-skill | `/skills/pokemon-player/` | 397 |  | pokemon-player |
| skip-generated | generated-skill | `/skills/polymarket/` | 397 |  | polymarket |
| skip-generated | generated-skill | `/skills/popular-web-designs/` | 429 |  | popular-web-designs |
| skip-generated | generated-skill | `/skills/powerpoint/` | 407 |  | powerpoint |
| skip-generated | generated-skill | `/skills/pretext/` | 590 |  | pretext |
| skip-generated | generated-skill | `/skills/private-project-notes-repo-intake/` | 651 |  | private-project-notes-repo-intake |
| skip-generated | generated-skill | `/skills/product-tool-frontend-design/` | 583 |  | product-tool-frontend-design |
| skip-generated | generated-skill | `/skills/product-tool-ui/` | 622 |  | product-tool-ui |
| skip-generated | generated-skill | `/skills/prompt-evaluation/` | 611 |  | prompt-evaluation |
| skip-generated | generated-skill | `/skills/public-person-background-check-to-vault/` | 468 |  | public-person-background-check-to-vault |
| skip-generated | generated-skill | `/skills/public-repo-aw-lite-onboarding/` | 592 |  | public-repo-aw-lite-onboarding |
| skip-generated | generated-skill | `/skills/quality-audit/` | 414 |  | quality-audit |
| skip-generated | generated-skill | `/skills/recheck/` | 380 |  | recheck |
| skip-generated | generated-skill | `/skills/refactor/` | 399 |  | refactor |
| skip-generated | generated-skill | `/skills/research-paper-writing/` | 431 |  | research-paper-writing |
| skip-generated | generated-skill | `/skills/runtime-release-browser-evidence/` | 595 |  | runtime-release-browser-evidence |
| skip-generated | generated-skill | `/skills/sdp-alteryx-template-field-analysis/` | 558 |  | sdp-alteryx-template-field-analysis |
| skip-generated | generated-skill | `/skills/sdp-dashboard-sqlite-read-model/` | 569 |  | sdp-dashboard-sqlite-read-model |
| skip-generated | generated-skill | `/skills/segment-anything-model/` | 431 |  | segment-anything-model |
| skip-generated | generated-skill | `/skills/self-analysis-context-writeback/` | 576 |  | self-analysis-context-writeback |
| skip-generated | generated-skill | `/skills/selfimprove/` | 392 |  | selfimprove |
| skip-generated | generated-skill | `/skills/selfimprove-axe/` | 404 |  | selfimprove-axe |
| skip-generated | generated-skill | `/skills/serving-llms-vllm/` | 417 |  | serving-llms-vllm |
| skip-generated | generated-skill | `/skills/simplify-code/` | 423 |  | simplify-code |
| skip-generated | generated-skill | `/skills/sketch/` | 385 |  | sketch |
| skip-generated | generated-skill | `/skills/skill-command-routing/` | 566 |  | skill-command-routing |
| skip-generated | generated-skill | `/skills/skills-sh-curation/` | 624 |  | skills-sh-curation |
| skip-generated | generated-skill | `/skills/songsee/` | 383 |  | songsee |
| skip-generated | generated-skill | `/skills/songwriting-and-ai-music/` | 428 |  | songwriting-and-ai-music |
| skip-generated | generated-skill | `/skills/spike/` | 406 |  | spike |
| skip-generated | generated-skill | `/skills/spotify/` | 386 |  | spotify |
| skip-generated | generated-skill | `/skills/sqlite-bulk-import-debugging/` | 547 |  | sqlite-bulk-import-debugging |
| skip-generated | generated-skill | `/skills/subagent-driven-development/` | 476 |  | subagent-driven-development |
| skip-generated | generated-skill | `/skills/successive-website-redesigns/` | 594 |  | successive-website-redesigns |
| skip-generated | generated-skill | `/skills/systematic-debugging/` | 456 |  | systematic-debugging |
| skip-generated | generated-skill | `/skills/tdd/` | 384 |  | tdd |
| skip-generated | generated-skill | `/skills/teams-meeting-pipeline/` | 541 |  | teams-meeting-pipeline |
| skip-generated | generated-skill | `/skills/telegram-to-vault-router/` | 429 |  | telegram-to-vault-router |
| skip-generated | generated-skill | `/skills/temp-publisher/` | 630 |  | temp-publisher |
| skip-generated | generated-skill | `/skills/test-driven-development/` | 456 |  | test-driven-development |
| skip-generated | generated-skill | `/skills/touchdesigner-mcp/` | 531 |  | touchdesigner-mcp |
| skip-generated | generated-skill | `/skills/vault-aw-lite-operations/` | 410 |  | vault-aw-lite-operations |
| skip-generated | generated-skill | `/skills/vault-capture-operations/` | 585 |  | vault-capture-operations |
| skip-generated | generated-skill | `/skills/vault-context-memory-ingestion/` | 553 |  | vault-context-memory-ingestion |
| skip-generated | generated-skill | `/skills/vercel-app-versioning/` | 483 |  | vercel-app-versioning |
| skip-generated | generated-skill | `/skills/vercel-operations-runbook/` | 676 |  | vercel-operations-runbook |
| skip-generated | generated-skill | `/skills/verification-line/` | 546 |  | verification-line |
| skip-generated | generated-skill | `/skills/viggo-adr/` | 581 |  | viggo-adr |
| skip-generated | generated-skill | `/skills/viggo-agent-interaction-style/` | 569 |  | viggo-agent-interaction-style |
| skip-generated | generated-skill | `/skills/viggo-draft/` | 563 |  | viggo-draft |
| skip-generated | generated-skill | `/skills/viggo-life-os-vault/` | 609 | legacy URL/name | viggo-life-os-vault |
| skip-generated | generated-skill | `/skills/viggo-output/` | 581 |  | viggo-output |
| skip-generated | generated-skill | `/skills/viggo-reflect/` | 556 |  | viggo-reflect |
| skip-generated | generated-skill | `/skills/viggo-research-decision-support/` | 608 |  | viggo-research-decision-support |
| skip-generated | generated-skill | `/skills/viggomeesters-homepage-development/` | 639 |  | viggomeesters-homepage-development |
| skip-generated | generated-skill | `/skills/webhook-subscriptions/` | 418 |  | webhook-subscriptions |
| skip-generated | generated-skill | `/skills/webshop-cart-automation/` | 555 |  | webshop-cart-automation |
| skip-generated | generated-skill | `/skills/website-scrape-to-vault/` | 516 |  | website-scrape-to-vault |
| skip-generated | generated-skill | `/skills/weights-and-biases/` | 420 |  | weights-and-biases |
| skip-generated | generated-skill | `/skills/worldmonitor/` | 533 |  | worldmonitor |
| skip-generated | generated-skill | `/skills/writing-plans/` | 433 |  | writing-plans |
| skip-generated | generated-skill | `/skills/xurl/` | 388 |  | xurl |
| skip-generated | generated-skill | `/skills/youtube-content/` | 400 |  | youtube-content |
| skip-generated | generated-skill | `/skills/youtube-to-obsidian-vault/` | 637 |  | youtube-to-obsidian-vault |
| skip-generated | generated-skill | `/skills/yuanbao/` | 381 |  | yuanbao |
| ok | methodology | `/source-backed-synthesis/` | 1915 |  | Source-backed Synthesis |
| thin | tech-stack-detail | `/tech-stack/ai-agents/` | 1044 | thin | AI Agents |
| thin | tech-stack-detail | `/tech-stack/developer-tools/` | 1011 | thin | Developer Tools |
| thin | tech-stack-detail | `/tech-stack/hardware/` | 1197 | thin | Hardware |
| thin | tech-stack-detail | `/tech-stack/hosting-automation/` | 1064 | thin | Hosting &amp; Automation |
| thin | hub | `/tech-stack/` | 1274 | thin | Granular stack, easy to maintain. |
| thin | tech-stack-detail | `/tech-stack/software/` | 1061 | thin | Software |
| ok | other | `/uses/` | 2222 |  | Tech Stack |
| ok | methodology | `/vault-first-operating-model/` | 1838 |  | Vault-first Operating Model |
