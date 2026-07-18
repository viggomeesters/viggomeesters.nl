#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "timeline" / "coverage.json"
TIMELINE = ROOT / "timeline" / "index.html"
SITEMAP = ROOT / "sitemap.xml"

MONTHS = ("", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


def e(value: object) -> str:
    return html.escape(str(value), quote=True)


def display_date(value: str) -> str:
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        year, month, day = value.split("-")
        return f"{int(day):02d} {MONTHS[int(month)]} {year}"
    return value


def validate(source: dict) -> list[dict]:
    entries = source.get("entries", [])
    required = {"id", "date", "date_label", "type", "type_label", "number_label", "title", "description", "links"}
    ids: set[str] = set()
    for item in entries:
        missing = required - item.keys()
        if missing:
            raise ValueError(f"{item.get('id', '<unknown>')} misses: {', '.join(sorted(missing))}")
        if item["id"] in ids:
            raise ValueError(f"Duplicate coverage id: {item['id']}")
        ids.add(item["id"])
        date.fromisoformat(item["date"])
        if not item["links"]:
            raise ValueError(f"{item['id']} has no proof link")
    return entries


def render_link(link: dict) -> str:
    attrs = ' target="_blank" rel="noopener"' if link.get("external") else ""
    return f'<a href="{e(link["href"])}"{attrs}>{e(link["label"])}</a>'


def render_entry(item: dict) -> str:
    links = "".join(render_link(link) for link in item["links"])
    label = display_date(item["date_label"])
    return f'''<article class="timeline-entry" data-date="{e(item["date"])}" data-type="{e(item["type"])}" data-coverage="{e(item["id"])}">
        <div class="entry-meta"><time class="entry-date" datetime="{e(item["date"])}">{e(label)}</time><span class="entry-type">{e(item["type_label"])}</span></div>
        <div class="entry-body"><span class="entry-number">{e(item["number_label"])}</span><h3>{e(item["title"])}</h3><p>{e(item["description"])}</p><div class="proof-links">{links}</div></div>
      </article>'''


def sort_key(entry: str) -> tuple[str, str]:
    match = re.search(r'data-date="([^"]+)"', entry)
    if not match:
        raise ValueError("Timeline entry without data-date")
    return match.group(1), entry


def sync_timeline(content: str, entries: list[dict]) -> str:
    certificate_rule = '.timeline-entry[data-type="certificate"]{--entry:#ffd166}'
    extra_rules = '.timeline-entry[data-type="employment"]{--entry:#ff7b72}.timeline-entry[data-type="education"]{--entry:#4fd1a1}'
    if extra_rules not in content:
        content = content.replace(certificate_rule, certificate_rule + extra_rules)

    employment_filter = '<button class="filter" type="button" data-filter="employment" aria-pressed="false">Work</button>'
    education_filter = '<button class="filter" type="button" data-filter="education" aria-pressed="false">Education</button>'
    career_filter = '<button class="filter" type="button" data-filter="career" aria-pressed="false">Professional</button>'
    if 'data-filter="employment"' not in content:
        content = content.replace(career_filter, career_filter + "\n        " + employment_filter + "\n        " + education_filter)

    section_match = re.search(r'(<section class="timeline" aria-label="Work and build timeline">)([\s\S]*?)(\n    </section>)', content)
    if not section_match:
        raise ValueError("Timeline section not found")
    existing = re.findall(r'<article class="timeline-entry[^>]*>[\s\S]*?</article>', section_match.group(2))
    existing = [entry for entry in existing if 'data-coverage=' not in entry and 'data-type="repository"' not in entry]
    combined = existing + [render_entry(item) for item in entries]
    combined.sort(key=sort_key, reverse=True)
    replacement = section_match.group(1) + "\n      " + "\n\n      ".join(entry.strip() for entry in combined) + section_match.group(3)
    content = content[:section_match.start()] + replacement + content[section_match.end():]
    content = re.sub(r'>\d+ milestones shown</span>', f'>{len(combined)} milestones shown</span>', content, count=1)
    content = content.replace("since 2014", "since 2006")
    content = content.replace("from 2014 to now", "from 2006 to now")
    content = content.replace("2014 to now", "2006 to now")
    content = content.replace("2014—now", "2006—now")
    content = content.replace(
        "Explore Viggo Meesters&apos; projects, credentials, products, repositories, systems, and writing",
        "Explore Viggo Meesters&apos; work, education, projects, credentials, products, repositories, systems, and writing",
    )
    content = content.replace(
        "Professional projects, products, repositories, systems, and writing since",
        "Work, education, professional projects, products, repositories, systems, and writing since",
    )
    if "work, education, professional projects" not in content:
        content = content.replace(
            "professional projects, credentials, products, repositories, systems, and ideas",
            "work, education, professional projects, credentials, products, repositories, systems, and ideas",
        )
    return content


def sync_sitemap(content: str) -> str:
    pattern = r'(<loc>https://viggomeesters\.com/timeline/</loc>\s*<lastmod>)[^<]+(</lastmod>)'
    return re.sub(pattern, r'\g<1>2026-07-18\g<2>', content, count=1)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    entries = validate(json.loads(SOURCE.read_text(encoding="utf-8")))
    expected_timeline = sync_timeline(TIMELINE.read_text(encoding="utf-8"), entries)
    expected_sitemap = sync_sitemap(SITEMAP.read_text(encoding="utf-8"))
    if args.check:
        stale = []
        if TIMELINE.read_text(encoding="utf-8") != expected_timeline:
            stale.append("timeline/index.html")
        if SITEMAP.read_text(encoding="utf-8") != expected_sitemap:
            stale.append("sitemap.xml")
        if stale:
            print("Timeline coverage is stale: " + ", ".join(stale), file=sys.stderr)
            return 1
        print(f"Timeline coverage check passed: {len(entries)} generated cards.")
        return 0
    TIMELINE.write_text(expected_timeline, encoding="utf-8")
    SITEMAP.write_text(expected_sitemap, encoding="utf-8")
    print(f"Generated {len(entries)} timeline coverage cards.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
