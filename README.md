# viggomeesters.com

![version](https://img.shields.io/badge/version-v1.0-31addd)

Static personal website for Viggo Meesters: public projects, proof-first working methods, system pages, guides, and repo-local agent workflow experiments.

The production site is intentionally simple: plain HTML/CSS/JS, no framework, no build step, and Vercel serves the repository root.

## Purpose

This repo publishes the public surface of Viggo's work:

- project pages for public tools and repositories;
- methodology pages for proof-first delivery and source-backed synthesis;
- guides and evergreen reference pages;
- generated public-safe snapshots such as the skills registry;
- repo-local `.go/` workflow state for agent continuity.

Private vault content, client/customer data, secrets, and personal operational notes do not belong in this repository.

## Live site

- Canonical URL: <https://viggomeesters.com/>
- GitHub repository: <https://github.com/viggomeesters/viggomeesters.nl>
- Vercel project: `viggos-projects-eac4720a/viggomeesters.nl`

## Highlights

- Static site: no runtime framework and no build pipeline.
- Public-safe content model: publish only what can be reviewed in the repo.
- Built-in checks for canonical URLs, sitemap coverage, robots rules, structured data, favicon/manifest wiring, IndexNow, and Vercel assumptions.
- Repo-local `.go/` workflow pilot so a fresh clone can read direction, constraints, hierarchy, and next work without private vault context.

## Installation

Clone the repository and use the checked-in scripts:

```sh
git clone https://github.com/viggomeesters/viggomeesters.nl.git
cd viggomeesters.nl
```

There are no package dependencies for normal validation. `package.json` only defines scripts.

## Usage

Serve the site locally:

```sh
npm run serve
```

Open <http://localhost:4173>.

Run the normal site checks:

```sh
npm run check
npm run check:seo
```

For public repo-readiness and fresh-clone validation, use the local wrapper instead of GitHub Actions:

```sh
scripts/check.sh
```

This repository intentionally uses local-only validation because the site is static and has no dependency install/build step.

Submit the deployed sitemap to IndexNow after a production deploy:

```sh
npm run submit:indexnow
```

## Development

Follow `AGENTS.md` before editing. Keep changes small and static:

1. inspect `git status --short --branch`;
2. edit the relevant HTML/CSS/data file directly;
3. update `sitemap.xml`, canonical URLs, and `scripts/check-site.mjs` expectations when adding public pages;
4. run `npm run check`;
5. commit and push scoped changes.

For visible layout changes, run a local server and inspect desktop/mobile before shipping.

## Repo-local workflow

This repo carries pilot `.go/` workflow state so a fresh clone can read the site's direction, constraints, hierarchy, and next work without private vault context.

```sh
python3 ~/github/go-workflow-stack/cli/go.py route . --json
python3 ~/github/go-workflow-stack/cli/go.py status . --json
python3 ~/github/go-workflow-stack/cli/go.py validate .
python3 ~/github/go-workflow-stack/cli/go.py readback .
```

The stack owns the tooling; this repo owns its own `.go/` project state.

## Deployment

```sh
npm run deploy:prod
```

Deploy only after local checks pass. Vercel serves the repository root.

## DNS

The domains `viggomeesters.com`, `www.viggomeesters.com`, `viggomeesters.nl`, and `www.viggomeesters.nl` are attached to the Vercel project. DNS should point to Vercel:

```text
A viggomeesters.com 76.76.21.21
A www.viggomeesters.com 76.76.21.21
```

The canonical hostname is `viggomeesters.com`; secondary hostnames should redirect to the apex domain.

## Content map

- `index.html`: homepage.
- `agent-workflow/`: timeline index for AI workflow evolution.
- `agent-workflow/*/`: per-stage timeline pages for AI workflow evolution.
- `personal-knowledge-system/`: public knowledge-system overview.
- `personal-knowledge-system/*/`: public component pages for the knowledge-system layers.
- `raycast-life-os/`: older vault-first Life OS project page.
- `methodologies/`: methodology index.
- `guides/`: guides and articles index.
- `tech-stack/`: granular tech stack index.
- `skills/`: generated public snapshot of Hermes skill metadata.
- `uses/`: legacy stack and tools page.
- `sap-agent-context/`, `mega-vault-viewer/`, `obsidian-plugins/`: project pages.
- `beste-kattenvoer/`, `beste-kattenbrokken/`: cat food analysis pages.
- `variant-*.html`: archived design variants, excluded from indexing.

## Release

Releases are tracked on GitHub. The current first public release is `v1.0`.

## Security and privacy

Report security issues through `SECURITY.md`. Do not commit secrets, private vault exports, customer/client material, or private screenshots. The public site may describe personal systems at a high level, but operational private data stays outside this repository.

## License

This repository is released under the MIT License. You may use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies under the license terms. See `LICENSE` for the full text.
