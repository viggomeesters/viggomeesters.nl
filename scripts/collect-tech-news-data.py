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
import math
import os
import re
import subprocess
import sys
import tempfile
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

SITE_REPO = Path(os.environ.get("TECH_NEWS_SITE_REPO", "/home/viggo/github/viggomeesters.nl")).expanduser()
OUT = SITE_REPO / "tech-news" / "data.json"
USER_AGENT = "BertusTechNewswatcher/0.1 (+https://viggomeesters.com)"
DEFAULT_MIN_SUCCESSFUL_SOURCES = 3
DEFAULT_MIN_ITEMS = 10
MIN_RETENTION_RATIO = 0.5
PUBLISH_BRANCH = os.environ.get("TECH_NEWS_PUBLISH_BRANCH", "main")
PUBLISH_REMOTE = os.environ.get("TECH_NEWS_PUBLISH_REMOTE", "origin")
PUBLISH_PATH = "tech-news/data.json"

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
    "ai-agents": ["ai agent", "ai agents", "agent", "agents", "agentic", "computer use", "tool use", "mcp", "model context protocol", "coding agent", "autonomous"],
    "models": ["llm", "language model", "openai", "anthropic", "claude", "gpt", "chatgpt", "gemini", "llama", "mistral", "reasoning model", "inference"],
    "developer-tools": ["github", "git", "developer", "devtool", "cli", "terminal", "ide", "copilot", "codex", "cursor", "debug", "observability"],
    "data-platforms": ["data", "etl", "warehouse", "duckdb", "sqlite", "database", "analytics", "pipeline", "semantic layer"],
    "enterprise-ai": ["enterprise", "sap", "salesforce", "microsoft", "google cloud", "aws", "azure", "workflow", "automation"],
    "privacy-risk": ["privacy", "security", "breach", "lawsuit", "regulation", "copyright", "safety", "attack", "vulnerability"],
}
NOISE = ["phone", "iphone", "android", "tesla", "streaming", "gaming", "crypto", "meme", "celebrity"]
AMBIGUOUS_AGENT_TERMS = {"agent", "agents", "autonomous"}
GENERIC_AGENT_CAPABILITY_TERMS = {"computer use", "tool use"}
EXPLICIT_AI_AGENT_SIGNALS = [
    "ai agent",
    "ai agents",
    "agentic",
    "coding agent",
    "coding agents",
    "llm agent",
    "llm agents",
    "software agent",
    "software agents",
    "autonomous agent",
    "autonomous agents",
    "agent workflow",
    "agent workflows",
    "ai powered agent",
    "ai powered agents",
    "agents powered by ai",
]
AI_ENTITY_SIGNALS = [
    "openai",
    "chatgpt",
    "anthropic",
    "claude",
    "gpt",
    "gemini",
    "llama",
    "mistral",
    "copilot",
    "codex",
    "llm",
    "language model",
]
AGENT_RELATION_SIGNALS = [
    "is an agent",
    "are agents",
    "became an agent",
    "becomes an agent",
    "acts as an agent",
    "functions as an agent",
]

@dataclass
class Item:
    title: str
    url: str
    source: str
    published: str
    summary: str


@dataclass(frozen=True)
class PublishResult:
    state: str
    detail: str = ""


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


def contains_term(text: str, term: str) -> bool:
    def normalize(value: str) -> str:
        value = re.sub(r"[-‐‑‒–—_/]+", " ", value.lower())
        return re.sub(r"\s+", " ", value).strip()

    escaped = re.escape(normalize(term)).replace(r"\ ", r"\s+")
    return re.search(rf"(?<!\w){escaped}(?!\w)", normalize(text)) is not None


def has_ai_agent_relation(text: str) -> bool:
    sentences = re.split(r"[.!?;]+", text)
    return any(
        any(contains_term(sentence, entity) for entity in AI_ENTITY_SIGNALS)
        and any(contains_term(sentence, relation) for relation in AGENT_RELATION_SIGNALS)
        for sentence in sentences
    )


