#!/usr/bin/env python3
"""Generate public skill summary pages from the local Hermes skills registry.

This intentionally publishes only name/category/description/path-derived summary
pages, not full SKILL.md runbooks. Run from the repo root:

    python3 scripts/generate-skills-pages.py

Then run:

    npm run check
"""
from __future__ import annotations

import datetime as _dt
import html
import json
import os
import re
import subprocess
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = Path.home() / ".hermes" / "skills"
BASE = "https://viggomeesters.com"
TODAY = _dt.date.today().isoformat()

CSS = """
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}:root{--bg:#0c0c0f;--surface:#141418;--border:rgba(255,255,255,.10);--sub:rgba(255,255,255,.055);--text:#c8cbd5;--muted:#53586b;--secondary:#8a90a6;--accent:#22c55e;--soft:rgba(34,197,94,.10);--font:'Sora',system-ui,-apple-system,sans-serif;--mono:'JetBrains Mono','SF Mono',monospace;--radius:16px;--bounce:cubic-bezier(.34,1.56,.64,1)}html{background:var(--bg);scroll-behavior:smooth;-webkit-font-smoothing:antialiased}body{background:var(--bg);color:var(--text);font-family:var(--font);font-size:15px;line-height:1.6;min-height:100vh;overflow-x:hidden}.page{position:relative;z-index:1;max-width:980px;margin:0 auto;padding:58px 20px 64px}.back{display:inline-flex;align-items:center;gap:6px;font-size:.82em;color:var(--muted);text-decoration:none;margin-bottom:32px;padding:6px 14px;background:var(--surface);border:1px solid var(--sub);border-radius:10px}.eyebrow{font-family:var(--mono);font-size:.72em;color:var(--accent);letter-spacing:.14em;text-transform:uppercase;margin-bottom:10px}.title{font-size:clamp(2rem,5vw,3.2rem);line-height:1.04;letter-spacing:-.04em;color:#eeeff4;font-weight:700;text-wrap:balance}.subtitle{max-width:760px;margin-top:14px;color:var(--secondary)}.meta{display:flex;flex-wrap:wrap;gap:8px;margin-top:16px}.pill{font-family:var(--mono);font-size:.72em;color:var(--secondary);background:rgba(255,255,255,.035);border:1px solid var(--sub);border-radius:999px;padding:5px 8px}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin-top:12px}.card{display:flex;gap:16px;align-items:flex-start;padding:20px;background:rgba(20,20,24,.74);border:1px solid var(--sub);border-radius:var(--radius);box-shadow:inset 0 1px 0 rgba(255,255,255,.026),0 0 28px rgba(34,197,94,.055),0 14px 40px rgba(0,0,0,.13);text-decoration:none;color:inherit}.icon{width:42px;height:42px;border-radius:12px;background:var(--soft);display:flex;align-items:center;justify-content:center;flex-shrink:0;color:var(--accent);font-family:var(--mono);font-size:.8em}.card h2{font-size:1em;color:#eeeff4;margin-bottom:5px}.card p{font-size:.88em;color:var(--secondary)}.tiny{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px;font-family:var(--mono);font-size:.7em;color:var(--muted)}.section{margin-top:34px}.section-title{display:flex;align-items:center;gap:8px;margin-bottom:12px;font-family:var(--mono);font-size:.75em;text-transform:uppercase;letter-spacing:.12em;color:var(--muted)}.section[hidden],.card[hidden]{display:none!important}.result-count{font-family:var(--mono);font-size:.75em;color:var(--muted);margin-top:10px}.search{width:100%;margin-top:22px;padding:12px 14px;border:1px solid var(--sub);border-radius:12px;background:var(--surface);color:var(--text);font:inherit}.item{padding:16px 18px;background:rgba(20,20,24,.74);border:1px solid var(--sub);border-radius:14px}.item strong{color:#eeeff4}.item p{color:var(--secondary);font-size:.9em;margin-top:4px}.list{display:grid;gap:10px}.footer{margin-top:42px;text-align:center;color:var(--muted);font-size:.72em;opacity:.55}@media(max-width:760px){.page{padding:42px 14px}.grid{grid-template-columns:1fr}.title{font-size:2rem}}
"""
SCRIPT = """<script>
const q=document.querySelector('[data-search]');
const result=document.querySelector('[data-result-count]');
function applySkillSearch(){
  const v=(q?.value||'').trim().toLowerCase();
  let total=0;
  document.querySelectorAll('[data-skill-section]').forEach(section=>{
    let visible=0;
    section.querySelectorAll('[data-filter]').forEach(card=>{
      const match=!v || card.dataset.filter.includes(v);
      card.hidden=!match;
      if(match) visible+=1;
    });
    section.hidden=visible===0;
    const title=section.querySelector('[data-section-title]');
    if(title){
      const label=section.dataset.category || '';
      const base=Number(section.dataset.total || visible);
      title.textContent = v ? `${label} · ${visible}/${base}` : `${label} · ${base}`;
    }
    total+=visible;
  });
  if(result){
    result.textContent = v ? `${total} matching skill${total===1?'':'s'}` : `${result.dataset.total} skills across ${result.dataset.categories} categories`;
  }
}
if(q){q.addEventListener('input',applySkillSearch);applySkillSearch();}
</script>"""


