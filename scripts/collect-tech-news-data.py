#!/usr/bin/env python3
"""Daily public tech-news watcher for viggomeesters.com.

- Reads public RSS/Atom feeds only; no credentials.
- Writes a compact public-safe JSON snapshot to /tech-news/data.json.
- Optionally commits and pushes only that generated data file for the static site.
- Prints a compact digest only when publish changes are made or on errors.
"""
from __future__ import annotations

import argparse
import email.utils
import hashlib
import html
import json
import os
import re
import subprocess
import sys
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SITE_REPO = Path(os.environ.get("TECH_NEWS_SITE_REPO", "/home/viggo/github/viggomeesters.nl")).expanduser()
OUT = SITE_REPO / "tech-news" / "data.json"
USER_AGENT = "BertusTechNewswatcher/0.1 (+https://viggomeesters.com)"

FEEDS: dict[str, str] = {
    "Hacker News": "https://news.ycombinator.com/rss",
    "Lobsters": "https://lobste.rs/rss",
    "The Verge": "https://www.theverge.com/rss/index.xml",
    "TechCrunch": "https://techcrunch.com/feed/",
    "Ars Technica": "https://feeds.arstechnica.com/arstechnica/index",
    "MIT Technology Review": "https://www.technologyreview.com/feed/",
    "GitHub Blog": "https://github.blog/feed/",
    "OpenAI News": "https://openai.com/news/rss.xml",
    "Simon Willison": "https://simonwillison.net/atom/everything/",
    "Wired": "https://www.wired.com/feed/rss",
}

AREAS: dict[str, list[str]] = {
    "ai-agents": ["agent", "agents", "agentic", "computer use", "tool use", "mcp", "model context protocol", "coding agent", "autonomous"],
    "models": ["llm", "language model", "openai", "anthropic", "claude", "gpt", "gemini", "llama", "mistral", "reasoning model", "inference"],
    "developer-tools": ["github", "git", "developer", "devtool", "cli", "terminal", "ide", "copilot", "codex", "cursor", "debug", "observability"],
    "data-platforms": ["data", "etl", "warehouse", "duckdb", "sqlite", "database", "analytics", "pipeline", "semantic layer"],
    "enterprise-ai": ["enterprise", "sap", "salesforce", "microsoft", "google cloud", "aws", "azure", "workflow", "automation"],
    "privacy-risk": ["privacy", "security", "breach", "lawsuit", "regulation", "copyright", "safety", "attack", "vulnerability"],
}
NOISE = ["phone", "iphone", "android", "tesla", "streaming", "gaming", "crypto", "meme", "celebrity"]

@dataclass
class Item:
    title: str
    url: str
    source: str
    published: str
    summary: str


