#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "certifications" / "data.json"
INDEX = ROOT / "certifications" / "index.html"
TIMELINE = ROOT / "timeline" / "index.html"
SITEMAP = ROOT / "sitemap.xml"
BASE_URL = "https://viggomeesters.com"
LASTMOD = "2026-07-13"
SITEMAP_START = "  <!-- BEGIN GENERATED CERTIFICATIONS -->"
SITEMAP_END = "  <!-- END GENERATED CERTIFICATIONS -->"

MONTHS = {
    "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr", "05": "May", "06": "Jun",
    "07": "Jul", "08": "Aug", "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec",
}

GROUP_TITLES = {
    "2025-11": "Alteryx learning sprint",
    "2022-11": "SAP, SQL, and professional practice",
    "2022-10": "Delivery foundations across SAP, data, and Lean",
    "2022-09": "The Aiden learning sprint begins",
    "2022-08": "Data foundations",
    "2021-04": "IBM data science foundations",
}

IMAGE_DIMENSIONS = {
    "introduction-to-python": (1458, 841),
    "sap-s4hana-cloud-public-edition-sales-2023": (672, 352),
    "sap-analytics-cloud": (672, 352),
    "python-for-data-science-ai-and-development": (1772, 928),
    "data-science-orientation": (1772, 928),
    "data-science-methodology": (1440, 2499),
    "technical-support-fundamentals": (1772, 928),
    "microsoft-excel-specialist-2013": (1902, 1046),
}


def e(value: object) -> str:
    return html.escape(str(value), quote=True)


def display_date(value: str) -> str:
    year, month = value.split("-")
    return f"{MONTHS[month]} {year}"


