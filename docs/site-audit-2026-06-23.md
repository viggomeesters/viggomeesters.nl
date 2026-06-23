# Site audit go-loop ledger — 2026-06-23

## Baseline

- Repo: `/home/viggo/github/viggomeesters.nl`
- Canonical: `https://viggomeesters.com`
- Initial check: `npm run check` passed before edits

## Completed clusters

### Cluster 1 — taxonomy fix: Tech Stack vs Personal Knowledge System

- Removed `/tech-stack/knowledge-system/` because those items are Personal Knowledge System components, not generic tech stack.
- Updated `/tech-stack/` from 6 to 5 sections.
- Updated `/personal-knowledge-system/` hero copy to English and made taxonomy explicit.
- Updated homepage card copy for Personal Knowledge System.
- Validation: `npm run check` passed with 249 public pages.

### Cluster 2 — thin hub/detail pass: Guides + Tech Stack

- Enriched `/guides/` with shelf rules without turning it into a heavy systems block.
- Enriched `/tech-stack/` with an explicit boundary explaining why Personal Knowledge System components are not listed there.
- Enriched all 5 tech-stack detail pages with `Why this belongs in the stack` and `Maintenance boundary` sections.
- Browser-checked `/guides/`, `/tech-stack/`, `/tech-stack/hardware/`, and `/personal-knowledge-system/` for overflow and visual coherence.

### Cluster 3 — Personal Knowledge System detail pages

- Enriched all 5 component detail pages with `Maintenance rule` and `Proof signal` cards.
- Browser-checked `/personal-knowledge-system/markdown-vault/` for layout, cards, and overflow.

## Review stack verdict for completed clusters

- Audit: taxonomy drift fixed; Tech Stack no longer owns vault/schema/validation concepts.
- Recheck: Guides and detail pages are less thin while still compact.
- Devil: no fake metrics or private details added; generated skill pages untouched; no framework/build step introduced.
- Judge: pass for completed clusters; continue later with remaining thin project/methodology pages.

## Page class counts

- generated-skill: 212
- homepage: 1
- hub: 6
- methodology: 7
- other: 2
- project: 5
- seo-dutch: 2
- system-detail: 9
- tech-stack-detail: 5

## Findings index

