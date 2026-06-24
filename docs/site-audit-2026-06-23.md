# Site audit go-loop ledger — 2026-06-23

## Baseline

- Repo: `/home/viggo/github/viggomeesters.nl`
- Canonical: `https://viggomeesters.com`
- Latest refresh: Cluster F validation passed with `npm run check`.

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

### Cluster F — remaining thin hubs/details

- Enriched `/guides/` with reader promise, quality bar, candidate queue, editorial checklist, and navigation role.
- Added compact homepage shelf-orientation and reader-path notes clarifying Projects vs Systems vs Methodologies vs Skills vs Setup.
- Enriched all 5 Personal Knowledge System detail pages with input/output protocol, review checklist, concrete example, and public-boundary cards where needed.
- Enriched `/tech-stack/` with curation/proof/update rules and all 5 tech-stack detail pages with decision/proof, update trigger, concrete example, and public-boundary sections where needed.

## Review stack verdict for completed clusters

- Audit: no non-generated public page remains below the current 1800-character thin-page heuristic, excluding intentional Dutch SEO pages.
- Recheck: no taxonomy drift back into Tech Stack; PKS components remain under Personal Knowledge System.
- Devil: additions are public-safe and concrete; no private vault contents, runbook internals, credentials, or local-only paths were published.
- Judge: pass for Cluster F after mechanical and browser verification.

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

