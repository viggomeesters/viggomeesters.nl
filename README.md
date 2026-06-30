# viggomeesters.com

![version](https://img.shields.io/badge/version-v1.0-31addd)

Static personal landing page hosted on Vercel.

## Local Development

```sh
npm run serve
```

Open `http://localhost:4173`.

## Checks

```sh
npm run check
npm run check:seo
```

The check script validates internal links, canonical URLs, sitemap coverage, crawler configuration, structured-data presence, favicon/manifest wiring, IndexNow setup, and Vercel routing assumptions.

## Search indexing

```sh
npm run submit:indexnow
```

The IndexNow submitter reads `sitemap.xml`, uses the public `indexnow-key.txt` verification file, and submits the current public URL list to IndexNow after deploy.

## Deploy

```sh
npm run deploy:prod
```

Vercel project: `viggos-projects-eac4720a/viggomeesters.nl`

GitHub repository: `github.com/viggomeesters/viggomeesters.nl`

## DNS

The domains `viggomeesters.com`, `www.viggomeesters.com`, `viggomeesters.nl`, and `www.viggomeesters.nl` are attached to the Vercel project. DNS should point to Vercel:

```text
A viggomeesters.com 76.76.21.21
A www.viggomeesters.com 76.76.21.21
```

The canonical hostname is `viggomeesters.com`; `www.viggomeesters.com`, `viggomeesters.nl`, and `www.viggomeesters.nl` redirect to the apex domain.

## Content Map

- `index.html`: homepage.
- `agent-workflow/`: timeline index for AI workflow evolution.
- `agent-workflow/*/`: per-stage timeline pages for the AI workflow evolution.
- `agent-brain/`: Hermes + Life OS AI workflow system page.
- `personal-knowledge-system/`: timeline index for the vault/knowledge-system evolution.
- `personal-knowledge-system/*/`: per-layer pages for the vault/knowledge-system evolution.
- `raycast-life-os/`: older vault-first Life OS project page.
- `methodologies/`: methodology index.
- `helicopter-to-detail/`, `knowledge-pyramid/`, `funnel-analysis/`, `source-backed-synthesis/`, `proof-first-delivery/`, `vault-first-operating-model/`, `agent-workflow-loop/`: methodology pages.
- `guides/`: guides and articles index.
- `cli-agents-guide/`: CLI agents guide.
- `tech-stack/`: granular tech stack index.
- `tech-stack/*/`: granular stack subpages for hardware, software, AI agents, dev tools, knowledge system, and hosting/automation.
- `skills/`: generated public snapshot of Hermes skill registry.
- `skills/*/`: per-skill public summary pages.
- `uses/`: legacy stack and tools page.
- `sap-agent-context/`: project page for the SAP Agent Context repository.
- `mega-vault-viewer/`: project page for the Mega Vault Viewer repository.
- `obsidian-plugins/`: public Obsidian plugin portfolio snapshot with GitHub source links.
- `beste-kattenvoer/`, `beste-kattenbrokken/`: cat food analysis pages.
- `variant-*.html`: archived design variants, excluded from indexing.
