#!/usr/bin/env python3
"""Reject known-dead or structurally invalid links in public watcher snapshots."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "scripts" / "feed-link-policy.json"
FEEDS = (ROOT / "trendwatch" / "data.json", ROOT / "tech-news" / "data.json")


def check(root: Path = ROOT) -> list[str]:
    policy = json.loads((root / "scripts" / "feed-link-policy.json").read_text(encoding="utf-8"))
    if policy.get("schema") != "viggomeesters.feed-link-policy.v1":
        return ["feed-link policy schema is invalid"]
    blocked = set(policy.get("blocked_urls", []))
    errors: list[str] = []
    for relative in ("trendwatch/data.json", "tech-news/data.json"):
        payload = json.loads((root / relative).read_text(encoding="utf-8"))
        for index, item in enumerate(payload.get("items", [])):
            url = str(item.get("url", ""))
            parsed = urlparse(url)
            if url in blocked:
                errors.append(f"{relative} item {index} contains blocked dead URL: {url}")
            if parsed.scheme != "https" or not parsed.netloc:
                errors.append(f"{relative} item {index} has invalid public URL: {url}")
            if parsed.netloc == "github.com" and parsed.path.startswith("/articles/"):
                errors.append(f"{relative} item {index} uses a non-repository GitHub path: {url}")
    return errors


def main() -> int:
    errors = check()
    if errors:
        print("Feed link check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Feed link check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