CSS = """
    *,*::before,*::after{box-sizing:border-box}
    :root{--bg:#090b10;--surface:#0f131b;--line:#272e39;--line-soft:#1a202a;--text:#cbd2df;--muted:#818c9f;--bright:#f4f7fb;--accent:#ffd166;--accent-soft:rgba(255,209,102,.09);--sans:system-ui,-apple-system,'Segoe UI',sans-serif;--mono:ui-monospace,'SFMono-Regular','Cascadia Code',monospace}
    html{background:var(--bg);color-scheme:dark;scroll-behavior:smooth;-webkit-font-smoothing:antialiased}body{min-width:320px;margin:0;background:radial-gradient(ellipse 62% 32% at 84% -10%,rgba(255,209,102,.10),transparent 70%),var(--bg);color:var(--text);font:15px/1.7 var(--sans)}
    a{color:inherit}a:focus-visible,button:focus-visible{outline:2px solid var(--accent);outline-offset:4px}.page{width:min(1120px,calc(100% - 40px));margin:auto;padding:26px 0 76px}.topbar{display:flex;justify-content:space-between;align-items:center;gap:20px;min-height:46px}.back,.timeline-link{display:inline-flex;min-height:44px;align-items:center;color:var(--muted);font:500 .69rem var(--mono);text-decoration:none}.back:hover,.timeline-link:hover{color:var(--bright)}
    .hero{display:grid;grid-template-columns:minmax(0,1.45fr) minmax(260px,.55fr);gap:clamp(42px,8vw,108px);align-items:end;padding:clamp(68px,10vw,116px) 0 64px;border-bottom:1px solid var(--line)}.eyebrow{color:var(--accent);font:600 .68rem var(--mono);letter-spacing:.14em;text-transform:uppercase}.hero h1{max-width:800px;margin:18px 0 24px;color:var(--bright);font-size:clamp(3.4rem,9vw,7.2rem);font-weight:680;line-height:.87;letter-spacing:-.075em;text-wrap:balance}.lede{max-width:660px;margin:0;color:#9ca6b8;font-size:clamp(1rem,1.45vw,1.16rem)}.proof-count{padding-top:20px;border-top:2px solid var(--accent)}.proof-count strong{display:block;color:var(--bright);font-size:2.35rem;line-height:1}.proof-count span{display:block;margin-top:10px;color:var(--muted);font:500 .66rem var(--mono)}
    .summary{display:grid;grid-template-columns:repeat(3,1fr);margin:0 0 58px;border-left:1px solid var(--line)}.metric{padding:22px;border-right:1px solid var(--line);border-bottom:1px solid var(--line)}.metric strong{display:block;color:var(--bright);font-size:1.5rem}.metric span{color:var(--muted);font:500 .65rem var(--mono)}
    .controls{display:flex;justify-content:space-between;align-items:end;gap:28px;padding-bottom:20px;border-bottom:1px solid var(--line)}.controls h2{margin:0;color:var(--bright);font-size:1rem}.controls p{margin:4px 0 0;color:var(--muted);font:400 .67rem var(--mono)}.filters{display:flex;flex-wrap:wrap;justify-content:flex-end;gap:8px}.filter{min-height:44px;padding:0 14px;border:1px solid var(--line);border-radius:999px;background:transparent;color:var(--muted);font:500 .66rem var(--mono);cursor:pointer}.filter:hover{border-color:#4c5668;color:var(--bright)}.filter[aria-pressed="true"]{border-color:rgba(255,209,102,.45);background:var(--accent-soft);color:var(--accent)}.filter-status{min-height:38px;padding:10px 0;color:var(--muted);font:400 .64rem var(--mono)}
    .credentials{border-top:1px solid var(--line)}.credential-row{scroll-margin-top:20px;display:grid;grid-template-columns:110px minmax(0,1fr) minmax(250px,.55fr);gap:28px;align-items:start;padding:30px 0;border-bottom:1px solid var(--line)}.credential-row[hidden]{display:none}.date{color:var(--accent);font:500 .67rem var(--mono)}.credential-copy h3{margin:0;color:var(--bright);font-size:clamp(1.25rem,2.4vw,1.85rem);line-height:1.12;letter-spacing:-.035em}.issuer{display:block;margin-top:8px;color:var(--muted);font-size:.79rem}.credential-meta{min-width:0}.credential-id{display:block;color:var(--muted);font:400 .63rem/1.5 var(--mono);overflow-wrap:anywhere}.actions{display:flex;flex-wrap:wrap;gap:8px 18px;margin-top:15px}.actions a{display:inline-flex;min-height:44px;align-items:center;color:var(--accent);font:500 .67rem var(--mono);text-underline-offset:5px}.missing{margin:13px 0 0;color:#a7afbd;font-size:.76rem;line-height:1.55}.source{display:inline-block;margin-top:10px;color:#6f7a8d;font:400 .6rem var(--mono)}
    .proof-strip{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;margin:72px 0 0;border:1px solid var(--line);background:var(--line)}.proof-strip a{position:relative;display:block;min-width:0;aspect-ratio:1.35;background:var(--surface);overflow:hidden}.proof-strip img{width:100%;height:100%;object-fit:cover;filter:saturate(.78);transition:transform .25s,filter .25s}.proof-strip a:hover img{transform:scale(1.025);filter:saturate(1)}.proof-strip span{position:absolute;inset:auto 0 0;padding:26px 14px 12px;background:linear-gradient(transparent,rgba(9,11,16,.92));color:var(--bright);font:500 .62rem var(--mono)}
    .boundary{display:grid;grid-template-columns:190px minmax(0,1fr);gap:48px;margin-top:68px;padding-top:46px;border-top:1px solid var(--line)}.boundary h2{margin:0;color:var(--bright);font-size:1.45rem}.boundary p{max-width:670px;margin:0;color:var(--muted)}.footer{display:flex;justify-content:space-between;gap:20px;margin-top:64px;padding-top:22px;border-top:1px solid var(--line);color:var(--muted);font:400 .65rem var(--mono)}
    @media(max-width:780px){.page{width:min(100% - 24px,1120px);padding-top:14px}.hero{grid-template-columns:1fr;gap:36px;padding:54px 0}.proof-count{max-width:320px}.summary{grid-template-columns:1fr}.controls{align-items:flex-start;flex-direction:column}.filters{justify-content:flex-start}.credential-row{grid-template-columns:88px minmax(0,1fr)}.credential-meta{grid-column:2}.proof-strip{grid-template-columns:1fr 1fr}.boundary{grid-template-columns:1fr;gap:12px}.footer{flex-direction:column}}
    @media(max-width:480px){.timeline-link{display:none}.hero h1{font-size:3.15rem}.credential-row{grid-template-columns:1fr;gap:8px}.credential-meta{grid-column:1}.proof-strip{grid-template-columns:1fr}.filter{padding:0 12px}}
    @media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}*,*::before,*::after{transition-duration:.01ms!important}}
"""