def esc(value: str) -> str:
    return html.escape(value or "")



def public_description(value: str, name: str = "skill") -> str:
    """Turn runtime skill-router descriptions into visitor-facing public copy.

    The generated skill pages are numerous, so this also normalizes snippet
    length for search pages: specific enough to avoid duplicate/short metadata,
    but short enough for normal search snippets.
    """
    raw = (value or "").strip()
    if not raw or raw.lower().startswith("enabled hermes skill from"):
        raw = f"Hermes workflow summary for {name}, published as a public registry card with private runbook details intentionally omitted."

    lower = raw.lower()
    rest = raw
    prefix = ""

    if lower.startswith("use only when "):
        prefix = "Specialized workflow for "
        rest = raw[len("Use only when "):]
    elif lower.startswith("use when "):
        prefix = "Workflow for "
        rest = raw[len("Use when "):]
    elif lower.startswith("use "):
        prefix = "Workflow for "
        rest = raw[len("Use "):]

    if prefix:
        rest = re.sub(r"^(Viggo asks for|Viggo asks|Viggo wants|the user asks for|the user asks|requests for|requests)\s+", "", rest, flags=re.IGNORECASE).strip()
        if rest.lower().startswith("to "):
            text = "Workflow to " + rest[3:]
        elif rest.lower().startswith("during "):
            text = "Workflow for use during " + rest[7:]
        elif rest.lower().startswith(("when ", "where ", "while ")):
            text = "Workflow for " + rest
        else:
            if rest:
                rest = rest[0].lower() + rest[1:]
            text = prefix + rest
    else:
        text = raw

    replacements = {
        "Viggo asks for": "requests for",
        "Viggo asks": "requests",
        "Viggo wants": "requests",
        "the user asks for": "requests for",
        "the user asks": "requests",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"\s+", " ", text).strip()
    if len(re.sub(r"[^A-Za-z0-9]", "", text)) < 24:
        text = f"Hermes workflow summary for {name}, published as a public registry card with private runbook details intentionally omitted."
    if len(text) > 158:
        cut = text[:155].rsplit(" ", 1)[0].rstrip(" ,;:")
        text = cut + "."
    if len(text) < 80:
        suffix = " It is shown as public metadata only; private steps and local paths stay inside Hermes."
        text = (text.rstrip(".") + "." + suffix)[:168].rsplit(" ", 1)[0].rstrip(" ,;:") + "."
    return text

def slugify(value: str) -> str:
    value = value.lower().replace("/", "-")
    return re.sub(r"[^a-z0-9_-]+", "-", value).strip("-") or "skill"


def parse_frontmatter(text: str) -> dict[str, str]:
    data = {}
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            for line in text[3:end].splitlines():
                if ":" in line and not line.startswith(" "):
                    key, value = line.split(":", 1)
                    data[key.strip()] = value.strip().strip('"')
    return data


