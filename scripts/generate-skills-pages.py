#!/usr/bin/env python3
"""Generate reviewed public skill pages from an explicit allowlist.

Runtime registry entries are candidates only. Public names, categories and copy
come from ``scripts/public-skills.json`` so a newly enabled or private skill is
excluded by default. Run from the repo root:

    python3 scripts/generate-skills-pages.py

Then run:

    npm run check
"""
from __future__ import annotations

import argparse
import datetime as _dt
import html
import json
import os
import re
import shutil
import subprocess
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Optional, Union

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
ROOT = DEFAULT_ROOT
SKILLS_ROOT = Path.home() / ".hermes" / "skills"
BASE = "https://viggomeesters.com"
TODAY = _dt.date.today().isoformat()
DANGLING_DESCRIPTION_TAILS = {
    "a",
    "an",
    "and",
    "as",
    "at",
    "by",
    "for",
    "from",
    "in",
    "into",
    "of",
    "on",
    "or",
    "the",
    "through",
    "to",
    "when",
    "with",
    "without",
}

CSS = """
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#0c0c0f;--surface:#141418;--border:rgba(255,255,255,.14);--sub:rgba(255,255,255,.10);--text:#c8cbd5;--muted:#9ba1b5;--secondary:#aeb4c5;--accent:#22c55e;--soft:rgba(34,197,94,.10);--font:'Sora',system-ui,-apple-system,sans-serif;--mono:'JetBrains Mono','SF Mono',monospace;--radius:16px}
html{background:var(--bg);scroll-behavior:smooth;-webkit-font-smoothing:antialiased}
body{background:var(--bg);color:var(--text);font-family:var(--font);font-size:15px;line-height:1.6;min-height:100vh;overflow-x:hidden}
.page{position:relative;z-index:1;max-width:980px;margin:0 auto;padding:58px 20px 64px}
.back{display:inline-flex;min-height:44px;align-items:center;gap:6px;font-size:.82em;color:var(--muted);text-decoration:none;margin-bottom:32px;padding:9px 14px;background:var(--surface);border:1px solid var(--sub);border-radius:10px}
.eyebrow{font-family:var(--mono);font-size:.72em;color:var(--accent);letter-spacing:.14em;text-transform:uppercase;margin-bottom:10px}
.title{font-size:clamp(2rem,5vw,3.2rem);line-height:1.04;letter-spacing:-.04em;color:#eeeff4;font-weight:700;text-wrap:balance}
.subtitle{max-width:760px;margin-top:14px;color:var(--secondary)}
.meta{display:flex;flex-wrap:wrap;gap:8px;margin-top:16px}
.pill{font-family:var(--mono);font-size:.72em;color:var(--secondary);background:rgba(255,255,255,.035);border:1px solid var(--sub);border-radius:999px;padding:5px 8px}
.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin-top:12px}
.card{display:flex;gap:16px;align-items:flex-start;padding:20px;background:rgba(20,20,24,.74);border:1px solid var(--sub);border-radius:var(--radius);box-shadow:inset 0 1px 0 rgba(255,255,255,.026),0 0 28px rgba(34,197,94,.055),0 14px 40px rgba(0,0,0,.13);text-decoration:none;color:inherit}
.icon{width:42px;height:42px;border-radius:12px;background:var(--soft);display:flex;align-items:center;justify-content:center;flex-shrink:0;color:var(--accent);font-family:var(--mono);font-size:.8em}
.card h3{font-size:1em;color:#eeeff4;margin-bottom:5px}.card p{font-size:.88em;color:var(--secondary)}
.tiny{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px;font-family:var(--mono);font-size:.74em;color:var(--muted)}
.section{margin-top:34px}.section-title{display:flex;align-items:center;gap:8px;margin-bottom:12px;font-family:var(--mono);font-size:.78em;text-transform:uppercase;letter-spacing:.12em;color:var(--muted)}
.section[hidden],.card[hidden]{display:none!important}
.result-count{font-family:var(--mono);font-size:.78em;color:var(--muted);margin-top:10px}
.search-label{display:block;margin-top:22px;font-family:var(--mono);font-size:.78em;color:var(--muted)}
.search{width:100%;margin-top:7px;padding:12px 14px;border:1px solid var(--border);border-radius:12px;background:var(--surface);color:var(--text);font:inherit}
.item{padding:16px 18px;background:rgba(20,20,24,.74);border:1px solid var(--sub);border-radius:14px}.item strong{color:#eeeff4}.item p{color:var(--secondary);font-size:.9em;margin-top:4px}
.list{display:grid;gap:10px}.next-link{display:block;color:inherit;text-decoration:none}
.footer{margin-top:42px;text-align:center;color:var(--muted);font-size:.82em}
:where(a,input):focus-visible{outline:3px solid var(--accent);outline-offset:3px}.card:hover,.card:focus-visible,.next-link:hover,.next-link:focus-visible{border-color:rgba(34,197,94,.55)}
@media(max-width:760px){.page{padding:42px 14px}.grid{grid-template-columns:1fr}.title{font-size:2rem}}
"""

