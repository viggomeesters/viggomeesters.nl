#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "public-projects.json"
ACCOUNT = "viggomeesters"
REPOSITORY_URL_RE = re.compile(r"https://github\.com/viggomeesters/([A-Za-z0-9_.-]+)")


def public_pages() -> dict[str, str]:
    pages: dict[str, str] = {}
    for path in sorted(ROOT.rglob("*.html")):
        relative = path.relative_to(ROOT)
        if any(part in {"node_modules", ".git", ".vercel", "reports"} for part in relative.parts):
            continue
        pages[relative.as_posix()] = path.read_text(encoding="utf-8", errors="ignore")
    return pages


def repository_mentions(pages: dict[str, str]) -> dict[str, list[str]]:
    mentions: dict[str, list[str]] = {}
    for path, markup in pages.items():
        for name in REPOSITORY_URL_RE.findall(markup):
            mentions.setdefault(name, []).append(path)
    return {name: sorted(set(paths)) for name, paths in sorted(mentions.items())}


def live_repositories() -> list[dict[str, object]]:
    command = [
        "gh", "repo", "list", ACCOUNT, "--limit", "200", "--source", "--json",
        "name,description,url,visibility,isArchived,isFork,createdAt,pushedAt",
    ]
    result = subprocess.run(command, cwd=ROOT, check=True, text=True, capture_output=True)
    repositories = json.loads(result.stdout)
    return sorted(
        (
            {
                "name": item["name"],
                "url": item["url"],
                "description": item.get("description") or "",
                "created_at": item["createdAt"],
                "pushed_at": item["pushedAt"],
            }
            for item in repositories
            if item["visibility"] == "PUBLIC" and not item["isArchived"] and not item["isFork"]
        ),
        key=lambda item: str(item["name"]).lower(),
    )


def refresh() -> int:
    current: dict[str, object] = {}
    previous: dict[str, dict[str, object]] = {}
    if DATA.exists():
        current = json.loads(DATA.read_text(encoding="utf-8"))
        previous = {
            item["name"]: {
                "site_evidence": item.get("site_evidence", []),
                "freshness": item.get("freshness"),
            }
            for item in current.get("repositories", [])
        }
    repositories = live_repositories()
    for item in repositories:
        prior = previous.get(str(item["name"]), {})
        item["site_evidence"] = prior.get("site_evidence", [])
        if prior.get("freshness") is not None:
            item["freshness"] = prior["freshness"]
    payload = {
        "account": ACCOUNT,
        "snapshot_date": date.today().isoformat(),
        "scope": "Active public source repositories; archived repositories and forks are excluded and classified separately.",
        "freshness_audit": current.get("freshness_audit"),
        "repositories": repositories,
        "excluded_repositories": current.get("excluded_repositories", []),
        "renamed_aliases": current.get("renamed_aliases", []),
    }
    DATA.parent.mkdir(parents=True, exist_ok=True)
    DATA.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"Refreshed {len(repositories)} active public repositories. "
        "New repositories keep empty site_evidence until deliberately placed; exclusions and aliases are preserved for explicit re-review."
    )
    return 0


def validate_coverage(source: dict[str, object], pages: dict[str, str]) -> list[str]:
    errors: list[str] = []
    repositories = source.get("repositories")
    exclusions = source.get("excluded_repositories")
    aliases = source.get("renamed_aliases")
    if not isinstance(repositories, list):
        return ["repositories: expected list"]
    if not isinstance(exclusions, list):
        return ["excluded_repositories: expected list"]
    if not isinstance(aliases, list):
        return ["renamed_aliases: expected list"]

    active_names = {item.get("name") for item in repositories if isinstance(item, dict)}
    excluded_names = {item.get("name") for item in exclusions if isinstance(item, dict)}
    overlap = sorted(name for name in active_names & excluded_names if isinstance(name, str))
    if overlap:
        errors.append(f"active and excluded inventories overlap: {', '.join(overlap)}")

    for label, items in (("active", repositories), ("excluded", exclusions)):
        seen: set[str] = set()
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                errors.append(f"{label}[{index}]: expected object")
                continue
            name = item.get("name")
            url = item.get("url")
            if not isinstance(name, str) or not name:
                errors.append(f"{label}[{index}].name: missing")
                continue
            if name in seen:
                errors.append(f"{label} {name}: duplicate classification")
            seen.add(name)
            if not isinstance(url, str) or not url:
                errors.append(f"{name}: missing canonical repository URL")
                continue
            actual = sorted(path for path, markup in pages.items() if url in markup)
            declared = sorted(item.get("site_evidence", []))
            if not actual:
                errors.append(f"{name}: repository URL is absent from all public HTML")
                continue
            if not declared:
                errors.append(f"{name}: site_evidence is empty; classify and place the repository deliberately")
                continue
            stale = [path for path in declared if path not in actual]
            if stale:
                errors.append(f"{name}: stale site_evidence: {', '.join(stale)}")
            undeclared = [path for path in actual if path not in declared]
            if undeclared:
                errors.append(f"{name}: undeclared public HTML evidence: {', '.join(undeclared)}")

    mentions = repository_mentions(pages)
    classified = {name for name in active_names | excluded_names if isinstance(name, str)}
    unclassified = sorted(set(mentions) - classified)
    if unclassified:
        errors.append(f"unclassified public repository mentions: {', '.join(unclassified)}")

    for index, alias in enumerate(aliases):
        if not isinstance(alias, dict):
            errors.append(f"renamed_aliases[{index}]: expected object")
            continue
        name = alias.get("name")
        previous_url = alias.get("previous_url")
        canonical = alias.get("canonical_repository")
        canonical_url = alias.get("canonical_url")
        corrected_files = alias.get("corrected_files")
        if not all(isinstance(value, str) and value for value in (name, previous_url, canonical, canonical_url)):
            errors.append(f"renamed_aliases[{index}]: incomplete alias classification")
            continue
        lingering = sorted(path for path, markup in pages.items() if previous_url in markup)
        if lingering:
            errors.append(f"{name}: renamed repository alias still appears in {', '.join(lingering)}")
        if canonical not in active_names:
            errors.append(f"{name}: canonical repository {canonical} is not in active inventory")
        if not isinstance(corrected_files, list) or not corrected_files:
            errors.append(f"{name}: corrected_files evidence is empty")
            continue
        for path in corrected_files:
            markup = pages.get(path)
            if markup is None:
                errors.append(f"{name}: corrected file is not public HTML: {path}")
            elif canonical_url not in markup:
                errors.append(f"{name}: canonical URL missing from corrected file {path}")

    return errors


def check() -> int:
    source = json.loads(DATA.read_text(encoding="utf-8"))
    pages = public_pages()
    errors = validate_coverage(source, pages)
    repositories = source.get("repositories", [])
    exclusions = source.get("excluded_repositories", [])
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"Public project coverage failed with {len(errors)} issue(s).", file=sys.stderr)
        return 1
    print(
        f"Public project coverage passed: {len(repositories)}/{len(repositories)} active public repositories covered; "
        f"{len(exclusions)} historical/fork mentions explicitly classified."
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit public GitHub repository coverage on viggomeesters.com")
    parser.add_argument("--refresh", action="store_true", help="Refresh the GitHub snapshot; requires gh authentication and network access")
    args = parser.parse_args()
    return refresh() if args.refresh else check()


if __name__ == "__main__":
    raise SystemExit(main())