def page(title: str, desc: str, canonical: str, body: str, include_script: bool = True) -> str:
    script = f"\n  {SCRIPT}" if include_script else ""
    return f'''<!DOCTYPE html>\n<html lang="en">\n<head>\n  <meta charset="UTF-8">\n  <meta name="viewport" content="width=device-width, initial-scale=1.0">\n  <title>{esc(title)}</title>\n  <meta name="description" content="{esc(desc)}">\n  <link rel="canonical" href="{esc(canonical)}">\n  <meta name="theme-color" content="#0c0c0f">\n  <link rel="icon" href="/favicon.ico" sizes="any">\n  <link rel="icon" href="/favicon.svg" type="image/svg+xml">\n  <link rel="apple-touch-icon" href="/apple-touch-icon.png">\n  <link rel="manifest" href="/site.webmanifest">\n  <meta property="og:title" content="{esc(title)}">\n  <meta property="og:description" content="{esc(desc)}">\n  <meta property="og:url" content="{esc(canonical)}">\n  <meta property="og:image" content="https://viggomeesters.com/og-image.png">\n  <meta name="twitter:card" content="summary_large_image">\n  <link rel="preconnect" href="https://fonts.googleapis.com">\n  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n  <link href="https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">\n  <style>{CSS}</style>\n  <script defer src="/_vercel/insights/script.js"></script>\n</head>\n<body>\n  <main class="page">\n{body}\n    <div class="footer">&copy; 2026 Viggo Meesters</div>\n  </main>{script}\n</body>\n</html>\n'''


def local_descriptions() -> dict[str, dict[str, str]]:
    """Descriptions from local SKILL.md files. Archive copies are ignored."""
    out: dict[str, dict[str, str]] = {}
    if not SKILLS_ROOT.exists():
        return out
    for md in SKILLS_ROOT.rglob("SKILL.md"):
        rel = md.relative_to(SKILLS_ROOT).as_posix()
        if rel.startswith(".archive/"):
            continue
        name = md.parent.name
        text = md.read_text(errors="ignore")
        fm = parse_frontmatter(text)
        public_name = (fm.get("name") or name).strip()
        out[public_name] = {
            "description": (fm.get("description") or "").strip()[:500],
            "path": str(md),
        }
    return out


def enabled_skills_from_cli() -> list[dict[str, str]]:
    """Parse `hermes skills list --enabled-only` rich-table output.

    This is the best local source for the active runtime registry because it
    includes builtin, official, and local skills. Descriptions are enriched from
    local SKILL.md files when present.
    """
    env = {"COLUMNS": "500"}
    proc = subprocess.run(
        ["hermes", "skills", "list", "--enabled-only"],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
        env={**os.environ, **env},
        check=True,
    )
    descriptions = local_descriptions()
    skills: list[dict[str, str]] = []
    for line in proc.stdout.splitlines():
        if not line.startswith("│"):
            continue
        cells = [cell.strip() for cell in line.strip("│").split("│")]
        if len(cells) < 5 or cells[0] == "Name":
            continue
        name, category, source, trust, status = cells[:5]
        if status != "enabled" or "…" in name:
            continue
        info = descriptions.get(name, {})
        desc = info.get("description") or f"Enabled Hermes skill from {source or 'runtime'} source."
        skills.append({
            "name": name,
            "category": category or "core",
            "description": desc[:500],
            "source": source,
            "trust": trust,
            "path": info.get("path", "builtin/runtime"),
        })
    return sorted(skills, key=lambda s: (s["category"], s["name"]))


def discover() -> list[dict[str, str]]:
    return enabled_skills_from_cli()


def clean_obsolete_skill_pages(out: Path, skills: list[dict[str, str]]) -> None:
    """Remove stale generated skill detail pages that no longer exist in the active registry."""
    active_slugs = {slugify(skill["name"]) for skill in skills}
    for child in out.iterdir():
        if not child.is_dir() or child.name in active_slugs:
            continue
        index = child / "index.html"
        if not index.exists():
            continue
        text = index.read_text(errors="ignore")
        if "<title>" in text and " — Skill" in text and "/skills/" in text:
            for nested in child.iterdir():
                nested.unlink()
            child.rmdir()


def regenerate_sitemap() -> None:
    sitemap = ROOT / "sitemap.xml"
    old = sitemap.read_text() if sitemap.exists() else ""
    oldmap = dict(re.findall(r"<loc>([^<]+)</loc>\n\s*<lastmod>([^<]+)</lastmod>", old))
    routes = []
    for idx in ROOT.rglob("index.html"):
        rel = idx.relative_to(ROOT).as_posix()
        if rel.startswith((".git/", ".vercel/", "node_modules/")):
            continue
        route = "/" if rel == "index.html" else "/" + str(Path(rel).parent).replace("\\", "/") + "/"
        routes.append(route)
    entries = []
    for route in sorted(set(routes), key=lambda r: (r.count("/"), r)):
        loc = BASE + route
        priority = "1.0" if route == "/" else ("0.8" if route in ["/uses/", "/tech-stack/", "/skills/"] else "0.7")
        entries.append(f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{oldmap.get(loc, TODAY)}</lastmod>\n    <priority>{priority}</priority>\n  </url>")
    sitemap.write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(entries) + "\n</urlset>\n")