PublicSkill = dict[str, Union[str, bool]]
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


def page(
    title: str,
    desc: str,
    canonical: str,
    body: str,
    include_script: bool = True,
    robots: Optional[str] = None,
) -> str:
    script = f"\n  {SCRIPT}" if include_script else ""
    robots_meta = f'\n  <meta name="robots" content="{esc(robots)}">' if robots else ""
    return f'''<!DOCTYPE html>\n<html lang="en">\n<head>\n  <meta charset="UTF-8">\n  <meta name="viewport" content="width=device-width, initial-scale=1.0">\n  <title>{esc(title)}</title>\n  <meta name="description" content="{esc(desc)}">{robots_meta}\n  <link rel="canonical" href="{esc(canonical)}">\n  <meta name="theme-color" content="#0c0c0f">\n  <link rel="icon" href="/favicon.ico" sizes="any">\n  <link rel="icon" href="/favicon.svg" type="image/svg+xml">\n  <link rel="apple-touch-icon" href="/apple-touch-icon.png">\n  <link rel="manifest" href="/site.webmanifest">\n  <meta property="og:title" content="{esc(title)}">\n  <meta property="og:description" content="{esc(desc)}">\n  <meta property="og:url" content="{esc(canonical)}">\n  <meta property="og:image" content="https://viggomeesters.com/og-image.png">\n  <meta name="twitter:card" content="summary_large_image">\n  <link rel="preconnect" href="https://fonts.googleapis.com">\n  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n  <link href="https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">\n  <style>{CSS}</style>\n  <script defer src="/_vercel/insights/script.js"></script>\n</head>\n<body>\n  <main class="page">\n{body}\n    <div class="footer">&copy; 2026 Viggo Meesters</div>\n  </main>{script}\n</body>\n</html>\n'''


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


def registry_from_json(path: Path) -> list[dict[str, str]]:
    """Load a captured runtime registry for deterministic generation/tests."""
    data = json.loads(path.read_text(encoding="utf-8"))
    skills = data.get("skills") if isinstance(data, dict) else data
    if not isinstance(skills, list) or not all(isinstance(item, dict) for item in skills):
        raise ValueError(f"Invalid registry JSON: {path}")
    return skills


