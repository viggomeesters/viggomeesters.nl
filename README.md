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
```

The check script validates internal links, canonical URLs, sitemap coverage, crawler configuration, and Vercel routing assumptions.

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
- `agent-brain/`: Hermes + Life OS AI workflow system page.
- `raycast-life-os/`: vault-first Life OS project page.
- `methodologies/`: methodology index.
- `helicopter-to-detail/`, `knowledge-pyramid/`, `funnel-analysis/`: methodology pages.
- `cli-agents-guide/`: CLI agents guide.
- `uses/`: stack and tools page.
- `obsidian-plugins/`: public Obsidian plugin portfolio snapshot with GitHub source links.
- `beste-kattenvoer/`, `beste-kattenbrokken/`: cat food analysis pages.
- `variant-*.html`: archived design variants, excluded from indexing.
