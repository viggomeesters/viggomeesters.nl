#!/usr/bin/env python3
"""generate-showcases.py — legacy showcase generator.

This script targets the old Agent Brain/Raycast Life OS source layout and can
reintroduce stale count-driven public copy. It is kept as a historical helper,
but write/dry-run execution now requires --legacy.

Legacy reads:
  - ~/Dev/agent-brain/context/registry.json
  - ~/Dev/raycast-life-os/extensions/life-os/package.json

Legacy updates content between <!-- BEGIN:section --> / <!-- END:section --> markers in:
  - agent-brain/index.html
  - raycast-life-os/index.html
"""

import argparse
import json
import re
import sys
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────

SITE_DIR = Path(__file__).resolve().parent
BRAIN_REGISTRY = Path.home() / "Dev/agent-brain/context/registry.json"
RLO_PACKAGE = Path.home() / "Dev/raycast-life-os/extensions/life-os/package.json"
RLO_SERVICES = Path.home() / "Dev/raycast-life-os/packages/core/src/services"
RLO_PAGE = SITE_DIR / "raycast-life-os/index.html"
BRAIN_PAGE = SITE_DIR / "agent-brain/index.html"

# ── Category metadata (name, prefixes/clusters, icon, css, description) ────

RLO_CATEGORIES = [
    ("Capture", ["Capture"], "+", "capture",
     "Create notes, tasks, health logs, and daily entries"),
    ("Save", ["Save"], "&#8615;", "save",
     "Capture emails, chats, and bookmarks from external apps"),
    ("PRM", ["PRM"], "&#9829;", "prm",
     "Contact management, decay tracking, and anniversaries"),
    ("Tasks", ["Tasks"], "&#9745;", "tasks",
     "Prioritized tasks, chores, rituals, and habits"),
    ("Browse", ["Browse"], "&#9776;", "browse",
     "References, media, projects, and purchases"),
    ("Search, Calendar & Review",
     ["Search", "Calendar", "Review", "Life OS"], "&#9670;", "review",
     "Vault search, calendar import, weekly review, and health"),
]

BRAIN_SKILL_CATEGORIES = [
    ("Audit", ["audit"], "&#9872;", "audit",
     "Comprehensive code quality frameworks"),
    ("Communication", ["comm"], "&#9993;", "comm",
     "Message drafting, email, and meeting workflows"),
    ("Development", ["dev"], "&#9998;", "dev",
     "Language and framework expertise"),
    ("Documentation", ["doc"], "&#9783;", "doc",
     "Document and file handling"),
    ("Git & CI", ["git", "gh"], "&#9741;", "git",
     "Version control and CI/CD workflows"),
    ("Work Management", ["work", "focus"], "&#9201;", "work",
     "Calendar, focus, and reporting"),
    ("Automation", ["standalone"], "&#9881;", "auto",
     "Core autonomous task execution"),
]

RLO_NOTE_TYPES = 12
RLO_AREAS = 4
BRAIN_TOOLS = 3


# ── Data loading ───────────────────────────────────────────────────────────

def load_rlo_commands():
    """Load and group RLO commands from package.json."""
    with open(RLO_PACKAGE) as f:
        data = json.load(f)
    commands = data.get("commands", [])
    grouped = {cat[0]: [] for cat in RLO_CATEGORIES}
    for cmd in commands:
        subtitle = cmd.get("subtitle", "")
        parts = re.split(r"[·•]", subtitle, maxsplit=1)
        prefix = parts[0].strip()
        placed = False
        for name, prefixes, *_ in RLO_CATEGORIES:
            if prefix in prefixes:
                grouped[name].append(cmd)
                placed = True
                break
        if not placed:
            grouped[RLO_CATEGORIES[-1][0]].append(cmd)
    return grouped, len(commands)


def count_rlo_services():
    """Count RLO service files."""
    if RLO_SERVICES.is_dir():
        return len(list(RLO_SERVICES.glob("*.ts")))
    return 29


def load_brain_data():
    """Load legacy Agent Brain data from registry.json."""
    with open(BRAIN_REGISTRY) as f:
        data = json.load(f)
    counts = data.get("counts", {})
    skills = data.get("skills", [])
    commands = data.get("commands", [])
    grouped = {cat[0]: [] for cat in BRAIN_SKILL_CATEGORIES}
    for skill in skills:
        cluster = skill.get("cluster", "")
        placed = False
        for name, clusters, *_ in BRAIN_SKILL_CATEGORIES:
            if cluster in clusters:
                grouped[name].append(skill)
                placed = True
                break
        if not placed:
            grouped[BRAIN_SKILL_CATEGORIES[-1][0]].append(skill)
    return grouped, commands, counts


