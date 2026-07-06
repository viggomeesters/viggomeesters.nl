#!/usr/bin/env python3
"""Export a public-safe Repo Trendwatcher snapshot for viggomeesters.com.

Reads the private vault ledger and writes a compact JSON projection used by
/trendwatch/. The output contains only public GitHub metadata and heuristic
scores, not private notes/tasks beyond high-level applied/status labels.
"""
from __future__ import annotations

import json
import os
from datetime import date, datetime
from pathlib import Path
from typing import Any

try:
    import yaml
except Exception as exc:  # pragma: no cover
    raise SystemExit(f"Missing PyYAML: {exc}")

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "trendwatch" / "data.json"


def resolve_ledger_path() -> Path:
    candidates: list[Path] = []
    env = os.environ.get("REPO_TRENDWATCH_LEDGER", "").strip()
    if env:
        candidates.append(Path(env).expanduser())
    for key in ("LIFEOS_JSONL_VAULT", "JSONL_VAULT_ROOT", "LIFEOS_VAULT"):
        env = os.environ.get(key, "").strip()
        if env:
            root = Path(env).expanduser()
            candidates.extend([root / "contracts" / "repo-inspiration-ledger.yaml", root / "system" / "contracts" / "repo-inspiration-ledger.yaml"])
    candidates.extend([
        Path("/mnt/c/Users/Viggo/Syncthing/jsonl-vault/default/contracts/repo-inspiration-ledger.yaml"),
        Path("/mnt/c/Users/viggo/Syncthing/jsonl-vault/default/contracts/repo-inspiration-ledger.yaml"),
    ])
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError("repo-inspiration-ledger.yaml not found in JSONL Vault contracts")


def clean(value: Any, fallback: str = "") -> str:
    if value is None:
        return fallback
    return " ".join(str(value).split()).strip() or fallback


def as_int(value: Any, fallback: int = 0) -> int:
    try:
        return int(value or fallback)
    except Exception:
        return fallback


def score(review: dict[str, Any], key: str) -> int:
    return max(0, min(5, as_int(review.get(key), 0)))


def is_done_entry(entry: dict[str, Any], status: str) -> bool:
    """Treat mined/adopted entries as done even if a later scout regressed status.

    The ledger's durable mining evidence is stronger than the triage status:
    once ideas were extracted or applied somewhere, the public dashboard should
    not keep surfacing the repo as an open Mine item.
    """
    if status in {"adopted", "mined"}:
        return True
    return bool(entry.get("ideas_extracted") or entry.get("applied_in"))


def action_for(recommendation: str, status: str, done: bool = False) -> tuple[str, str]:
    if done:
        return "Done", "Already mined/adopted"
    if recommendation == "mine_now":
        return "Mine", "Worth a focused pattern-mining pass"
    if recommendation == "watch":
        return "Watch", "Interesting; wait or mine when it matches a current project"
    if recommendation == "reject":
        return "Skip", "Low value or risk/noise markers"
    return "Ledger", "Captured for provenance only"


def priority_for(review: dict[str, Any], status: str, done: bool = False) -> int:
    if done:
        return 55
    rec = clean(review.get("recommendation"), "ledger_only")
    base = {"mine_now": 95, "watch": 72, "ledger_only": 38, "reject": 8}.get(rec, 30)
    return max(0, min(100, base + score(review, "fit_score") * 2 + score(review, "leverage_score") * 2 - score(review, "risk_score") * 5))


def sort_date(entry: dict[str, Any]) -> str:
    return clean(entry.get("first_seen") or entry.get("last_seen") or "0000-00-00")


def main() -> int:
    ledger_path = resolve_ledger_path()
    ledger = yaml.safe_load(ledger_path.read_text(encoding="utf-8")) or {}
    entries = ledger.get("entries") or []
    if not isinstance(entries, list):
        raise ValueError("ledger entries must be a list")

    public_items: list[dict[str, Any]] = []
    recommendations: dict[str, int] = {}
    useful = 0
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        review = entry.get("review") if isinstance(entry.get("review"), dict) else {}
        recommendation = clean(review.get("recommendation"), "ledger_only")
        status = clean(entry.get("status"), "inbox")
        done = is_done_entry(entry, status)
        action, action_detail = action_for(recommendation, status, done)
        priority = priority_for(review, status, done)
        if recommendation in {"mine_now", "watch"} and not done:
            useful += 1
        recommendations[recommendation] = recommendations.get(recommendation, 0) + 1
        areas = entry.get("mined_for") or review.get("matched_stack_areas") or []
        if not isinstance(areas, list):
            areas = [clean(areas)] if areas else []
        tags = entry.get("tags") or []
        if not isinstance(tags, list):
            tags = []
        repo = clean(entry.get("repo"))
        if not repo:
            continue
        public_items.append(
            {
                "id": clean(entry.get("id"), repo.lower().replace("/", "-")),
                "repo": repo,
                "url": clean(entry.get("url"), f"https://github.com/{repo}"),
                "firstSeen": clean(entry.get("first_seen")),
                "lastSeen": clean(entry.get("last_seen"), clean(entry.get("first_seen"))),
                "seenCount": as_int(entry.get("seen_count"), 1),
                "status": status,
                "recommendation": recommendation,
                "action": action,
                "actionDetail": action_detail,
                "priority": priority,
                "why": clean(entry.get("why_interesting") or review.get("rationale"), "Captured by the repo trendwatcher."),
                "areas": [clean(area) for area in areas if clean(area)][:6],
                "tags": [clean(tag) for tag in tags if clean(tag)][:10],
                "language": clean(entry.get("language")),
                "stars": as_int(entry.get("stars"), 0),
                "forks": as_int(entry.get("forks"), 0),
                "license": clean(entry.get("license"), "unknown"),
                "scores": {
                    "fit": score(review, "fit_score"),
                    "leverage": score(review, "leverage_score"),
                    "novelty": score(review, "novelty_score"),
                    "maturity": score(review, "maturity_score"),
                    "risk": score(review, "risk_score"),
                },
            }
        )

    public_items.sort(key=lambda item: (item.get("firstSeen") or "", item.get("priority") or 0, item.get("repo") or ""), reverse=True)
    payload = {
        "generatedAt": datetime.now().astimezone().isoformat(timespec="seconds"),
        "ledgerUpdated": clean(ledger.get("updated"), date.today().isoformat()),
        "source": "contracts/repo-inspiration-ledger.yaml",
        "total": len(public_items),
        "usefulOpen": useful,
        "recommendations": recommendations,
        "items": public_items,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"exported {len(public_items)} trendwatch items to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