def load_public_allowlist(path: Path) -> list[PublicSkill]:
    """Load and validate the reviewed public metadata before any writes."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema") != "viggomeesters.public-skills.v1":
        raise ValueError(f"Invalid public skills schema: {path}")
    approved_raw = data.get("approved_proper_nouns", [])
    if not isinstance(approved_raw, list) or not all(
        isinstance(item, str) and item.strip() for item in approved_raw
    ):
        raise ValueError("approved_proper_nouns must be a list of non-empty strings")
    approved_proper_nouns = {item.strip() for item in approved_raw}
    skills = data.get("skills")
    if not isinstance(skills, list) or not skills:
        raise ValueError("Public skills allowlist must contain at least one reviewed skill")

    names: set[str] = set()
    slugs: set[str] = set()
    reviewed: list[PublicSkill] = []
    for item in skills:
        if not isinstance(item, dict):
            raise ValueError("Every public skill entry must be an object")
        entry = {key: str(item.get(key, "")).strip() for key in ("name", "category", "description")}
        if not all(entry.values()):
            raise ValueError("Every public skill needs reviewed name, category and description")
        validate_public_description(entry["description"], approved_proper_nouns)
        provenance_fields = (
            "maintainer",
            "origin",
            "attribution",
            "declared_license",
            "implementation_status",
            "reviewed_at",
            "indexable",
        )
        if any(field not in item for field in provenance_fields):
            raise ValueError("Every public skill needs complete reviewed provenance")
        entry.update(
            {
                "maintainer": str(item["maintainer"]).strip(),
                "origin": str(item["origin"]).strip(),
                "attribution": str(item["attribution"]).strip(),
                "declared_license": str(item["declared_license"]).strip(),
                "implementation_status": str(item["implementation_status"]).strip(),
                "reviewed_at": str(item["reviewed_at"]).strip(),
            }
        )
        for field in (
            "maintainer",
            "origin",
            "attribution",
            "declared_license",
            "implementation_status",
        ):
            if not entry[field]:
                raise ValueError(f"Every public skill needs reviewed {field}")
            validate_public_text(entry[field], approved_proper_nouns)
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", entry["reviewed_at"]):
            raise ValueError("Every public skill needs an ISO reviewed_at date")
        indexable = item["indexable"]
        if not isinstance(indexable, bool):
            raise ValueError("Every public skill indexable flag must be boolean")
        entry["indexable"] = indexable
        folded = entry["name"].casefold()
        slug = slugify(entry["name"])
        if folded in names:
            raise ValueError(f"Duplicate public skill name: {entry['name']}")
        if slug in slugs:
            raise ValueError(f"Duplicate public skill slug: {slug}")
        names.add(folded)
        slugs.add(slug)
        reviewed.append(entry)
    return reviewed


def validate_public_text(value: str, approved_proper_nouns: set[str]) -> None:
    """Reject common PII shapes and unreviewed proper nouns without logging values."""
    pii_patterns = [
        r"\b[A-Z][A-Za-z'’-]{2,}(?:\s+[A-Z][A-Za-z'’-]{2,}){0,2}\s+\d{1,5}[A-Za-z]?\b",
        r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
        r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        r"(?<!\w)(?:\+?\d[\s().-]?){8,}\d(?!\w)",
    ]
    if any(re.search(pattern, value, flags=re.IGNORECASE) for pattern in pii_patterns):
        raise ValueError("Reviewed public skill metadata contains PII-like data")

    for match in re.finditer(r"\b[A-Z][A-Za-z0-9]*(?:[-'][A-Za-z0-9]+)*\b", value):
        token = match.group(0)
        prefix = value[: match.start()].rstrip()
        at_sentence_start = not prefix or prefix[-1] in ".?!;"
        if not at_sentence_start and token not in approved_proper_nouns:
            raise ValueError("Reviewed public skill metadata contains an unapproved proper noun")


def validate_public_description(description: str, approved_proper_nouns: set[str]) -> None:
    """Require safe, grammatically complete visitor-facing copy."""
    validate_public_text(description, approved_proper_nouns)

    if not re.search(r'[.!?]["”’)]?$', description) or description.endswith(("...", "…")):
        raise ValueError("Reviewed public skill description must end with a complete sentence")
    terminal_word = re.search(r"([A-Za-z]+)[.!?][\"”’)]?$", description)
    if terminal_word and terminal_word.group(1).casefold() in DANGLING_DESCRIPTION_TAILS:
        raise ValueError("Reviewed public skill description has a dangling grammatical tail")

def select_public_skills(
    discovered: list[dict[str, str]], reviewed: list[PublicSkill]
) -> list[PublicSkill]:
    """Return only allowlisted skills with reviewed metadata.

    Runtime descriptions and operational metadata are deliberately ignored.
    """
    by_name = {str(skill.get("name", "")).casefold(): skill for skill in discovered}
    missing = [entry["name"] for entry in reviewed if entry["name"].casefold() not in by_name]
    if missing:
        raise ValueError("Allowlisted skills missing from registry: " + ", ".join(missing))
    return sorted(reviewed, key=lambda skill: (skill["category"], skill["name"]))


def discover(registry_json: Optional[Path] = None) -> list[dict[str, str]]:
    if registry_json is not None:
        return registry_from_json(registry_json)
    return enabled_skills_from_cli()


def render_sitemap(skill_routes: list[str]) -> str:
    sitemap = ROOT / "sitemap.xml"
    old = sitemap.read_text() if sitemap.exists() else ""
    oldmap = dict(re.findall(r"<loc>([^<]+)</loc>\n\s*<lastmod>([^<]+)</lastmod>", old))
    routes = list(skill_routes)
    for idx in ROOT.rglob("index.html"):
        rel = idx.relative_to(ROOT).as_posix()
        if rel.startswith((".git/", ".vercel/", "node_modules/", "skills/", ".skills-build-")):
            continue
        route = "/" if rel == "index.html" else "/" + str(Path(rel).parent).replace("\\", "/") + "/"
        routes.append(route)
    entries = []
    for route in sorted(set(routes), key=lambda r: (r.count("/"), r)):
        loc = BASE + route
        priority = "1.0" if route == "/" else ("0.8" if route in ["/uses/", "/tech-stack/", "/skills/"] else "0.7")
        entries.append(f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{oldmap.get(loc, TODAY)}</lastmod>\n    <priority>{priority}</priority>\n  </url>")
    return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(entries) + "\n</urlset>\n"


def render_homepage_count(skill_count: int) -> str:
    homepage = ROOT / "index.html"
    text = homepage.read_text(encoding="utf-8")
    label = f"{skill_count} skill{'s' if skill_count != 1 else ''}"
    rendered, replacements = re.subn(
        r'(<span class="card-tag" data-public-skill-count>)\d+ skills?(</span>)',
        rf"\g<1>{label}\g<2>",
        text,
    )
    if replacements != 1:
        raise ValueError("Homepage must contain exactly one public skill count marker")
    return rendered


def write_skills_tree(out: Path, skills: list[PublicSkill]) -> int:
    out.mkdir()
    (out / "skills-data.json").write_text(
        json.dumps(
            {"generated_at": TODAY, "count": len(skills), "skills": skills},
            ensure_ascii=False,
            indent=2,
        )
    )
    groups = defaultdict(list)
    for skill in skills:
        groups[skill["category"]].append(skill)
        body = f'''    <a class="back" href="/skills/">&larr; Skills</a>
    <header><div class="eyebrow">Skill / {esc(skill['category'])}</div><h1 class="title">{esc(skill['name'])}</h1><p class="subtitle">{esc(skill['description'])}</p><div class="meta"><span class="pill">reviewed workflow</span><span class="pill">{esc(skill['category'])}</span><span class="pill">reviewed {esc(skill['reviewed_at'])}</span></div></header>
    <section class="section"><h2 class="section-title">Capability and boundary</h2><div class="list"><article class="item"><strong>Use case</strong><p>{esc(skill['description'])}</p></article><article class="item"><strong>Implementation status</strong><p>{esc(skill['implementation_status'])}</p></article></div></section>
    <section class="section"><h2 class="section-title">Provenance</h2><div class="list"><article class="item"><strong>Maintainer</strong><p>{esc(skill['maintainer'])}</p></article><article class="item"><strong>Origin</strong><p>{esc(skill['origin'])}</p></article><article class="item"><strong>Attribution</strong><p>{esc(skill['attribution'])}</p></article><article class="item"><strong>Declared workflow license</strong><p>{esc(skill['declared_license'])}</p></article><article class="item"><strong>Review status</strong><p>Public summary reviewed on {esc(skill['reviewed_at'])}.</p></article></div></section>
    <section class="section"><h2 class="section-title">Next step</h2><div class="list"><a class="item next-link" href="/skills/"><strong>Compare the reviewed catalog</strong><p>Return to all public skill summaries and categories.</p></a></div></section>'''
        detail = out / slugify(skill["name"])
        detail.mkdir()
        (detail / "index.html").write_text(
            page(
                f"{skill['name']} — Hermes Skill Workflow",
                skill["description"],
                f"{BASE}/skills/{slugify(skill['name'])}/",
                body,
                include_script=False,
                robots=None if skill.get("indexable") else "noindex, follow",
            )
        )
    sections = []
    for category in sorted(groups):
        cards = []
        for skill in groups[category]:
            filt = (skill["name"] + " " + category + " " + skill["description"]).lower()
            cards.append(f'''      <a class="card" data-filter="{esc(filt)}" href="/skills/{slugify(skill['name'])}/"><div class="icon" aria-hidden="true">SK</div><div><h3>{esc(skill['name'])}</h3><p>{esc(skill['description'])}</p><div class="tiny"><span>{esc(category)}</span><span>reviewed summary</span></div></div></a>''')
        sections.append(f'''    <section class="section" data-skill-section data-category="{esc(category)}" data-total="{len(groups[category])}"><h2 class="section-title" data-section-title>{esc(category)} · {len(groups[category])}</h2><div class="grid">{''.join(cards)}</div></section>''')
    body = f'''    <a class="back" href="/">&larr; viggomeesters.com</a>\n    <header><div class="eyebrow">Reviewed capability catalog</div><h1 class="title">Reusable workflows, with their boundaries visible.</h1><p class="subtitle">Explore a curated set of public workflow summaries. Each entry identifies its purpose, maintenance status, provenance and declared license without publishing the private implementation.</p><div class="meta"><span class="pill">{len(skills)} reviewed skills</span><span class="pill">{len(groups)} categories</span><span class="pill">reviewed {TODAY}</span><span class="pill">generated from allowlist</span></div></header>\n    <label class="search-label" for="skill-search">Search the catalog</label><input id="skill-search" class="search" data-search placeholder="Try audit, accessibility or productivity…" type="search" autocomplete="off">\n    <div class="result-count" data-result-count data-total="{len(skills)}" data-categories="{len(groups)}" aria-live="polite">{len(skills)} skills across {len(groups)} categories</div>\n{''.join(sections)}'''
    (out / "index.html").write_text(
        page(
            "Hermes Skills Registry — Viggo Meesters",
            "Curated public workflow summaries with reviewed purpose, provenance, maintenance status and declared licensing.",
            f"{BASE}/skills/",
            body,
        )
    )
    return len(groups)


def replace_public_output(
    staged_skills: Path,
    staged_sitemap: Path,
    staged_homepage: Path,
) -> None:
    target = ROOT / "skills"
    backup = staged_skills.parent / "skills-backup"
    had_target = target.exists()
    file_targets = [
        (staged_sitemap, ROOT / "sitemap.xml", staged_skills.parent / "sitemap-backup"),
        (staged_homepage, ROOT / "index.html", staged_skills.parent / "homepage-backup"),
    ]
    existed: dict[Path, bool] = {}
    for _, file_target, file_backup in file_targets:
        existed[file_target] = file_target.exists()
        if existed[file_target]:
            if not file_target.is_file():
                raise ValueError(f"Public output target is not a file: {file_target.name}")
            shutil.copy2(file_target, file_backup)
    if had_target:
        target.rename(backup)
    try:
        staged_skills.rename(target)
        for staged_file, file_target, _ in file_targets:
            staged_file.replace(file_target)
    except Exception:
        if target.exists():
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()
        if had_target and backup.exists():
            backup.rename(target)
        for _, file_target, file_backup in file_targets:
            if file_backup.exists():
                file_backup.replace(file_target)
            elif not existed[file_target] and file_target.exists():
                file_target.unlink()
        raise


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site-root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument(
        "--allowlist",
        type=Path,
        help="Reviewed public skill manifest (default: <site-root>/scripts/public-skills.json)",
    )
    parser.add_argument(
        "--registry-json",
        type=Path,
        help="Captured runtime registry; defaults to `hermes skills list --enabled-only`",
    )
    return parser.parse_args()


def main() -> None:
    global ROOT
    args = parse_args()
    ROOT = args.site_root.resolve()
    allowlist_path = args.allowlist or (ROOT / "scripts" / "public-skills.json")
    reviewed = load_public_allowlist(allowlist_path)
    skills = select_public_skills(discover(args.registry_json), reviewed)
    with tempfile.TemporaryDirectory(prefix=".skills-build-", dir=str(ROOT)) as temp_dir:
        stage = Path(temp_dir)
        staged_skills = stage / "skills"
        category_count = write_skills_tree(staged_skills, skills)
        skill_routes = ["/skills/"] + [
            f"/skills/{slugify(skill['name'])}/"
            for skill in skills
            if skill.get("indexable")
        ]
        staged_sitemap = stage / "sitemap.xml"
        staged_sitemap.write_text(render_sitemap(skill_routes))
        staged_homepage = stage / "index.html"
        staged_homepage.write_text(render_homepage_count(len(skills)))
        replace_public_output(staged_skills, staged_sitemap, staged_homepage)
    print(f"Generated {len(skills)} skills across {category_count} categories")


if __name__ == "__main__":
    main()