def main() -> None:
    skills = discover()
    for skill in skills:
        skill["description"] = public_description(skill.get("description", ""), skill.get("name", "skill"))
    out = ROOT / "skills"
    out.mkdir(exist_ok=True)
    clean_obsolete_skill_pages(out, skills)
    (out / "skills-data.json").write_text(json.dumps({"generated_at": TODAY, "count": len(skills), "skills": [{k: v for k, v in skill.items() if k != "path"} for skill in skills]}, ensure_ascii=False, indent=2))
    groups = defaultdict(list)
    for skill in skills:
        groups[skill["category"]].append(skill)
        body = f'''    <a class="back" href="/skills/">&larr; Skills</a>\n    <header><div class="eyebrow">Skill / {esc(skill['category'])}</div><h1 class="title">{esc(skill['name'])}</h1><p class="subtitle">{esc(skill['description'] or 'No description available.')}</p><div class="meta"><span class="pill">Hermes skill</span><span class="pill">{esc(skill['category'])}</span><span class="pill">snapshot {TODAY}</span></div></header>\n    <section class="section"><div class="section-title">Public summary</div><div class="list"><article class="item"><strong>Skill identifier</strong><p><code>{esc(skill['name'])}</code></p></article><article class="item"><strong>What this page is</strong><p>A public summary card for discovery. Detailed runbooks, private steps, local paths, credentials, and sensitive project context are intentionally not published.</p></article><article class="item"><strong>Registry snapshot</strong><p>Generated from the currently enabled local Hermes skill registry. Use this page to see that a workflow exists; the actual workflow runs inside Hermes.</p></article></div></section>'''
        d = out / slugify(skill["name"])
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(page(f"{skill['name']} — Hermes Skill Workflow", skill["description"] or f"Hermes workflow summary for {skill['name']}.", f"{BASE}/skills/{slugify(skill['name'])}/", body, include_script=False))
    sections = []
    for category in sorted(groups):
        cards = []
        for skill in groups[category]:
            filt = (skill["name"] + " " + category + " " + (skill["description"] or "")).lower()
            cards.append(f'''      <a class="card" data-filter="{esc(filt)}" href="/skills/{slugify(skill['name'])}/"><div class="icon">SK</div><div><h2>{esc(skill['name'])}</h2><p>{esc(skill['description'] or 'No description available.')}</p><div class="tiny"><span>{esc(category)}</span><span>skill</span></div></div></a>''')
        sections.append(f'''    <section class="section" data-skill-section data-category="{esc(category)}" data-total="{len(groups[category])}"><div class="section-title" data-section-title>{esc(category)} · {len(groups[category])}</div><div class="grid">{''.join(cards)}</div></section>''')
    body = f'''    <a class="back" href="/">&larr; viggomeesters.com</a>\n    <header><div class="eyebrow">Hermes skills registry</div><h1 class="title">Skills as reusable operating knowledge.</h1><p class="subtitle">A public snapshot of reusable Hermes skill categories and summaries. Useful as a map of the operating knowledge behind this site without exposing implementation details.</p><div class="meta"><span class="pill">{len(skills)} skills</span><span class="pill">{len(groups)} categories</span><span class="pill">generated {TODAY}</span><span class="pill">public registry snapshot</span></div></header>\n    <input class="search" data-search placeholder="Search skills, categories, descriptions…" aria-label="Search skills">\n    <div class="result-count" data-result-count data-total="{len(skills)}" data-categories="{len(groups)}">{len(skills)} skills across {len(groups)} categories</div>\n{''.join(sections)}'''
    (out / "index.html").write_text(page("Hermes Skills Registry — Viggo Meesters", "Snapshot index of Hermes skills grouped by category, with per-skill public summary pages.", f"{BASE}/skills/", body))
    regenerate_sitemap()
    print(f"Generated {len(skills)} skills across {len(groups)} categories")


if __name__ == "__main__":
    main()
