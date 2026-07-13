#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "projects" / "data.json"
TIMELINE = ROOT / "timeline" / "index.html"
SITEMAP = ROOT / "sitemap.xml"
BASE_URL = "https://viggomeesters.com"
LASTMOD = "2026-07-13"
SITEMAP_START = "  <!-- BEGIN GENERATED PROJECT PAGES -->"
SITEMAP_END = "  <!-- END GENERATED PROJECT PAGES -->"


def e(value: str) -> str:
    return html.escape(value, quote=True)


def attrs(link: dict[str, object]) -> str:
    return ' target="_blank" rel="noopener"' if link.get("external") else ""


def head(title: str, description: str, route: str) -> str:
    return f"""  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(title)} — Viggo Meesters</title>
  <meta name="description" content="{e(description)}">
  <link rel="canonical" href="{BASE_URL}{route}">
  <meta name="theme-color" content="#090b10">
  <meta property="og:title" content="{e(title)} — Viggo Meesters">
  <meta property="og:description" content="{e(description)}">
  <meta property="og:type" content="article">
  <meta property="og:url" content="{BASE_URL}{route}">
  <meta property="og:image" content="{BASE_URL}/og-image.png">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{e(title)} — Viggo Meesters">
  <meta name="twitter:description" content="{e(description)}">
  <meta name="twitter:image" content="{BASE_URL}/og-image.png">
  <link rel="icon" href="/favicon.ico" sizes="any">
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">
  <link rel="manifest" href="/site.webmanifest">"""


DETAIL_CSS = """
    *,*::before,*::after{box-sizing:border-box}
    :root{--bg:#090b10;--surface:#0f131b;--line:#272e39;--line-soft:#1b222c;--text:#cbd2df;--muted:#818c9f;--bright:#f4f7fb;--accent:#f5a524;--accent-soft:rgba(245,165,36,.09);--sans:system-ui,-apple-system,'Segoe UI',sans-serif;--mono:ui-monospace,'SFMono-Regular','Cascadia Code',monospace}
    html{background:var(--bg);color-scheme:dark;-webkit-font-smoothing:antialiased}body{min-width:320px;margin:0;background:radial-gradient(ellipse 60% 34% at 88% -12%,rgba(245,165,36,.10),transparent 72%),var(--bg);color:var(--text);font:15px/1.7 var(--sans)}
    a{color:inherit}a:focus-visible{outline:2px solid var(--accent);outline-offset:5px}.page{width:min(1080px,calc(100% - 40px));margin:auto;padding:26px 0 72px}.topbar{display:flex;justify-content:space-between;align-items:center;gap:20px;min-height:46px}.back,.timeline-link{display:inline-flex;min-height:44px;align-items:center;color:var(--muted);font:500 .69rem var(--mono);text-decoration:none}.back:hover,.timeline-link:hover{color:var(--bright)}
    .hero{display:grid;grid-template-columns:minmax(0,1.45fr) minmax(260px,.55fr);gap:clamp(40px,8vw,108px);align-items:end;padding:clamp(62px,9vw,104px) 0 62px;border-bottom:1px solid var(--line)}.eyebrow{margin-bottom:18px;color:var(--accent);font:600 .68rem var(--mono);letter-spacing:.14em;text-transform:uppercase}.hero h1{max-width:760px;margin:0;color:var(--bright);font-size:clamp(3rem,8vw,7.2rem);font-weight:680;line-height:.89;letter-spacing:-.07em;text-wrap:balance}.lede{max-width:660px;margin:24px 0 0;color:#9ca6b8;font-size:clamp(1rem,1.5vw,1.16rem);line-height:1.7}.period{padding-top:20px;border-top:2px solid var(--accent)}.period span{display:block;color:var(--muted);font:500 .64rem var(--mono);letter-spacing:.12em;text-transform:uppercase}.period strong{display:block;margin-top:10px;color:var(--bright);font-size:1.06rem}
    .facts{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));border-left:1px solid var(--line);margin:0 0 66px}.fact{min-width:0;padding:22px;border-right:1px solid var(--line);border-bottom:1px solid var(--line)}.fact dt{color:var(--muted);font:500 .61rem var(--mono);letter-spacing:.1em;text-transform:uppercase}.fact dd{margin:9px 0 0;color:var(--bright);font-size:.86rem;overflow-wrap:anywhere}
    .content{display:grid;grid-template-columns:190px minmax(0,1fr);gap:clamp(36px,7vw,82px)}.section-label{color:var(--accent);font:500 .65rem var(--mono);letter-spacing:.12em;text-transform:uppercase}.copy-block+.copy-block{margin-top:54px;padding-top:52px;border-top:1px solid var(--line-soft)}.copy-block h2{margin:0 0 14px;color:var(--bright);font-size:clamp(1.5rem,3vw,2.25rem);letter-spacing:-.035em}.copy-block p{max-width:680px;margin:0;color:#9ba5b6}.gap-list{display:grid;grid-template-columns:1fr 1fr;gap:0;margin:22px 0 0;padding:0;border-top:1px solid var(--line);border-left:1px solid var(--line);list-style:none}.gap-list li{min-width:0;padding:18px 20px;border-right:1px solid var(--line);border-bottom:1px solid var(--line);color:#abb4c2;font-size:.84rem}.boundary{padding:22px;border-left:2px solid var(--accent);background:var(--accent-soft)}.links{display:flex;flex-wrap:wrap;gap:10px 24px;margin-top:22px}.links a{display:inline-flex;min-height:44px;align-items:center;color:var(--accent);font:500 .7rem var(--mono);text-underline-offset:5px}
    .project-nav{display:grid;grid-template-columns:1fr 1fr;gap:1px;margin-top:72px;background:var(--line);border:1px solid var(--line)}.project-nav a{display:block;min-width:0;padding:22px;background:var(--bg);text-decoration:none}.project-nav a:hover{background:var(--accent-soft)}.project-nav span{display:block;color:var(--muted);font:500 .6rem var(--mono);letter-spacing:.1em;text-transform:uppercase}.project-nav strong{display:block;margin-top:8px;color:var(--bright);overflow-wrap:anywhere}.project-nav .older{text-align:right}.footer{display:flex;justify-content:space-between;gap:20px;margin-top:42px;padding-top:22px;border-top:1px solid var(--line);color:var(--muted);font:400 .65rem var(--mono)}
    @media(max-width:760px){.page{width:min(100% - 24px,1080px);padding-top:14px}.hero{grid-template-columns:1fr;gap:36px;padding:48px 0}.period{max-width:360px}.facts{grid-template-columns:1fr 1fr;margin-bottom:52px}.content{grid-template-columns:1fr;gap:14px}.gap-list{grid-template-columns:1fr}.project-nav{grid-template-columns:1fr}.project-nav .older{text-align:left}.footer{flex-direction:column}}
    @media(max-width:420px){.timeline-link{display:none}.hero h1{font-size:2.75rem}.facts{grid-template-columns:1fr}.fact{padding:18px}.project-nav a{padding:18px}}
"""


