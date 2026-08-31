#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "public-projects.json"
ACCOUNT = "viggomeesters"


def public_pages() -> dict[str, str]:
    pages: dict[str, str] = {}
    for path in sorted(ROOT.rglob("index.html")):
        relative = path.relative_to(ROOT)
        if any(part in {"node_modules", ".git", ".vercel", "reports"} for part in relative.parts):
            continue
        pages[relative.as_posix()] = path.read_text(encoding="utf-8", errors="ignore")
    return pages


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
    previous: dict[str, list[str]] = {}
    if DATA.exists():
        current = json.loads(DATA.read_text(encoding="utf-8"))
        previous = {
            item["name"]: item.get("site_evidence", [])
            for item in current.get("repositories", [])
        }
    repositories = live_repositories()
    for item in repositories:
        item["site_evidence"] = previous.get(str(item["name"]), [])
    payload = {
        "account": ACCOUNT,
        "snapshot_date": date.today().isoformat(),
        "scope": "Active public source repositories; archived repositories and forks are excluded.",
        "repositories": repositories,
    }
    DATA.parent.mkdir(parents=True, exist_ok=True)
    DATA.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Refreshed {len(repositories)} active public repositories. New repositories keep empty site_evidence until deliberately placed.")
    return 0


def check() -> int:
    source = json.loads(DATA.read_text(encoding="utf-8"))
    repositories = source.get("repositories", [])
    pages = public_pages()
    errors: list[str] = []
    for item in repositories:
        name = item["name"]
        url = item["url"]
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
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"Public project coverage failed: {len(repositories) - len(errors)}/{len(repositories)} repositories covered.", file=sys.stderr)
        return 1
    print(f"Public project coverage passed: {len(repositories)}/{len(repositories)} active public repositories have declared HTML evidence.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit public GitHub repository coverage on viggomeesters.com")
    parser.add_argument("--refresh", action="store_true", help="Refresh the GitHub snapshot; requires gh authentication and network access")
    args = parser.parse_args()
    return refresh() if args.refresh else check()


if __name__ == "__main__":
    raise SystemExit(main())