| Status | Class | Route | Chars | Flags | Notes |
|---|---:|---|---:|---|---|
| ok | project | `/agent-brain/` | 2849 | Life OS label | Hermes + Life OS |
| thin | system-detail | `/agent-workflow/2025-december-github-copilot-vscode/` | 1276 | thin | From typing code to steering autocomplete. |
| thin | system-detail | `/agent-workflow/2026-february-claude-code-life-os-x/` | 1328 | thin; Life OS label | From repo sessions to a vault-backed operating layer. |
| thin | system-detail | `/agent-workflow/2026-january-claude-code-agent-brain/` | 1265 | thin | From editor helper to repo-operating agent. |
| thin | system-detail | `/agent-workflow/2026-may-hermes-codex-viggo-agent-skills/` | 1430 | thin | From one agent session to a command bus with procedural memory. |
| thin | hub | `/agent-workflow/` | 1565 | thin | From editor helper to routed agent cockpit. |
| thin | methodology | `/agent-workflow-loop/` | 729 | thin | Agent Workflow Loop |
| language | seo-dutch | `/beste-kattenbrokken/` | 13897 | Dutch? waarom, hoe, geen, niet | Beste Kattenbrokken 2026 |
| language | seo-dutch | `/beste-kattenvoer/` | 13909 | Dutch? mager, waarom, hoe, geen, niet | Beste Kattenvoer 2026 |
| ok | other | `/cli-agents-guide/` | 10353 |  | CLI Agents + Obsidian: A Practical Guide |
| ok | methodology | `/funnel-analysis/` | 6118 |  | Funnel Analysis |
| thin | hub | `/guides/` | 988 | thin | Practical writing, outside the systems grid. |
| ok | methodology | `/helicopter-to-detail/` | 4453 |  | Helicopter to Detail |
| thin | homepage | `/` | 1405 | thin | Viggo Meesters |
| ok | methodology | `/knowledge-pyramid/` | 6339 |  | Knowledge Pyramid |
| thin | project | `/mega-vault-viewer/` | 1092 | thin | A local-first viewer for large Markdown vaults. |
| thin | hub | `/methodologies/` | 1438 | thin | Methodologies |
| ok | project | `/obsidian-plugins/` | 3103 |  | Small plugins for making vaults more inspectable. |
| thin | system-detail | `/personal-knowledge-system/agent-interfaces/` | 1108 | thin | Agent interfaces |
| ok | hub | `/personal-knowledge-system/` | 2055 |  | The operating map of the system. |
| thin | system-detail | `/personal-knowledge-system/markdown-vault/` | 994 | thin | Markdown vault |
| thin | system-detail | `/personal-knowledge-system/schema-and-frontmatter/` | 1000 | thin | Schema &amp; frontmatter |
| thin | system-detail | `/personal-knowledge-system/system-folder/` | 994 | thin | system/ folder |
| thin | system-detail | `/personal-knowledge-system/validation-and-indexing/` | 997 | thin | Validation &amp; indexes |
| thin | methodology | `/proof-first-delivery/` | 712 | thin | Proof-first Delivery |
| ok | project | `/raycast-life-os/` | 2101 | Life OS label | Life OS |
| thin | project | `/sap-agent-context/` | 1088 | thin | SAP context that agents can actually use. |
| skip-generated | generated-skill | `/skills/agent-cli-delegation/` | 609 |  | agent-cli-delegation |
| skip-generated | generated-skill | `/skills/agent-correction-loop/` | 642 |  | agent-correction-loop |
| skip-generated | generated-skill | `/skills/agent-prompt-intelligence/` | 632 |  | agent-prompt-intelligence |
| skip-generated | generated-skill | `/skills/agent-workflow-lite/` | 432 |  | agent-workflow-lite |
| skip-generated | generated-skill | `/skills/agent-workflow-lite-execution/` | 590 |  | agent-workflow-lite-execution |
| skip-generated | generated-skill | `/skills/agent-workflow-lite-planning/` | 601 |  | agent-workflow-lite-planning |
| skip-generated | generated-skill | `/skills/agent-workflow-loop/` | 625 |  | agent-workflow-loop |
| skip-generated | generated-skill | `/skills/agent-workflow-resilience/` | 431 |  | agent-workflow-resilience |
| skip-generated | generated-skill | `/skills/airtable/` | 403 |  | airtable |
| skip-generated | generated-skill | `/skills/alteryx-flow-generator-operations/` | 621 |  | alteryx-flow-generator-operations |
| skip-generated | generated-skill | `/skills/apple-notes/` | 411 |  | apple-notes |
| skip-generated | generated-skill | `/skills/apple-platform-automation/` | 617 |  | apple-platform-automation |
| skip-generated | generated-skill | `/skills/apple-reminders/` | 420 |  | apple-reminders |
| skip-generated | generated-skill | `/skills/architecture-diagram/` | 430 |  | architecture-diagram |
| skip-generated | generated-skill | `/skills/arxiv/` | 383 |  | arxiv |
| skip-generated | generated-skill | `/skills/ascii-art/` | 390 |  | ascii-art |
| skip-generated | generated-skill | `/skills/ascii-video/` | 403 |  | ascii-video |
| skip-generated | generated-skill | `/skills/audio-to-obsidian-vault/` | 593 |  | audio-to-obsidian-vault |
| skip-generated | generated-skill | `/skills/audiocraft-audio-generation/` | 446 |  | audiocraft-audio-generation |
| skip-generated | generated-skill | `/skills/audit/` | 390 |  | audit |
| skip-generated | generated-skill | `/skills/audit-findings-to-aw-lite-plan/` | 629 |  | audit-findings-to-aw-lite-plan |
| skip-generated | generated-skill | `/skills/aw-lite-legacy-workflow-migration/` | 666 |  | aw-lite-legacy-workflow-migration |
| skip-generated | generated-skill | `/skills/aw-lite-loop-runtime/` | 619 |  | aw-lite-loop-runtime |
| skip-generated | generated-skill | `/skills/aw-lite-planning/` | 594 |  | aw-lite-planning |
| skip-generated | generated-skill | `/skills/baoyu-article-illustrator/` | 445 |  | baoyu-article-illustrator |
| skip-generated | generated-skill | `/skills/baoyu-comic/` | 403 |  | baoyu-comic |
| skip-generated | generated-skill | `/skills/baoyu-infographic/` | 411 |  | baoyu-infographic |
| skip-generated | generated-skill | `/skills/bertus-command-bus/` | 413 |  | bertus-command-bus |
| skip-generated | generated-skill | `/skills/bertus-email-gateway-ops/` | 525 |  | bertus-email-gateway-ops |
| skip-generated | generated-skill | `/skills/better/` | 377 |  | better |
| skip-generated | generated-skill | `/skills/blogwatcher/` | 403 |  | blogwatcher |
| skip-generated | generated-skill | `/skills/brainstorm/` | 389 |  | brainstorm |
| skip-generated | generated-skill | `/skills/business-architecture-explainer-reports/` | 688 |  | business-architecture-explainer-reports |
| skip-generated | generated-skill | `/skills/calendar-invite-email/` | 422 |  | calendar-invite-email |
| skip-generated | generated-skill | `/skills/caveman/` | 380 |  | caveman |
| skip-generated | generated-skill | `/skills/claude-code/` | 438 |  | claude-code |
| skip-generated | generated-skill | `/skills/claude-design/` | 408 |  | claude-design |
| skip-generated | generated-skill | `/skills/codebase-inspection/` | 454 |  | codebase-inspection |
| skip-generated | generated-skill | `/skills/codex/` | 421 |  | codex |
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
| skip-generated | generated-skill | `/skills/findmy/` | 394 |  | findmy |
| skip-generated | generated-skill | `/skills/fo-generation-quality-gates/` | 419 |  | fo-generation-quality-gates |
| skip-generated | generated-skill | `/skills/frontend/` | 375 |  | frontend |
| skip-generated | generated-skill | `/skills/frontend-slides/` | 593 |  | frontend-slides |
| skip-generated | generated-skill | `/skills/generated-document-review/` | 557 |  | generated-document-review |
| skip-generated | generated-skill | `/skills/gif-search/` | 382 |  | gif-search |
| skip-generated | generated-skill | `/skills/github-auth/` | 415 |  | github-auth |
| skip-generated | generated-skill | `/skills/github-code-review/` | 430 |  | github-code-review |
| skip-generated | generated-skill | `/skills/github-issues/` | 424 |  | github-issues |
| skip-generated | generated-skill | `/skills/github-operations/` | 606 |  | github-operations |
| skip-generated | generated-skill | `/skills/github-pr-workflow/` | 433 |  | github-pr-workflow |
| skip-generated | generated-skill | `/skills/github-repo-management/` | 442 |  | github-repo-management |
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
| skip-generated | generated-skill | `/skills/imessage/` | 405 |  | imessage |
| skip-generated | generated-skill | `/skills/improve/` | 380 |  | improve |
| ok | hub | `/skills/` | 28570 |  | Skills as reusable operating knowledge. |
| skip-generated | generated-skill | `/skills/job-application-package/` | 572 |  | job-application-package |
| skip-generated | generated-skill | `/skills/jupyter-live-kernel/` | 428 |  | jupyter-live-kernel |
| skip-generated | generated-skill | `/skills/kanban-codex-lane/` | 562 |  | kanban-codex-lane |
| skip-generated | generated-skill | `/skills/kanban-orchestrator/` | 698 |  | kanban-orchestrator |
| skip-generated | generated-skill | `/skills/kanban-worker/` | 628 |  | kanban-worker |
| skip-generated | generated-skill | `/skills/kanban-workflows/` | 575 |  | kanban-workflows |
| skip-generated | generated-skill | `/skills/landing-page-redesign/` | 580 |  | landing-page-redesign |
| skip-generated | generated-skill | `/skills/life-os-custom-harness/` | 495 | Life OS label | life-os-custom-harness |
| skip-generated | generated-skill | `/skills/life-os-hermes-workflow/` | 904 | Life OS label | life-os-hermes-workflow |
| skip-generated | generated-skill | `/skills/life-os-meeting-capture-pipeline/` | 686 | Life OS label | life-os-meeting-capture-pipeline |
| skip-generated | generated-skill | `/skills/life-os-memory-pipeline/` | 593 | Life OS label | life-os-memory-pipeline |
| skip-generated | generated-skill | `/skills/life-os-task/` | 538 | Life OS label | life-os-task |
| skip-generated | generated-skill | `/skills/linear/` | 396 |  | linear |
| skip-generated | generated-skill | `/skills/llama-cpp/` | 389 |  | llama-cpp |
| skip-generated | generated-skill | `/skills/llm-wiki/` | 393 |  | llm-wiki |
| skip-generated | generated-skill | `/skills/local-service-website-design/` | 596 |  | local-service-website-design |
| skip-generated | generated-skill | `/skills/loop/` | 387 |  | loop |
| skip-generated | generated-skill | `/skills/macos-computer-use/` | 379 |  | macos-computer-use |
| skip-generated | generated-skill | `/skills/manim-video/` | 395 |  | manim-video |
| skip-generated | generated-skill | `/skills/maps/` | 388 |  | maps |
| skip-generated | generated-skill | `/skills/master-tactician/` | 692 |  | master-tactician |
| skip-generated | generated-skill | `/skills/mem-ui-design/` | 478 |  | mem-ui-design |
| skip-generated | generated-skill | `/skills/minecraft-modpack-server/` | 433 |  | minecraft-modpack-server |
| skip-generated | generated-skill | `/skills/nano-pdf/` | 401 |  | nano-pdf |
| skip-generated | generated-skill | `/skills/native-mcp/` | 389 |  | native-mcp |
| skip-generated | generated-skill | `/skills/next/` | 371 |  | next |
| skip-generated | generated-skill | `/skills/next-improvements/` | 410 |  | next-improvements |
| skip-generated | generated-skill | `/skills/node-inspect-debugger/` | 476 |  | node-inspect-debugger |
| skip-generated | generated-skill | `/skills/notion/` | 396 |  | notion |
| skip-generated | generated-skill | `/skills/obliteratus/` | 392 |  | obliteratus |
| skip-generated | generated-skill | `/skills/obsidian/` | 401 |  | obsidian |
| skip-generated | generated-skill | `/skills/obsidian-plugin-portfolio/` | 619 |  | obsidian-plugin-portfolio |
| skip-generated | generated-skill | `/skills/ocr-and-documents/` | 422 |  | ocr-and-documents |
| skip-generated | generated-skill | `/skills/opencode/` | 432 |  | opencode |
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
| skip-generated | generated-skill | `/skills/python-debugpy/` | 442 |  | python-debugpy |
| skip-generated | generated-skill | `/skills/quality-audit/` | 414 |  | quality-audit |
| skip-generated | generated-skill | `/skills/recheck/` | 380 |  | recheck |
| skip-generated | generated-skill | `/skills/refactor/` | 399 |  | refactor |
| skip-generated | generated-skill | `/skills/requesting-code-review/` | 478 |  | requesting-code-review |
| skip-generated | generated-skill | `/skills/research-paper-writing/` | 431 |  | research-paper-writing |
| skip-generated | generated-skill | `/skills/runtime-release-browser-evidence/` | 595 |  | runtime-release-browser-evidence |
| skip-generated | generated-skill | `/skills/safe-output-compression/` | 576 |  | safe-output-compression |
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
| skip-generated | generated-skill | `/skills/viggo-life-os-vault/` | 609 | Life OS label | viggo-life-os-vault |
| skip-generated | generated-skill | `/skills/viggo-output/` | 581 |  | viggo-output |
| skip-generated | generated-skill | `/skills/viggo-reflect/` | 556 |  | viggo-reflect |
| skip-generated | generated-skill | `/skills/viggo-research-decision-support/` | 608 |  | viggo-research-decision-support |
| skip-generated | generated-skill | `/skills/viggomeesters-homepage-development/` | 639 |  | viggomeesters-homepage-development |
| skip-generated | generated-skill | `/skills/webhook-subscriptions/` | 418 |  | webhook-subscriptions |
| skip-generated | generated-skill | `/skills/webshop-cart-automation/` | 555 |  | webshop-cart-automation |
| skip-generated | generated-skill | `/skills/website-scrape-to-vault/` | 516 |  | website-scrape-to-vault |
| skip-generated | generated-skill | `/skills/weights-and-biases/` | 420 |  | weights-and-biases |
| skip-generated | generated-skill | `/skills/windows-laptop-quiet-tuning/` | 576 |  | windows-laptop-quiet-tuning |
| skip-generated | generated-skill | `/skills/windows-wsl-quiet-operations/` | 574 |  | windows-wsl-quiet-operations |
| skip-generated | generated-skill | `/skills/worldmonitor/` | 533 |  | worldmonitor |
| skip-generated | generated-skill | `/skills/writing-plans/` | 433 |  | writing-plans |
| skip-generated | generated-skill | `/skills/xurl/` | 388 |  | xurl |
| skip-generated | generated-skill | `/skills/youtube-content/` | 400 |  | youtube-content |
| skip-generated | generated-skill | `/skills/youtube-to-obsidian-vault/` | 637 |  | youtube-to-obsidian-vault |
| skip-generated | generated-skill | `/skills/yuanbao/` | 381 |  | yuanbao |
| thin | methodology | `/source-backed-synthesis/` | 804 | thin | Source-backed Synthesis |
| thin | tech-stack-detail | `/tech-stack/ai-agents/` | 1044 | thin | AI Agents |
| thin | tech-stack-detail | `/tech-stack/developer-tools/` | 1011 | thin | Developer Tools |
| thin | tech-stack-detail | `/tech-stack/hardware/` | 1197 | thin | Hardware |
| thin | tech-stack-detail | `/tech-stack/hosting-automation/` | 1064 | thin | Hosting &amp; Automation |
| thin | hub | `/tech-stack/` | 1274 | thin | Granular stack, easy to maintain. |
| thin | tech-stack-detail | `/tech-stack/software/` | 1061 | thin | Software |
| ok | other | `/uses/` | 2204 |  | Tech Stack |
| thin | methodology | `/vault-first-operating-model/` | 737 | thin | Vault-first Operating Model |