INDEX_CSS = DETAIL_CSS + """
    .index-hero{max-width:800px;padding:clamp(58px,9vw,104px) 0 64px}.index-hero h1{margin:0;color:var(--bright);font-size:clamp(3.4rem,9vw,7.4rem);line-height:.88;letter-spacing:-.075em}.index-hero p{max-width:650px;margin:25px 0 0;color:#9ca6b8;font-size:1.08rem}.index-meta{margin-top:18px;color:var(--accent);font:500 .67rem var(--mono)}.project-list{border-top:1px solid var(--line)}.project-row{display:grid;grid-template-columns:150px minmax(0,1fr) auto;gap:28px;align-items:center;min-height:122px;padding:22px 0;border-bottom:1px solid var(--line);text-decoration:none}.project-row:hover .project-title{color:var(--accent)}.project-date{color:var(--muted);font:500 .66rem var(--mono)}.project-title{display:block;color:var(--bright);font-size:clamp(1.2rem,2.4vw,1.85rem);font-weight:620;line-height:1.1;letter-spacing:-.035em}.project-role{display:block;margin-top:8px;color:var(--muted);font-size:.78rem}.project-arrow{color:var(--accent);font-size:1.2rem}.additions{display:grid;grid-template-columns:190px minmax(0,1fr);gap:50px;margin-top:72px;padding-top:48px;border-top:1px solid var(--line)}.additions h2{margin:0;color:var(--bright);font-size:1.5rem}.additions p{max-width:650px;margin:0;color:var(--muted)}
    @media(max-width:680px){.project-row{grid-template-columns:1fr auto;gap:8px}.project-date{grid-column:1}.project-copy{grid-column:1}.project-arrow{grid-column:2;grid-row:1 / 3}.additions{grid-template-columns:1fr;gap:12px}}
"""