def render_index(credentials: list[dict]) -> str:
    rows = []
    for item in credentials:
        artifact = item["artifact"]
        if artifact["status"] == "hosted":
            local = f'<a href="{e(artifact["path"])}" target="_blank" rel="noopener">Open local proof &nearr;</a>'
            source = f'<span class="source">Self-hosted · SHA-256 {e(artifact["sha256"][:12])}</span>'
            missing = ""
        else:
            local = ""
            source = '<span class="source">Metadata preserved · original requested</span>'
            missing = f'<p class="missing">{e(artifact["reason"])}</p>'
        credential_id = f'Credential {e(item["credential_id"])}' if item["credential_id"] else "No credential ID supplied"
        rows.append(f'''<article class="credential-row" id="{e(item["slug"])}" data-category="{e(item["category"])}">
          <time class="date" datetime="{e(item["issued"])}">{display_date(item["issued"])}</time>
          <div class="credential-copy"><h3>{e(item["title"])}</h3><span class="issuer">{e(item["issuer"])} · {e(item["category"])}</span></div>
          <div class="credential-meta"><span class="credential-id">{credential_id}</span><div class="actions">{local}<a href="{e(item["verification_url"])}" target="_blank" rel="noopener">Issuer record &nearr;</a></div>{missing}{source}</div>
        </article>''')

    image_items = [item for item in credentials if item["artifact"].get("mime_type", "").startswith("image/")][:4]
    proof_strip_parts = []
    for item in image_items:
        width, height = IMAGE_DIMENSIONS[item["slug"]]
        proof_strip_parts.append(f'<a href="{e(item["artifact"]["path"])}" target="_blank" rel="noopener"><img src="{e(item["artifact"]["path"])}" alt="{e(item["title"])} certificate preview" width="{width}" height="{height}" loading="lazy"><span>{e(item["issuer"])} · {display_date(item["issued"])}</span></a>')
    proof_strip = "".join(proof_strip_parts)
    structured = json.dumps({
        "@context": "https://schema.org", "@type": "ItemList", "name": "Certifications by Viggo Meesters",
        "numberOfItems": len(credentials), "itemListElement": [
            {"@type": "ListItem", "position": index + 1, "name": item["title"], "url": f'{BASE_URL}/certifications/#{item["slug"]}'}
            for index, item in enumerate(credentials)
        ],
    }, ensure_ascii=False).replace("</", "<\\/")
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Certifications &amp; Credentials — Viggo Meesters</title>
  <meta name="description" content="A verified archive of 36 SAP, data, automation, process, and development credentials earned by Viggo Meesters since 2016.">
  <link rel="canonical" href="{BASE_URL}/certifications/">
  <meta name="theme-color" content="#090b10">
  <meta property="og:title" content="Certifications &amp; Credentials — Viggo Meesters">
  <meta property="og:description" content="36 credentials with 30 locally hosted proof files on viggomeesters.com.">
  <meta property="og:type" content="profile"><meta property="og:url" content="{BASE_URL}/certifications/"><meta property="og:image" content="{BASE_URL}/og-image.png">
  <meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="Certifications &amp; Credentials — Viggo Meesters"><meta name="twitter:description" content="36 credentials with provenance and locally hosted proof."><meta name="twitter:image" content="{BASE_URL}/og-image.png">
  <link rel="icon" href="/favicon.ico" sizes="any"><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="/apple-touch-icon.png"><link rel="manifest" href="/site.webmanifest">
  <script type="application/ld+json">{structured}</script>
  <style>{CSS}</style>
  <script defer src="/_vercel/insights/script.js"></script>