def matched_area_keywords(area: str, words: list[str], text: str) -> list[str]:
    matches = [word for word in words if contains_term(text, word)]
    if area != "ai-agents":
        return matches[:5]

    explicit_agent_context = any(
        contains_term(text, signal) for signal in EXPLICIT_AI_AGENT_SIGNALS
    ) or has_ai_agent_relation(text)
    ai_entity_context = any(
        contains_term(text, entity) for entity in AI_ENTITY_SIGNALS
    )
    ambiguous_agent_context = any(
        word in AMBIGUOUS_AGENT_TERMS for word in matches
    )
    if ambiguous_agent_context and not explicit_agent_context:
        return []
    return [
        word
        for word in matches
        if word not in GENERIC_AGENT_CAPABILITY_TERMS
        or explicit_agent_context
        or ai_entity_context
    ][:5]


def score(item: Item) -> dict[str, Any]:
    text = " ".join([item.title, item.summary]).lower()
    matches = {
        area: area_matches
        for area, words in AREAS.items()
        if (area_matches := matched_area_keywords(area, words, text))
    }
    noise = [word for word in NOISE if contains_term(text, word)]
    relevance = min(5, len(matches) + (1 if any(a in matches for a in ["ai-agents", "models", "developer-tools", "data-platforms"]) else 0))
    leverage = min(5, len(matches.get("ai-agents", [])) // 2 + len(matches.get("developer-tools", [])) // 2 + len(matches.get("data-platforms", [])) // 2 + (1 if item.source in {"GitHub Blog", "OpenAI News", "Simon Willison"} else 0))
    novelty = 4 if any(contains_term(text, word) for word in ["launch", "release", "new", "announces", "introduces", "open source"]) else 2 + min(2, len(matches))
    urgency = 4 if any(contains_term(text, word) for word in ["security", "breach", "vulnerability", "lawsuit", "shutdown", "deprecated", "pricing"]) else 2 + (1 if relevance >= 4 else 0)
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
            parsed = parse_feed(source, http_get(url))
            if not parsed:
                errors[source] = "feed contained no valid items"
                continue
            for item in parsed:
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


def load_previous_snapshot(path: Path) -> Optional[dict[str, Any]]:
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("items"), list):
        raise ValueError("existing snapshot has an invalid shape")
    items = data["items"]
    total = data.get("total")
    if type(total) is not int or total < 0 or total != len(items):
        raise ValueError("existing snapshot has an invalid total")
    required_fields = ("id", "title", "url", "source")
    seen_ids: set[str] = set()
    seen_urls: set[str] = set()
    for record in items:
        if not isinstance(record, dict) or not all(
            isinstance(record.get(field), str) and record[field]
            for field in required_fields
        ):
            raise ValueError("existing snapshot contains an invalid item")
        normalized_url = record["url"].lower().split("?")[0]
        if record["id"] in seen_ids or normalized_url in seen_urls:
            raise ValueError("existing snapshot contains duplicate items")
        seen_ids.add(record["id"])
        seen_urls.add(normalized_url)
    return data


def rescore_snapshot_item(record: dict[str, Any]) -> Optional[dict[str, Any]]:
    title = record.get("title")
    url = record.get("url")
    source = record.get("source")
    if not all(isinstance(value, str) and value for value in (title, url, source)):
        return None
    rescored = dict(record)
    rescored.update(
        score(
            Item(
                title=title,
                url=url,
                source=source,
                published=str(record.get("published") or ""),
                summary=str(record.get("summary") or ""),
            )
        )
    )
    return rescored


def retain_failed_source_items(
    fresh_items: list[dict[str, Any]],
    previous: Optional[dict[str, Any]],
    failed_sources: set[str],
    limit: int,
) -> tuple[list[dict[str, Any]], list[str], int]:
    if not previous or not failed_sources:
        return fresh_items[:limit], [], 0

    fresh_keys = {
        str(item.get("url") or "").lower().split("?")[0]
        for item in fresh_items
        if item.get("url")
    }
    retained: list[dict[str, Any]] = []
    retained_keys: set[str] = set()
    for record in previous.get("items", []):
        if not isinstance(record, dict) or record.get("source") not in failed_sources:
            continue
        rescored = rescore_snapshot_item(record)
        if rescored is None:
            continue
        key = str(rescored["url"]).lower().split("?")[0]
        if key in fresh_keys or key in retained_keys:
            continue
        retained_keys.add(key)
        retained.append(rescored)

    retained.sort(
        key=lambda row: (row.get("priority") or 0, row.get("published") or ""),
        reverse=True,
    )
    retained = retained[:limit]
    remaining = max(0, limit - len(retained))
    required_fresh = min(
        len(fresh_items),
        math.ceil(limit * MIN_RETENTION_RATIO),
    )
    if remaining < required_fresh:
        raise ValueError(
            "failed-source retention leaves insufficient capacity for fresh items "
            f"({remaining}/{required_fresh})"
        )
    merged = retained + fresh_items[:remaining]
    merged.sort(
        key=lambda row: (row.get("priority") or 0, row.get("published") or ""),
        reverse=True,
    )
    retained_sources = sorted({str(item["source"]) for item in retained})
    return merged, retained_sources, len(retained)