# ── Description cleanup ────────────────────────────────────────────────────

def clean_desc(desc):
    """Strip metadata suffixes and truncate for showcase display."""
    desc = re.sub(r"\.\s*Use\b.*$", "", desc, flags=re.IGNORECASE)
    desc = re.sub(r"\.\s*Do NOT\b.*$", "", desc, flags=re.IGNORECASE)
    desc = re.sub(r"\.\s*Trigger[s ].*$", "", desc, flags=re.IGNORECASE)
    desc = desc.strip().rstrip(".")
    if len(desc) > 100:
        first = desc.split(". ")[0]
        if len(first) < len(desc):
            desc = first
    if len(desc) > 100:
        desc = desc[:97].rsplit(" ", 1)[0].rstrip(".,;:") + "\u2026"
    return desc


# ── HTML rendering ─────────────────────────────────────────────────────────

def render_stat(num, label):
    return (
        f"      <div class=\"stat\">\n"
        f"        <div class=\"stat-num\">{num}</div>\n"
        f"        <div class=\"stat-label\">{label}</div>\n"
        f"      </div>"
    )


def render_detail_item(name, desc):
    return (
        f"          <div class=\"detail-item\">"
        f"<span class=\"detail-name\">{name}</span>"
        f"<span class=\"detail-desc\">{desc}</span>"
        f"</div>"
    )


def render_details(name, desc, icon, css, items, item_fn):
    item_lines = "\n".join(item_fn(it) for it in items)
    return (
        f"      <details>\n"
        f"        <summary>\n"
        f"          <span class=\"summary-left\">\n"
        f"            <span class=\"summary-icon {css}\">{icon}</span>\n"
        f"            <span class=\"summary-text\">\n"
        f"              <span class=\"summary-name\">{name}</span>\n"
        f"              <span class=\"summary-desc\">{desc}</span>\n"
        f"            </span>\n"
        f"          </span>\n"
        f"          <span class=\"summary-count\">{len(items)}</span>\n"
        f"          <span class=\"chevron\">&#9654;</span>\n"
        f"        </summary>\n"
        f"        <div class=\"detail-list\">\n"
        f"{item_lines}\n"
        f"        </div>\n"
        f"      </details>"
    )


# ── Section generators ─────────────────────────────────────────────────────

def generate_rlo_stats(cmd_count, svc_count):
    stats = "\n".join([
        render_stat(cmd_count, "Commands"),
        render_stat(svc_count, "Services"),
        render_stat(RLO_NOTE_TYPES, "Note Types"),
        render_stat(RLO_AREAS, "Areas"),
    ])
    return (
        f"    <div class=\"stats reveal\">\n"
        f"{stats}\n"
        f"    </div>"
    )


def generate_rlo_commands(grouped, total):
    parts = [
        f"    <div class=\"reveal\">",
        f"      <div class=\"section-label\" style=\"--dot-color: #f97316\">Commands ({total})</div>",
        "",
    ]
    for name, prefixes, icon, css, desc in RLO_CATEGORIES:
        items = grouped[name]
        if not items:
            continue
        item_fn = lambda cmd: render_detail_item(cmd["title"], cmd["description"])
        parts.append(render_details(name, desc, icon, css, items, item_fn))
        parts.append("")
    parts.append("    </div>")
    return "\n".join(parts)


def generate_brain_stats(counts):
    stats = "\n".join([
        render_stat(counts.get("skills", 0), "Skills"),
        render_stat(counts.get("commands", 0), "Commands"),
        render_stat(counts.get("scripts", 0), "Scripts"),
        render_stat(BRAIN_TOOLS, "Tools"),
    ])
    return (
        f"    <div class=\"stats reveal\">\n"
        f"{stats}\n"
        f"    </div>"
    )


def generate_brain_skills(grouped, total):
    parts = [
        f"    <div class=\"reveal\">",
        f"      <div class=\"section-label\" style=\"--dot-color: #22c55e\">Skills ({total})</div>",
        "",
    ]
    for name, clusters, icon, css, desc in BRAIN_SKILL_CATEGORIES:
        items = grouped[name]
        if not items:
            continue
        item_fn = lambda s: render_detail_item(s["name"], clean_desc(s["description"]))
        parts.append(render_details(name, desc, icon, css, items, item_fn))
        parts.append("")
    parts.append("    </div>")
    return "\n".join(parts)