</head>
<body>
  <main class="page">
    <nav class="topbar" aria-label="Page navigation"><a class="back" href="/">&larr; viggomeesters.com</a><a class="timeline-link" href="/timeline/?type=certificate">View learning timeline &rarr;</a></nav>
    <header class="hero"><div><div class="eyebrow">Learn / verify / apply</div><h1>Credentials, with receipts.</h1><p class="lede">A complete record of 36 certificates and credentials. A local proof file is served whenever the active vault or official issuer still provides one.</p></div><div class="proof-count"><strong>30</strong><span>locally hosted proofs · 6 source files still needed</span></div></header>
    <section class="summary" aria-label="Archive summary"><div class="metric"><strong>36</strong><span>credentials since 2016</span></div><div class="metric"><strong>6</strong><span>SAP credentials</span></div><div class="metric"><strong>14</strong><span>DataCamp credentials</span></div></section>
    <section class="controls" aria-labelledby="archive-heading"><div><h2 id="archive-heading">Complete credential archive</h2><p>Newest first · issuer verification retained</p></div><div class="filters" aria-label="Filter credentials"><button class="filter" type="button" data-filter="all" aria-pressed="true">All</button><button class="filter" type="button" data-filter="SAP" aria-pressed="false">SAP</button><button class="filter" type="button" data-filter="Data and automation" aria-pressed="false">Data &amp; automation</button><button class="filter" type="button" data-filter="Professional practice" aria-pressed="false">Professional practice</button><button class="filter" type="button" data-filter="Foundations" aria-pressed="false">Foundations</button></div></section>
    <div class="filter-status"><span id="filter-status" role="status" aria-live="polite">36 credentials shown</span></div>
    <section class="credentials" aria-label="All credentials">{''.join(rows)}</section>
    <section class="proof-strip" aria-label="Selected locally hosted credential previews">{proof_strip}</section>
    <section class="boundary"><h2>Proof boundary</h2><p>30 files are copied from integrity-checked vault blobs or downloaded from official verification pages. Six former Aiden Academy records now require StudyTube authentication and are shown as metadata only until the original image files can be added. Historical credentials may show Ricardo, Viggo, or V. Mulders: the name used when they were issued. Nothing is reconstructed or presented as an issuer original.</p></section>
    <footer class="footer"><span>&copy; 2026 Viggo Meesters</span><span><a href="/timeline/">Timeline</a> · <a href="/projects/">Projects</a> · <a href="mailto:38-isles-effete@icloud.com">Email</a></span></footer>
  </main>
  <script>(()=>{{const buttons=[...document.querySelectorAll('[data-filter]')],rows=[...document.querySelectorAll('.credential-row')],status=document.getElementById('filter-status'),valid=new Set(buttons.map(button=>button.dataset.filter));function apply(requested,update=true){{const filter=valid.has(requested)?requested:'all';let visible=0;rows.forEach(row=>{{const show=filter==='all'||row.dataset.category===filter;row.hidden=!show;if(show)visible+=1}});buttons.forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.filter===filter)));status.textContent=`${{visible}} ${{visible===1?'credential':'credentials'}} shown`;if(update){{const url=new URL(location.href);if(filter==='all')url.searchParams.delete('category');else url.searchParams.set('category',filter);history.replaceState({{filter}},'',url)}}}}buttons.forEach(button=>button.addEventListener('click',()=>apply(button.dataset.filter)));window.addEventListener('popstate',()=>apply(new URLSearchParams(location.search).get('category')||'all',false));apply(new URLSearchParams(location.search).get('category')||'all',false)}})();</script>