- None under the current 1800-character heuristic, excluding generated skills and Dutch SEO pages.

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
| ok | hub | `/guides/` | 2056 |  | Practical writing, outside the systems grid. |
| ok | methodology | `/helicopter-to-detail/` | 4453 |  | Helicopter to Detail |
| ok | homepage | `/` | 1857 |  | Viggo Meesters |
| ok | methodology | `/knowledge-pyramid/` | 6339 |  | Knowledge Pyramid |
| ok | project | `/mega-vault-viewer/` | 1875 |  | A local-first viewer for large Markdown vaults. |
| ok | hub | `/methodologies/` | 1930 |  | Methodologies |
| ok | project | `/obsidian-plugins/` | 3531 |  | Small plugins for making vaults more inspectable. |
| ok | system-detail | `/personal-knowledge-system/agent-interfaces/` | 1804 |  | Agent interfaces |
| ok | hub | `/personal-knowledge-system/` | 2055 |  | The operating map of the system. |
| ok | system-detail | `/personal-knowledge-system/markdown-vault/` | 1863 |  | Markdown vault |
| ok | system-detail | `/personal-knowledge-system/schema-and-frontmatter/` | 1872 |  | Schema &amp; frontmatter |
| ok | system-detail | `/personal-knowledge-system/system-folder/` | 1843 |  | system/ folder |
| ok | system-detail | `/personal-knowledge-system/validation-and-indexing/` | 1834 |  | Validation &amp; indexes |
| ok | methodology | `/proof-first-delivery/` | 1803 |  | Proof-first Delivery |
| ok | project | `/raycast-life-os/` | 2403 | legacy URL/name | Personal Knowledge System starter |
| ok | project | `/sap-agent-context/` | 1960 |  | SAP context that agents can actually use. |
| skip-generated | generated-skill | `/skills/agent-cli-delegation/` | 777 |  | agent-cli-delegation |
| skip-generated | generated-skill | `/skills/agent-correction-loop/` | 810 |  | agent-correction-loop |
| skip-generated | generated-skill | `/skills/agent-prompt-intelligence/` | 800 |  | agent-prompt-intelligence |
| skip-generated | generated-skill | `/skills/agent-workflow-lite/` | 600 |  | agent-workflow-lite |
| skip-generated | generated-skill | `/skills/agent-workflow-lite-execution/` | 758 |  | agent-workflow-lite-execution |
| skip-generated | generated-skill | `/skills/agent-workflow-lite-planning/` | 769 |  | agent-workflow-lite-planning |
| skip-generated | generated-skill | `/skills/agent-workflow-loop/` | 793 |  | agent-workflow-loop |
| skip-generated | generated-skill | `/skills/airtable/` | 571 |  | airtable |
| skip-generated | generated-skill | `/skills/architecture-diagram/` | 598 |  | architecture-diagram |
| skip-generated | generated-skill | `/skills/arxiv/` | 551 |  | arxiv |
| skip-generated | generated-skill | `/skills/ascii-art/` | 558 |  | ascii-art |
| skip-generated | generated-skill | `/skills/ascii-video/` | 571 |  | ascii-video |
| skip-generated | generated-skill | `/skills/audio-to-obsidian-vault/` | 761 |  | audio-to-obsidian-vault |
| skip-generated | generated-skill | `/skills/audiocraft-audio-generation/` | 614 |  | audiocraft-audio-generation |
| skip-generated | generated-skill | `/skills/audit/` | 558 |  | audit |
| skip-generated | generated-skill | `/skills/aw-lite-loop-runtime/` | 787 |  | aw-lite-loop-runtime |
| skip-generated | generated-skill | `/skills/baoyu-article-illustrator/` | 613 |  | baoyu-article-illustrator |
| skip-generated | generated-skill | `/skills/baoyu-comic/` | 571 |  | baoyu-comic |
| skip-generated | generated-skill | `/skills/baoyu-infographic/` | 579 |  | baoyu-infographic |
| skip-generated | generated-skill | `/skills/bertus-command-bus/` | 581 |  | bertus-command-bus |
| skip-generated | generated-skill | `/skills/bertus-email-gateway-ops/` | 693 |  | bertus-email-gateway-ops |
| skip-generated | generated-skill | `/skills/better/` | 545 |  | better |
| skip-generated | generated-skill | `/skills/blogwatcher/` | 571 |  | blogwatcher |
| skip-generated | generated-skill | `/skills/brainstorm/` | 557 |  | brainstorm |
| skip-generated | generated-skill | `/skills/calendar-invite-email/` | 590 |  | calendar-invite-email |
| skip-generated | generated-skill | `/skills/caveman/` | 548 |  | caveman |
| skip-generated | generated-skill | `/skills/claude-design/` | 576 |  | claude-design |
| skip-generated | generated-skill | `/skills/codebase-inspection/` | 622 |  | codebase-inspection |
| skip-generated | generated-skill | `/skills/comfyui/` | 714 |  | comfyui |
| skip-generated | generated-skill | `/skills/compact-agent-output/` | 739 |  | compact-agent-output |
| skip-generated | generated-skill | `/skills/computer-use/` | 509 |  | computer-use |
| skip-generated | generated-skill | `/skills/consumption-kruidvat/` | 773 |  | consumption-kruidvat |
| skip-generated | generated-skill | `/skills/consumption-notenshop/` | 765 |  | consumption-notenshop |
| skip-generated | generated-skill | `/skills/data-audit/` | 680 |  | data-audit |
| skip-generated | generated-skill | `/skills/debug/` | 558 |  | debug |
| skip-generated | generated-skill | `/skills/debugging-hermes-tui-commands/` | 648 |  | debugging-hermes-tui-commands |
| skip-generated | generated-skill | `/skills/design-md/` | 566 |  | design-md |
| skip-generated | generated-skill | `/skills/devil/` | 558 |  | devil |
| skip-generated | generated-skill | `/skills/devil-review/` | 579 |  | devil-review |
| skip-generated | generated-skill | `/skills/document-photo-to-vault/` | 899 |  | document-photo-to-vault |
| skip-generated | generated-skill | `/skills/dogfood/` | 550 |  | dogfood |
| skip-generated | generated-skill | `/skills/dspy/` | 544 |  | dspy |
| skip-generated | generated-skill | `/skills/evaluating-llms-harness/` | 595 |  | evaluating-llms-harness |
| skip-generated | generated-skill | `/skills/excalidraw/` | 564 |  | excalidraw |
| skip-generated | generated-skill | `/skills/external-service-automation/` | 754 |  | external-service-automation |
| skip-generated | generated-skill | `/skills/fo-generation-quality-gates/` | 587 |  | fo-generation-quality-gates |
| skip-generated | generated-skill | `/skills/frontend/` | 543 |  | frontend |
| skip-generated | generated-skill | `/skills/frontend-product-ui/` | 672 |  | frontend-product-ui |
| skip-generated | generated-skill | `/skills/frontend-slides/` | 761 |  | frontend-slides |
| skip-generated | generated-skill | `/skills/generated-document-review/` | 725 |  | generated-document-review |
| skip-generated | generated-skill | `/skills/gif-search/` | 550 |  | gif-search |
| skip-generated | generated-skill | `/skills/github-operations/` | 774 |  | github-operations |
| skip-generated | generated-skill | `/skills/go-goal/` | 564 |  | go-goal |
| skip-generated | generated-skill | `/skills/go-loop/` | 564 |  | go-loop |
| skip-generated | generated-skill | `/skills/go-now/` | 561 |  | go-now |
| skip-generated | generated-skill | `/skills/go-plan/` | 564 |  | go-plan |
| skip-generated | generated-skill | `/skills/go-task/` | 564 |  | go-task |
| skip-generated | generated-skill | `/skills/go-workflow/` | 755 |  | go-workflow |
| skip-generated | generated-skill | `/skills/go-workflow-antislop/` | 624 |  | go-workflow-antislop |
| skip-generated | generated-skill | `/skills/go-workflow-audit/` | 703 |  | go-workflow-audit |
| skip-generated | generated-skill | `/skills/go-workflow-better/` | 706 |  | go-workflow-better |
| skip-generated | generated-skill | `/skills/go-workflow-build/` | 624 |  | go-workflow-build |
| skip-generated | generated-skill | `/skills/go-workflow-cancel/` | 684 |  | go-workflow-cancel |
| skip-generated | generated-skill | `/skills/go-workflow-devil/` | 627 |  | go-workflow-devil |
| skip-generated | generated-skill | `/skills/go-workflow-docs-ledger/` | 647 |  | go-workflow-docs-ledger |
| skip-generated | generated-skill | `/skills/go-workflow-git/` | 705 |  | go-workflow-git |
| skip-generated | generated-skill | `/skills/go-workflow-interview/` | 695 |  | go-workflow-interview |
| skip-generated | generated-skill | `/skills/go-workflow-plan/` | 643 |  | go-workflow-plan |
| skip-generated | generated-skill | `/skills/go-workflow-release/` | 703 |  | go-workflow-release |
| skip-generated | generated-skill | `/skills/go-workflow-route-claim/` | 662 |  | go-workflow-route-claim |
| skip-generated | generated-skill | `/skills/go-workflow-setup/` | 628 |  | go-workflow-setup |
| skip-generated | generated-skill | `/skills/go-workflow-ship/` | 618 |  | go-workflow-ship |
| skip-generated | generated-skill | `/skills/go-workflow-verify/` | 633 |  | go-workflow-verify |
| skip-generated | generated-skill | `/skills/godmode/` | 559 |  | godmode |
| skip-generated | generated-skill | `/skills/google-workspace/` | 595 |  | google-workspace |
| skip-generated | generated-skill | `/skills/grill-me/` | 551 |  | grill-me |
| skip-generated | generated-skill | `/skills/grill-with-docs/` | 588 |  | grill-with-docs |
| skip-generated | generated-skill | `/skills/hardening-pass/` | 569 |  | hardening-pass |
| skip-generated | generated-skill | `/skills/heartmula/` | 557 |  | heartmula |
| skip-generated | generated-skill | `/skills/hermes-agent/` | 589 |  | hermes-agent |
| skip-generated | generated-skill | `/skills/hermes-agent-skill-authoring/` | 647 |  | hermes-agent-skill-authoring |
| skip-generated | generated-skill | `/skills/hermes-operations-runbook/` | 742 |  | hermes-operations-runbook |
| skip-generated | generated-skill | `/skills/hermes-s6-container-supervision/` | 796 |  | hermes-s6-container-supervision |
| skip-generated | generated-skill | `/skills/himalaya/` | 542 |  | himalaya |
| skip-generated | generated-skill | `/skills/huggingface-hub/` | 579 |  | huggingface-hub |
| skip-generated | generated-skill | `/skills/humanizer/` | 555 |  | humanizer |
| skip-generated | generated-skill | `/skills/ideation/` | 552 |  | ideation |
| skip-generated | generated-skill | `/skills/improve/` | 548 |  | improve |
| ok | hub | `/skills/` | 28919 |  | Skills as reusable operating knowledge. |
| skip-generated | generated-skill | `/skills/job-application-package/` | 740 |  | job-application-package |
| skip-generated | generated-skill | `/skills/jupyter-live-kernel/` | 596 |  | jupyter-live-kernel |
| skip-generated | generated-skill | `/skills/kanban-codex-lane/` | 730 |  | kanban-codex-lane |
| skip-generated | generated-skill | `/skills/kanban-workflows/` | 743 |  | kanban-workflows |
| skip-generated | generated-skill | `/skills/landing-page-redesign/` | 748 |  | landing-page-redesign |
| skip-generated | generated-skill | `/skills/life-os-custom-harness/` | 663 | legacy URL/name | life-os-custom-harness |
| skip-generated | generated-skill | `/skills/life-os-hermes-workflow/` | 1072 | legacy URL/name | life-os-hermes-workflow |
| skip-generated | generated-skill | `/skills/life-os-memory-pipeline/` | 761 | legacy URL/name | life-os-memory-pipeline |
| skip-generated | generated-skill | `/skills/life-os-task/` | 706 | legacy URL/name | life-os-task |
| skip-generated | generated-skill | `/skills/linear/` | 564 |  | linear |
| skip-generated | generated-skill | `/skills/llama-cpp/` | 557 |  | llama-cpp |
| skip-generated | generated-skill | `/skills/llm-wiki/` | 561 |  | llm-wiki |
| skip-generated | generated-skill | `/skills/local-service-website-design/` | 764 |  | local-service-website-design |
| skip-generated | generated-skill | `/skills/loop/` | 555 |  | loop |
| skip-generated | generated-skill | `/skills/manim-video/` | 563 |  | manim-video |
| skip-generated | generated-skill | `/skills/maps/` | 556 |  | maps |
| skip-generated | generated-skill | `/skills/master-tactician/` | 860 |  | master-tactician |
| skip-generated | generated-skill | `/skills/mem-ui-design/` | 646 |  | mem-ui-design |
| skip-generated | generated-skill | `/skills/minecraft-modpack-server/` | 601 |  | minecraft-modpack-server |
| skip-generated | generated-skill | `/skills/nano-pdf/` | 569 |  | nano-pdf |
| skip-generated | generated-skill | `/skills/native-mcp/` | 557 |  | native-mcp |
| skip-generated | generated-skill | `/skills/next/` | 539 |  | next |
| skip-generated | generated-skill | `/skills/next-improvements/` | 578 |  | next-improvements |
| skip-generated | generated-skill | `/skills/notion/` | 564 |  | notion |
| skip-generated | generated-skill | `/skills/obliteratus/` | 560 |  | obliteratus |
| skip-generated | generated-skill | `/skills/obsidian/` | 569 |  | obsidian |
| skip-generated | generated-skill | `/skills/obsidian-plugin-portfolio/` | 787 |  | obsidian-plugin-portfolio |
| skip-generated | generated-skill | `/skills/ocr-and-documents/` | 590 |  | ocr-and-documents |
| skip-generated | generated-skill | `/skills/openhue/` | 563 |  | openhue |
| skip-generated | generated-skill | `/skills/p5js/` | 542 |  | p5js |
| skip-generated | generated-skill | `/skills/pixel-art/` | 557 |  | pixel-art |
| skip-generated | generated-skill | `/skills/plan/` | 639 |  | plan |
| skip-generated | generated-skill | `/skills/pokemon-player/` | 565 |  | pokemon-player |
| skip-generated | generated-skill | `/skills/polymarket/` | 565 |  | polymarket |
| skip-generated | generated-skill | `/skills/popular-web-designs/` | 597 |  | popular-web-designs |
| skip-generated | generated-skill | `/skills/powerpoint/` | 575 |  | powerpoint |
| skip-generated | generated-skill | `/skills/pretext/` | 758 |  | pretext |
| skip-generated | generated-skill | `/skills/private-project-notes-repo-intake/` | 819 |  | private-project-notes-repo-intake |
| skip-generated | generated-skill | `/skills/product-tool-frontend-design/` | 751 |  | product-tool-frontend-design |
| skip-generated | generated-skill | `/skills/product-tool-ui/` | 790 |  | product-tool-ui |
| skip-generated | generated-skill | `/skills/prompt-evaluation/` | 779 |  | prompt-evaluation |
| skip-generated | generated-skill | `/skills/public-person-background-check-to-vault/` | 636 |  | public-person-background-check-to-vault |
| skip-generated | generated-skill | `/skills/public-repo-aw-lite-onboarding/` | 760 |  | public-repo-aw-lite-onboarding |
| skip-generated | generated-skill | `/skills/quality-audit/` | 582 |  | quality-audit |
| skip-generated | generated-skill | `/skills/recheck/` | 548 |  | recheck |
| skip-generated | generated-skill | `/skills/refactor/` | 567 |  | refactor |
| skip-generated | generated-skill | `/skills/research-paper-writing/` | 599 |  | research-paper-writing |
| skip-generated | generated-skill | `/skills/runtime-release-browser-evidence/` | 763 |  | runtime-release-browser-evidence |
| skip-generated | generated-skill | `/skills/sdp-alteryx-template-field-analysis/` | 726 |  | sdp-alteryx-template-field-analysis |
| skip-generated | generated-skill | `/skills/sdp-dashboard-sqlite-read-model/` | 737 |  | sdp-dashboard-sqlite-read-model |
| skip-generated | generated-skill | `/skills/segment-anything-model/` | 599 |  | segment-anything-model |
| skip-generated | generated-skill | `/skills/self-analysis-context-writeback/` | 744 |  | self-analysis-context-writeback |
| skip-generated | generated-skill | `/skills/selfimprove/` | 560 |  | selfimprove |
| skip-generated | generated-skill | `/skills/selfimprove-axe/` | 572 |  | selfimprove-axe |
| skip-generated | generated-skill | `/skills/serving-llms-vllm/` | 585 |  | serving-llms-vllm |
| skip-generated | generated-skill | `/skills/simplify-code/` | 591 |  | simplify-code |
| skip-generated | generated-skill | `/skills/sketch/` | 553 |  | sketch |
| skip-generated | generated-skill | `/skills/skill-command-routing/` | 734 |  | skill-command-routing |
| skip-generated | generated-skill | `/skills/skills-sh-curation/` | 792 |  | skills-sh-curation |
| skip-generated | generated-skill | `/skills/songsee/` | 551 |  | songsee |
| skip-generated | generated-skill | `/skills/songwriting-and-ai-music/` | 596 |  | songwriting-and-ai-music |
| skip-generated | generated-skill | `/skills/spike/` | 574 |  | spike |
| skip-generated | generated-skill | `/skills/spotify/` | 554 |  | spotify |
| skip-generated | generated-skill | `/skills/sqlite-bulk-import-debugging/` | 715 |  | sqlite-bulk-import-debugging |
| skip-generated | generated-skill | `/skills/subagent-driven-development/` | 644 |  | subagent-driven-development |
| skip-generated | generated-skill | `/skills/successive-website-redesigns/` | 762 |  | successive-website-redesigns |
| skip-generated | generated-skill | `/skills/systematic-debugging/` | 624 |  | systematic-debugging |
| skip-generated | generated-skill | `/skills/tdd/` | 552 |  | tdd |
| skip-generated | generated-skill | `/skills/teams-meeting-pipeline/` | 709 |  | teams-meeting-pipeline |
| skip-generated | generated-skill | `/skills/telegram-to-vault-router/` | 597 |  | telegram-to-vault-router |
| skip-generated | generated-skill | `/skills/temp-publisher/` | 798 |  | temp-publisher |
| skip-generated | generated-skill | `/skills/test-driven-development/` | 624 |  | test-driven-development |
| skip-generated | generated-skill | `/skills/touchdesigner-mcp/` | 699 |  | touchdesigner-mcp |
| skip-generated | generated-skill | `/skills/vault-aw-lite-operations/` | 578 |  | vault-aw-lite-operations |
| skip-generated | generated-skill | `/skills/vault-capture-operations/` | 753 |  | vault-capture-operations |
| skip-generated | generated-skill | `/skills/vault-context-memory-ingestion/` | 721 |  | vault-context-memory-ingestion |
| skip-generated | generated-skill | `/skills/vercel-app-versioning/` | 651 |  | vercel-app-versioning |
| skip-generated | generated-skill | `/skills/vercel-operations-runbook/` | 844 |  | vercel-operations-runbook |
| skip-generated | generated-skill | `/skills/verification-line/` | 714 |  | verification-line |
| skip-generated | generated-skill | `/skills/viggo-adr/` | 749 |  | viggo-adr |
| skip-generated | generated-skill | `/skills/viggo-agent-interaction-style/` | 737 |  | viggo-agent-interaction-style |
| skip-generated | generated-skill | `/skills/viggo-draft/` | 731 |  | viggo-draft |
| skip-generated | generated-skill | `/skills/viggo-life-os-vault/` | 777 | legacy URL/name | viggo-life-os-vault |
| skip-generated | generated-skill | `/skills/viggo-output/` | 749 |  | viggo-output |
| skip-generated | generated-skill | `/skills/viggo-reflect/` | 724 |  | viggo-reflect |
| skip-generated | generated-skill | `/skills/viggo-research-decision-support/` | 776 |  | viggo-research-decision-support |
| skip-generated | generated-skill | `/skills/viggomeesters-homepage-development/` | 807 |  | viggomeesters-homepage-development |
| skip-generated | generated-skill | `/skills/webhook-subscriptions/` | 586 |  | webhook-subscriptions |
| skip-generated | generated-skill | `/skills/webshop-cart-automation/` | 723 |  | webshop-cart-automation |
| skip-generated | generated-skill | `/skills/website-scrape-to-vault/` | 684 |  | website-scrape-to-vault |
| skip-generated | generated-skill | `/skills/weights-and-biases/` | 588 |  | weights-and-biases |
| skip-generated | generated-skill | `/skills/worldmonitor/` | 701 |  | worldmonitor |
| skip-generated | generated-skill | `/skills/writing-plans/` | 601 |  | writing-plans |
| skip-generated | generated-skill | `/skills/xurl/` | 556 |  | xurl |
| skip-generated | generated-skill | `/skills/youtube-content/` | 568 |  | youtube-content |
| skip-generated | generated-skill | `/skills/youtube-to-obsidian-vault/` | 805 |  | youtube-to-obsidian-vault |
| skip-generated | generated-skill | `/skills/yuanbao/` | 549 |  | yuanbao |
| ok | methodology | `/source-backed-synthesis/` | 1915 |  | Source-backed Synthesis |
| ok | tech-stack-detail | `/tech-stack/ai-agents/` | 1912 |  | AI Agents |
| ok | tech-stack-detail | `/tech-stack/developer-tools/` | 1914 |  | Developer Tools |
| ok | tech-stack-detail | `/tech-stack/hardware/` | 1966 |  | Hardware |
| ok | tech-stack-detail | `/tech-stack/hosting-automation/` | 1920 |  | Hosting &amp; Automation |
| ok | hub | `/tech-stack/` | 1900 |  | Granular stack, easy to maintain. |
| ok | tech-stack-detail | `/tech-stack/software/` | 1938 |  | Software |
| ok | other | `/uses/` | 2222 |  | Tech Stack |
| ok | methodology | `/vault-first-operating-model/` | 1838 |  | Vault-first Operating Model |