def generate_brain_commands(commands, total):
    item_fn = lambda c: render_detail_item(f'/{c["name"]}', clean_desc(c["description"]))
    details = render_details(
        "Slash Commands", "Quick-access workflows invoked via /command",
        "/", "cmd", commands, item_fn,
    )
    return "\n".join([
        f"    <div class=\"reveal\">",
        f"      <div class=\"section-label\" style=\"--dot-color: #818cf8\">Commands ({total})</div>",
        "",
        details,
        "",
        "    </div>",
    ])


# ── Marker replacement ─────────────────────────────────────────────────────

def replace_section(html, section, content):
    """Replace content between BEGIN/END markers, preserving marker indentation."""
    pattern = (
        rf"([ \t]*<!-- BEGIN:{re.escape(section)} -->)\n"
        rf".*?\n"
        rf"([ \t]*<!-- END:{re.escape(section)} -->)"
    )
    def repl(m):
        return f"{m.group(1)}\n{content}\n{m.group(2)}"
    new_html, n = re.subn(pattern, repl, html, count=1, flags=re.DOTALL)
    if n == 0:
        print(f"  WARNING: markers for {section} not found", file=sys.stderr)
    return new_html


# ── Page updaters ──────────────────────────────────────────────────────────

def update_rlo_page(dry_run=False):
    print("── Raycast Life OS ──")
    grouped, cmd_count = load_rlo_commands()
    svc_count = count_rlo_services()
    for name, *_ in RLO_CATEGORIES:
        print(f"  {name}: {len(grouped[name])}")
    print(f"  Total: {cmd_count} commands, {svc_count} services")

    if dry_run:
        print(f"  [dry-run] Would update {RLO_PAGE}")
        return

    html = RLO_PAGE.read_text()

    # Replace marked sections
    html = replace_section(html, "stats", generate_rlo_stats(cmd_count, svc_count))
    html = replace_section(html, "commands", generate_rlo_commands(grouped, cmd_count))

    # Update meta description
    meta = (
        f"A personal knowledge system built on Obsidian and Raycast. "
        f"{cmd_count} commands, {RLO_NOTE_TYPES} note types, contact CRM, "
        f"health tracking, and an open-source starter vault."
    )
    html = re.sub(
        r'<meta name="description" content="[^"]*">',
        f'<meta name="description" content="{meta}">',
        html,
    )

    # Update command count in subtitle
    html = re.sub(r"\b\d+ commands\b", f"{cmd_count} commands", html)

    RLO_PAGE.write_text(html)
    print(f"  Updated {RLO_PAGE}")


def update_brain_page(dry_run=False):
    print("── Legacy Agent Brain ──")
    grouped, commands, counts = load_brain_data()
    n_skills = counts.get("skills", 0)
    n_cmds = counts.get("commands", 0)
    n_scripts = counts.get("scripts", 0)
    for name, *_ in BRAIN_SKILL_CATEGORIES:
        print(f"  {name}: {len(grouped[name])}")
    print(f"  Total: {n_skills} skills, {n_cmds} commands, {n_scripts} scripts")

    if dry_run:
        print(f"  [dry-run] Would update {BRAIN_PAGE}")
        return

    html = BRAIN_PAGE.read_text()

    # Replace marked sections
    html = replace_section(html, "stats", generate_brain_stats(counts))
    html = replace_section(html, "skills", generate_brain_skills(grouped, n_skills))
    html = replace_section(html, "commands", generate_brain_commands(commands, n_cmds))

    # Update meta description
    meta = (
        f"Deterministic autopilot for coordinating Claude, Codex, and Gemini. "
        f"{n_skills} skills, {n_cmds} commands, {n_scripts} scripts."
    )
    html = re.sub(
        r'<meta name="description" content="[^"]*">',
        f'<meta name="description" content="{meta}">',
        html,
    )

    # Update architecture diagram skill count
    html = re.sub(r"\d+ Skills", f"{n_skills} Skills", html)

    BRAIN_PAGE.write_text(html)
    print(f"  Updated {BRAIN_PAGE}")


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Regenerate showcase pages")
    ap.add_argument("--dry-run", action="store_true", help="Preview without writing")
    ap.add_argument("--legacy", action="store_true", help="Run the deprecated legacy generator intentionally")
    ap.add_argument("--brain-only", action="store_true")
    ap.add_argument("--rlo-only", action="store_true")
    args = ap.parse_args()

    if not args.legacy:
        print(
            "This generator is deprecated and can reintroduce stale public copy. "
            "Pass --legacy to run it intentionally.",
            file=sys.stderr,
        )
        sys.exit(2)

    if not args.brain_only:
        update_rlo_page(args.dry_run)
    if not args.rlo_only:
        update_brain_page(args.dry_run)

    if not args.dry_run:
        print("\nDone. Run 'git diff --stat' to review changes.")


if __name__ == "__main__":
    main()