def run(cmd: list[str], *, cwd: Path = SITE_REPO) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}
    return subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        timeout=120,
        env=env,
    )


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    serialized = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    json.loads(serialized)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=str(path.parent),
        text=True,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(serialized)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def publish_if_changed() -> PublishResult:
    try:
        branch = run(["git", "branch", "--show-current"])
        if branch.returncode != 0:
            return PublishResult("failed", f"git branch check failed: {branch.stdout.strip()}")
        if branch.stdout.strip() != PUBLISH_BRANCH:
            return PublishResult(
                "failed",
                f"publish requires branch {PUBLISH_BRANCH}; found {branch.stdout.strip() or 'detached HEAD'}",
            )

        worktree = run(["git", "status", "--porcelain"])
        if worktree.returncode != 0:
            return PublishResult("failed", f"git worktree check failed: {worktree.stdout.strip()}")
        unrelated = [
            line
            for line in worktree.stdout.splitlines()
            if line and line[3:] != PUBLISH_PATH
        ]
        if unrelated:
            return PublishResult(
                "failed",
                "publish requires a clean worktree outside "
                f"{PUBLISH_PATH}: {'; '.join(unrelated)}",
            )

        fetch = run([
            "git",
            "fetch",
            "--quiet",
            "--no-tags",
            PUBLISH_REMOTE,
            PUBLISH_BRANCH,
        ])
        if fetch.returncode != 0:
            return PublishResult("failed", f"git fetch failed: {fetch.stdout.strip()}")
        divergence = run([
            "git",
            "rev-list",
            "--left-right",
            "--count",
            f"HEAD...{PUBLISH_REMOTE}/{PUBLISH_BRANCH}",
        ])
        if divergence.returncode != 0:
            return PublishResult(
                "failed",
                f"git divergence check failed: {divergence.stdout.strip()}",
            )
        if divergence.stdout.split() != ["0", "0"]:
            return PublishResult(
                "failed",
                "publish requires local HEAD to match "
                f"{PUBLISH_REMOTE}/{PUBLISH_BRANCH}; divergence {divergence.stdout.strip()}",
            )

        status = run(["git", "status", "--porcelain", "--", PUBLISH_PATH])
        if status.returncode != 0:
            return PublishResult("failed", f"git status failed: {status.stdout.strip()}")
        if not status.stdout.strip():
            return PublishResult("unchanged")

        add = run(["git", "add", "--", PUBLISH_PATH])
        if add.returncode != 0:
            return PublishResult("failed", f"git add failed: {add.stdout.strip()}")

        commit = run([
            "git",
            "commit",
            "--only",
            "-m",
            "chore: update tech news snapshot",
            "--",
            PUBLISH_PATH,
        ])
        if commit.returncode != 0:
            return PublishResult("failed", f"git commit failed: {commit.stdout.strip()}")

        local_head = run(["git", "rev-parse", "HEAD"])
        if local_head.returncode != 0:
            return PublishResult(
                "failed",
                "git local SHA read-back failed after local commit: "
                + local_head.stdout.strip(),
            )
        local_sha = local_head.stdout.strip()
        push = run([
            "git",
            "push",
            "--porcelain",
            PUBLISH_REMOTE,
            f"HEAD:{PUBLISH_BRANCH}",
        ])
        if push.returncode != 0:
            return PublishResult(
                "failed",
                "git push failed after local commit: " + push.stdout.strip(),
            )
        remote_head = run([
            "git",
            "ls-remote",
            "--heads",
            PUBLISH_REMOTE,
            f"refs/heads/{PUBLISH_BRANCH}",
        ])
        if remote_head.returncode != 0:
            return PublishResult(
                "failed",
                "git remote SHA read-back failed after push: "
                + remote_head.stdout.strip(),
            )
        remote_sha = remote_head.stdout.split(maxsplit=1)[0] if remote_head.stdout.strip() else ""
        if remote_sha != local_sha:
            return PublishResult(
                "failed",
                "remote SHA mismatch after push: "
                f"local {local_sha or 'missing'}, remote {remote_sha or 'missing'}",
            )
        return PublishResult("published", (commit.stdout + push.stdout).strip())
    except (OSError, subprocess.SubprocessError) as exc:
        return PublishResult("failed", f"git command failed: {type(exc).__name__}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=90)
    parser.add_argument("--min-successful-sources", type=int, default=DEFAULT_MIN_SUCCESSFUL_SOURCES)
    parser.add_argument("--min-items", type=int, default=DEFAULT_MIN_ITEMS)
    parser.add_argument("--no-publish", action="store_true", help="write JSON only; do not commit/push")
    parser.add_argument("--quiet", action="store_true", help="only print errors")
    args = parser.parse_args()

    if args.limit < 1 or args.min_successful_sources < 1 or args.min_items < 1:
        print("collection gate failed: limit and minimums must be positive", file=sys.stderr)
        return 2

    try:
        previous = load_previous_snapshot(OUT)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"collection gate failed: previous snapshot invalid ({type(exc).__name__})", file=sys.stderr)
        return 2

    items, errors = collect(args.limit)
    successful_source_names = [source for source in FEEDS if source not in errors]
    successful_sources = len(successful_source_names)
    required_sources = min(args.min_successful_sources, len(FEEDS))
    required_items = min(args.min_items, args.limit)
    previous_total = int(previous.get("total", 0)) if previous else 0
    required_retention = (
        math.ceil(min(previous_total, args.limit) * MIN_RETENTION_RATIO)
        if previous_total
        else 0
    )
    if (
        successful_sources < required_sources
        or len(items) < required_items
        or len(items) < required_retention
    ):
        print(
            "collection gate failed: "
            f"successful sources {successful_sources}/{required_sources}; "
            f"items {len(items)}/{required_items}; "
            f"retention {len(items)}/{required_retention}",
            file=sys.stderr,
        )
        return 2
    try:
        items, retained_sources, retained_items = retain_failed_source_items(
            items,
            previous,
            set(errors),
            args.limit,
        )
    except ValueError as exc:
        print(f"collection gate failed: {exc}", file=sys.stderr)
        return 2
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    useful = sum(1 for i in items if i.get("action") in {"Read", "Watch"})
    payload = {
        "generatedAt": now,
        "source": "public RSS/Atom feeds",
        "total": len(items),
        "usefulOpen": useful,
        "sources": list(FEEDS.keys()),
        "successfulSources": successful_source_names,
        "failedSources": sorted(errors),
        "retainedSources": retained_sources,
        "retainedItems": retained_items,
        "errors": errors,
        "items": items,
    }
    try:
        atomic_write_json(OUT, payload)
    except (OSError, ValueError, TypeError) as exc:
        print(f"snapshot write failed: {type(exc).__name__}", file=sys.stderr)
        return 4

    if args.no_publish:
        if not args.quiet:
            print(f"exported {len(items)} tech-news items to {OUT} ({useful} useful)")
        return 0

    publish = publish_if_changed()
    if publish.state == "failed":
        print(publish.detail or "publish failed", file=sys.stderr)
        return 3
    if publish.state == "published" and not args.quiet:
        top = [i for i in items if i.get("action") in {"Read", "Watch"}][:5]
        print(f"## 🟣 Tech Newswatcher — {datetime.now().astimezone().strftime('%Y-%m-%d %H:%M %Z')}")
        print(f"Samenvatting: {useful} useful / {len(items)} items · pagina bijgewerkt")
        for idx, item in enumerate(top, 1):
            print(f"{idx}. {item['title']} — {item['source']} · {item['action']} · priority {item['priority']}")
            print(f"   {item['url']}")
        print("Pagina: https://viggomeesters.com/tech-news/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