def render_detail(project: dict, newer: dict | None, older: dict | None) -> str:
    route = f'/projects/{project["slug"]}/'
    description = f'{project["title"]}: {project["summary"]}. Role: {project["role"]}.'
    if len(description) < 80:
        description += " This record covers the project scope, period, role, and professional context."
    seo_title = project["title"]
    if len(f'{seo_title} — Viggo Meesters') < 25:
        seo_title += " project"
    gaps = "".join(f"<li>{e(item)}</li>" for item in project["detail_gaps"])
    links = "".join(
        f'<a href="{e(link["href"])}"{attrs(link)}>{e(link["label"])} &rarr;</a>'
        for link in project["links"]
    )
    nav = []
    if newer:
        nav.append(f'<a href="/projects/{newer["slug"]}/"><span>Newer project</span><strong>{e(newer["title"])}</strong></a>')
    else:
        nav.append('<a href="/timeline/"><span>Newer work</span><strong>Return to the timeline</strong></a>')
    if older:
        nav.append(f'<a class="older" href="/projects/{older["slug"]}/"><span>Older project</span><strong>{e(older["title"])}</strong></a>')
    else:
        nav.append('<a class="older" href="/projects/"><span>Project archive</span><strong>View all projects</strong></a>')
    structured = json.dumps({"@context":"https://schema.org","@type":"CreativeWork","name":project["title"],"description":project["summary"],"author":{"@type":"Person","name":"Viggo Meesters","url":f"{BASE_URL}/"},"url":f"{BASE_URL}{route}"}, ensure_ascii=False).replace("</", "<\\/")
    return f"""<!doctype html>
<html lang="en">
<head>
{head(seo_title, description, route)}
  <script type="application/ld+json">{structured}</script>
  <style>{DETAIL_CSS}  </style>
  <script defer src="/_vercel/insights/script.js"></script>
</head>
<body data-project-slug="{e(project["slug"])}">
  <main class="page">
    <nav class="topbar" aria-label="Project navigation"><a class="back" href="/projects/">&larr; all projects</a><a class="timeline-link" href="/timeline/">View timeline &rarr;</a></nav>
    <header class="hero"><div><div class="eyebrow">{e(project["context"])}</div><h1>{e(project["title"])}</h1><p class="lede">{e(project["summary"])}.</p></div><div class="period"><span>Period</span><strong>{e(project["period"])}</strong></div></header>
    <dl class="facts"><div class="fact"><dt>Role</dt><dd>{e(project["role"])}</dd></div><div class="fact"><dt>Linked to</dt><dd>{e(project["linked_to"])}</dd></div><div class="fact"><dt>Organisation</dt><dd>{e(project["organization"])}</dd></div><div class="fact"><dt>Context</dt><dd>{e(project["context"])}</dd></div></dl>
    <section class="content"><div class="section-label">Project record</div><div>
      <div class="copy-block"><h2>Known scope</h2><p>{e(project["summary"])}. The role recorded for this period was {e(project["role"])}.</p></div>
      <div class="copy-block"><h2>What can be shown</h2><div class="boundary"><p>This page contains the high-level project facts currently available in the professional record. Client data, private repositories, internal artifacts, and unverified outcomes are intentionally excluded.</p>{f'<div class="links">{links}</div>' if links else ''}</div></div>
      <div class="copy-block" data-detail-status="needs-input"><h2>What can still be added</h2><p>These details would make the project story more useful without requiring confidential material.</p><ul class="gap-list">{gaps}</ul></div>
    </div></section>
    <nav class="project-nav" aria-label="Adjacent projects">{''.join(nav)}</nav>
    <footer class="footer"><span>&copy; 2026 Viggo Meesters</span><span><a href="/projects/">Projects</a> · <a href="/timeline/">Timeline</a> · <a href="mailto:38-isles-effete@icloud.com">Email</a></span></footer>
  </main>
</body>
</html>
"""