</body>
</html>
'''


def render_timeline_entries(credentials: list[dict]) -> list[str]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for item in credentials:
        groups[item["issued"]].append(item)
    entries = []
    for issued, items in groups.items():
        issuers = ", ".join(sorted({item["issuer"] for item in items}))
        title = GROUP_TITLES.get(issued, items[0]["title"] if len(items) == 1 else f'{len(items)} credentials completed')
        links = "".join(f'<a href="/certifications/#{e(item["slug"])}">{e(item["title"])} &rarr;</a>' for item in items)
        count = f'{len(items)} credentials' if len(items) != 1 else "Credential"
        entries.append(f'''<article class="timeline-entry" data-date="{issued}-01" data-type="certificate" data-certification-group="{issued}">
        <div class="entry-meta"><time class="entry-date" datetime="{issued}">{display_date(issued)}</time><span class="entry-type">Learning</span></div>
        <div class="entry-body"><span class="entry-number">{e(count)} / {e(issuers)}</span><h3>{e(title)}</h3><p>{'A focused learning milestone connecting ' + e(len(items)) + ' verified credentials.' if len(items) > 1 else 'A verified credential added to the professional learning record.'}</p><div class="proof-links">{links}</div></div>
      </article>''')
    return entries


def sync_timeline(content: str, credentials: list[dict]) -> str:
    certificate_rule = '.timeline-entry[data-type="certificate"]{--entry:#ffd166}'
    content = re.sub(f'(?:{re.escape(certificate_rule)})+', certificate_rule, content)
    if certificate_rule not in content:
        content = content.replace('.timeline-entry[data-type="writing"]{--entry:#8ee6b1}.timeline-entry[data-type="career"]{--entry:#f5a524}', '.timeline-entry[data-type="writing"]{--entry:#8ee6b1}.timeline-entry[data-type="career"]{--entry:#f5a524}' + certificate_rule)
    if 'data-filter="certificate"' not in content:
        content = content.replace('<button class="filter" type="button" data-filter="writing" aria-pressed="false">Writing</button>', '<button class="filter" type="button" data-filter="writing" aria-pressed="false">Writing</button>\n        <button class="filter" type="button" data-filter="certificate" aria-pressed="false">Learning</button>')
    section_match = re.search(r'(<section class="timeline" aria-label="Work and build timeline">)([\s\S]*?)(\n    </section>)', content)
    if not section_match:
        raise ValueError("Timeline section not found")
    existing = re.findall(r'<article class="timeline-entry[^>]*>[\s\S]*?</article>', section_match.group(2))
    existing = [entry for entry in existing if 'data-certification-group=' not in entry]
    combined = existing + render_timeline_entries(credentials)
    combined.sort(key=lambda entry: re.search(r'data-date="([^"]+)"', entry).group(1), reverse=True)
    replacement = section_match.group(1) + "\n      " + "\n\n      ".join(entry.strip() for entry in combined) + section_match.group(3)
    content = content[:section_match.start()] + replacement + content[section_match.end():]
    content = re.sub(r'>\d+ milestones shown</span>', f'>{len(combined)} milestones shown</span>', content, count=1)
    content = content.replace("professional projects, products, repositories, agent systems, data migration work, and writing since 2014", "professional projects, credentials, products, repositories, agent systems, data migration work, and writing since 2014")
    content = content.replace("professional projects, products, repositories, systems, and ideas from 2014 to now", "professional projects, credentials, products, repositories, systems, and ideas from 2014 to now")
    return content


def sync_sitemap(content: str) -> str:
    block = f'''{SITEMAP_START}
  <url>
    <loc>{BASE_URL}/certifications/</loc>
    <lastmod>{LASTMOD}</lastmod>
    <priority>0.7</priority>
  </url>
{SITEMAP_END}'''
    if SITEMAP_START in content:
        return re.sub(re.escape(SITEMAP_START) + r'[\s\S]*?' + re.escape(SITEMAP_END), block, content)
    return content.replace("</urlset>", f"{block}\n</urlset>")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    credentials = json.loads(CATALOG.read_text(encoding="utf-8"))
    expected_index = render_index(credentials)
    expected_timeline = sync_timeline(TIMELINE.read_text(encoding="utf-8"), credentials)
    expected_sitemap = sync_sitemap(SITEMAP.read_text(encoding="utf-8"))
    if args.check:
        stale = []
        if not INDEX.is_file() or INDEX.read_text(encoding="utf-8") != expected_index:
            stale.append("certifications/index.html")
        if TIMELINE.read_text(encoding="utf-8") != expected_timeline:
            stale.append("timeline/index.html")
        if SITEMAP.read_text(encoding="utf-8") != expected_sitemap:
            stale.append("sitemap.xml")
        if stale:
            print("Certification archive is stale: " + ", ".join(stale), file=sys.stderr)
            return 1
        print(f"Certification archive check passed: {len(credentials)} credentials.")
        return 0
    INDEX.write_text(expected_index, encoding="utf-8")
    TIMELINE.write_text(expected_timeline, encoding="utf-8")
    SITEMAP.write_text(expected_sitemap, encoding="utf-8")
    print(f"Generated certification archive and {len({item['issued'] for item in credentials})} timeline milestones.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