def http_get(url: str, timeout: int = 30) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/rss+xml, application/atom+xml, text/xml;q=0.9, */*;q=0.1"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def strip_html(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", value or "")
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def parse_date(value: str) -> str:
    if not value:
        return ""
    try:
        dt = email.utils.parsedate_to_datetime(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone().isoformat(timespec="seconds")
    except Exception:
        return strip_html(value)[:80]


def child_text(el: ET.Element, names: list[str]) -> str:
    for name in names:
        found = el.find(name)
        if found is not None and found.text:
            return found.text
    # namespace-agnostic fallback
    wanted = {n.split("}")[-1] for n in names}
    for child in list(el):
        if child.tag.split("}")[-1] in wanted and child.text:
            return child.text
    return ""


def child_link(el: ET.Element) -> str:
    for child in list(el):
        tag = child.tag.split("}")[-1]
        if tag == "link":
            href = child.attrib.get("href")
            if href:
                return href
            if child.text:
                return child.text
    return ""


def parse_feed(source: str, raw: bytes) -> list[Item]:
    root = ET.fromstring(raw)
    items = root.findall(".//item")
    if not items:
        items = [el for el in root.iter() if el.tag.split("}")[-1] == "entry"]
    out: list[Item] = []
    for el in items[:30]:
        title = strip_html(child_text(el, ["title", "{http://www.w3.org/2005/Atom}title"]))
        url = child_link(el).strip()
        published = parse_date(child_text(el, ["pubDate", "published", "updated", "{http://www.w3.org/2005/Atom}published", "{http://www.w3.org/2005/Atom}updated"]))
        summary = strip_html(child_text(el, ["description", "summary", "content", "{http://www.w3.org/2005/Atom}summary", "{http://www.w3.org/2005/Atom}content"]))[:360]
        if title and url:
            out.append(Item(title=title, url=url, source=source, published=published, summary=summary))
    return out


def score(item: Item) -> dict[str, Any]:
    text = " ".join([item.title, item.summary, item.source]).lower()
    matches = {area: [w for w in words if w in text][:5] for area, words in AREAS.items() if any(w in text for w in words)}
    noise = [w for w in NOISE if w in text]
    relevance = min(5, len(matches) + (1 if any(a in matches for a in ["ai-agents", "models", "developer-tools", "data-platforms"]) else 0))
    leverage = min(5, len(matches.get("ai-agents", [])) // 2 + len(matches.get("developer-tools", [])) // 2 + len(matches.get("data-platforms", [])) // 2 + (1 if item.source in {"GitHub Blog", "OpenAI News", "Simon Willison"} else 0))
    novelty = 4 if any(w in text for w in ["launch", "release", "new", "announces", "introduces", "open source"]) else 2 + min(2, len(matches))
    urgency = 4 if any(w in text for w in ["security", "breach", "vulnerability", "lawsuit", "shutdown", "deprecated", "pricing"]) else 2 + (1 if relevance >= 4 else 0)
    risk = min(5, len(matches.get("privacy-risk", [])) + len(noise))
    if relevance <= 1 and noise:
        risk = max(risk, 3)
    priority = max(0, min(100, 28 + relevance * 10 + leverage * 8 + novelty * 4 + urgency * 3 - risk * 8))
    if priority >= 84 and risk <= 3:
        action, detail = "Read", "High-signal; worth opening today"
    elif priority >= 72 and risk <= 3:
        action, detail = "Watch", "Relevant, but not urgent"
    elif risk >= 4 or relevance <= 1:
        action, detail = "Skip", "Low fit or noisy consumer-tech item"
    else:
        action, detail = "Ledger", "Keep as context/provenance"
    return {
        "areas": sorted(matches),
        "matchedKeywords": matches,
        "scores": {"relevance": relevance, "leverage": leverage, "novelty": min(5, novelty), "urgency": min(5, urgency), "risk": risk},
        "priority": priority,
        "action": action,
        "actionDetail": detail,
    }


def item_id(url: str, title: str) -> str:
    return hashlib.sha1(f"{url}|{title}".encode("utf-8")).hexdigest()[:16]


def collect(limit: int) -> tuple[list[dict[str, Any]], dict[str, str]]:
    seen: set[str] = set()
    rows: list[dict[str, Any]] = []
    errors: dict[str, str] = {}
    for source, url in FEEDS.items():
        try:
            for item in parse_feed(source, http_get(url)):
                key = item.url.lower().split("?")[0]
                if key in seen:
                    continue
                seen.add(key)
                sc = score(item)
                rows.append({
                    "id": item_id(item.url, item.title),
                    "title": item.title,
                    "url": item.url,
                    "source": item.source,
                    "published": item.published,
                    "summary": item.summary,
                    **sc,
                })
        except Exception as exc:
            errors[source] = str(exc)[:220]
    rows.sort(key=lambda r: (r.get("priority") or 0, r.get("published") or ""), reverse=True)
    return rows[:limit], errors


def run(cmd: list[str], *, cwd: Path = SITE_REPO) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)


def publish_if_changed() -> tuple[bool, str]:
    status = run(["git", "status", "--porcelain", "--", "tech-news/data.json"])
    if not status.stdout.strip():
        return False, ""
    run(["git", "add", "tech-news/data.json"])
    commit = run(["git", "commit", "-m", "chore: update tech news snapshot"])
    if commit.returncode != 0:
        return False, commit.stdout.strip()
    push = run(["git", "push"])
    return push.returncode == 0, (commit.stdout + push.stdout).strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=90)
    parser.add_argument("--no-publish", action="store_true", help="write JSON only; do not commit/push")
    parser.add_argument("--quiet", action="store_true", help="only print errors")
    args = parser.parse_args()

    items, errors = collect(args.limit)
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    useful = sum(1 for i in items if i.get("action") in {"Read", "Watch"})
    payload = {
        "generatedAt": now,
        "source": "public RSS/Atom feeds",
        "total": len(items),
        "usefulOpen": useful,
        "sources": list(FEEDS.keys()),
        "errors": errors,
        "items": items,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if args.no_publish:
        if not args.quiet:
            print(f"exported {len(items)} tech-news items to {OUT} ({useful} useful)")
        return 0

    ok, detail = publish_if_changed()
    if ok and not args.quiet:
        top = [i for i in items if i.get("action") in {"Read", "Watch"}][:5]
        print(f"## 🟣 Tech Newswatcher — {datetime.now().astimezone().strftime('%Y-%m-%d %H:%M %Z')}")
        print(f"Samenvatting: {useful} useful / {len(items)} items · pagina bijgewerkt")
        for idx, item in enumerate(top, 1):
            print(f"{idx}. {item['title']} — {item['source']} · {item['action']} · priority {item['priority']}")
            print(f"   {item['url']}")
        print("Pagina: https://viggomeesters.com/tech-news/")
    elif detail and not args.quiet:
        print(detail)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