def render_index(projects: list[dict]) -> str:
    rows = "".join(
        f'<a class="project-row" href="/projects/{p["slug"]}/"><span class="project-date">{e(p["period"])}</span><span class="project-copy"><span class="project-title">{e(p["title"])}</span><span class="project-role">{e(p["role"])} · {e(p["linked_to"])}</span></span><span class="project-arrow" aria-hidden="true">&nearr;</span></a>'
        for p in projects
    )
    return f"""<!doctype html>
<html lang="en">
<head>
{head("Projects", "A complete index of 36 professional and personal projects by Viggo Meesters, from 2014 to now.", "/projects/")}
  <style>{INDEX_CSS}  </style>
  <script defer src="/_vercel/insights/script.js"></script>
</head>
<body>
  <main class="page">
    <nav class="topbar" aria-label="Page navigation"><a class="back" href="/">&larr; viggomeesters.com</a><a class="timeline-link" href="/timeline/">View timeline &rarr;</a></nav>
    <header class="index-hero"><h1>Projects.</h1><p>Every project in the professional record, with its own first-party page. Known facts stay separate from details that still need your input.</p><div class="index-meta">36 projects · 2014 to now · newest first</div></header>
    <section class="project-list" aria-label="All projects">{rows}</section>
    <section class="additions"><h2>What can still be added</h2><p>The pages already contain period, role, organisation, context, and known scope. The next enrichment pass can add your specific decisions, methods, outcomes, tools, screenshots, and lessons project by project.</p></section>
    <footer class="footer"><span>&copy; 2026 Viggo Meesters</span><span><a href="/timeline/">Timeline</a> · <a href="/apps/">Apps</a> · <a href="/systems/">Systems</a></span></footer>
  </main>
</body>
</html>
"""


def sync_timeline(content: str, projects: list[dict]) -> str:
    for project in projects:
        route = f'/projects/{project["slug"]}/'
        if f'href="{route}"' in content:
            continue
        title = e(project["timeline_heading"])
        pattern = re.compile(r'(<article class="timeline-entry[^>]*>[\s\S]*?<h3>' + re.escape(title) + r'</h3>[\s\S]*?<div class="proof-links">)')
        content, count = pattern.subn(rf'\1<a href="{route}">Open project page &rarr;</a>', content, count=1)
        if count != 1:
            raise ValueError(f'Could not connect timeline entry for {project["title"]}')
    return content


def project_sitemap(projects: list[dict]) -> str:
    routes = ["/projects/"] + [f'/projects/{p["slug"]}/' for p in projects]
    urls = []
    for route in routes:
        urls.append(f"  <url>\n    <loc>{BASE_URL}{route}</loc>\n    <lastmod>{LASTMOD}</lastmod>\n    <priority>{'0.8' if route == '/projects/' else '0.6'}</priority>\n  </url>")
    return f"{SITEMAP_START}\n" + "\n".join(urls) + f"\n{SITEMAP_END}"


def sync_sitemap(content: str, projects: list[dict]) -> str:
    block = project_sitemap(projects)
    if SITEMAP_START in content:
        return re.sub(re.escape(SITEMAP_START) + r'[\s\S]*?' + re.escape(SITEMAP_END), block, content)
    return content.replace("</urlset>", f"{block}\n</urlset>")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    projects = json.loads(CATALOG.read_text(encoding="utf-8"))
    expected: dict[Path, str] = {ROOT / "projects" / "index.html": render_index(projects)}
    for index, project in enumerate(projects):
        newer = projects[index - 1] if index else None
        older = projects[index + 1] if index + 1 < len(projects) else None
        expected[ROOT / "projects" / project["slug"] / "index.html"] = render_detail(project, newer, older)
    timeline = sync_timeline(TIMELINE.read_text(encoding="utf-8"), projects)
    sitemap = sync_sitemap(SITEMAP.read_text(encoding="utf-8"), projects)

    if args.check:
        stale = [str(path.relative_to(ROOT)) for path, value in expected.items() if not path.is_file() or path.read_text(encoding="utf-8") != value]
        if TIMELINE.read_text(encoding="utf-8") != timeline:
            stale.append("timeline/index.html")
        if SITEMAP.read_text(encoding="utf-8") != sitemap:
            stale.append("sitemap.xml")
        if stale:
            print("Project pages are stale: " + ", ".join(stale), file=sys.stderr)
            return 1
        print(f"Project page check passed: {len(projects)} detail pages and index are current.")
        return 0

    for path, value in expected.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value, encoding="utf-8")
    TIMELINE.write_text(timeline, encoding="utf-8")
    SITEMAP.write_text(sitemap, encoding="utf-8")
    print(f"Generated {len(projects)} project pages, index, timeline links, and sitemap routes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
