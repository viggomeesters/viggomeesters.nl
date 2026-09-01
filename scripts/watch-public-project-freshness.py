#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path
from typing import NamedTuple
from urllib.parse import urlsplit, urlunsplit

DEFAULT_INVENTORY = "https://viggomeesters.com/data/public-projects.json"
DEFAULT_STATE_FILE = Path.home() / ".hermes" / "state" / "viggomeesters-project-freshness-watchdog.json"
EXPIRY_WARNING_DAYS = 14
MAX_FINDINGS = 20
SECRET_RE = re.compile(
    r"(?i)(github_pat_[a-z0-9_]+|gh[pousr]_[a-z0-9_]+|(?:token|secret|password)\s*[=:]\s*\S+)"
)

GRAPHQL_QUERY = """
query($login: String!) {
  repositoryOwner(login: $login) {
    repositories(
      first: 100
      privacy: PUBLIC
      ownerAffiliations: OWNER
      orderBy: {field: NAME, direction: ASC}
    ) {
      nodes {
        name
        url
        description
        homepageUrl
        pushedAt
        isArchived
        isFork
        parent { nameWithOwner }
        defaultBranchRef { target { ... on Commit { oid } } }
        latestRelease { tagName publishedAt url }
      }
      pageInfo { hasNextPage endCursor }
    }
  }
}
""".strip()


class WatchdogError(RuntimeError):
    pass


class Finding(NamedTuple):
    severity: str
    repo: str
    field: str
    old: object
    new: object
    action: str


def safe_value(value: object, *, limit: int = 240) -> str:
    if value is None:
        return "—"
    if isinstance(value, bool):
        text = "ja" if value else "nee"
    else:
        text = str(value).replace("\n", " ").replace("\r", " ").strip()
    text = SECRET_RE.sub("[REDACTED]", text)
    if len(text) > limit:
        text = text[: limit - 1] + "…"
    return text or "—"


def canonical_url(value: object) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    parts = urlsplit(value.strip())
    path = parts.path.rstrip("/")
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path, parts.query, ""))


def load_json(location: str) -> dict[str, object]:
    if location.startswith(("https://", "http://")):
        request = urllib.request.Request(location, headers={"User-Agent": "viggomeesters-freshness-watchdog/1"})
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                raw = response.read()
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise WatchdogError(f"kan JSON-bron niet laden: {location}: {exc}") from exc
    else:
        try:
            raw = Path(location).read_bytes()
        except OSError as exc:
            raise WatchdogError(f"kan JSON-bestand niet laden: {location}: {exc}") from exc
    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise WatchdogError(f"ongeldige JSON in {location}: {exc}") from exc
    if not isinstance(payload, dict):
        raise WatchdogError(f"JSON-bron is geen object: {location}")
    return payload


def normalize_graphql_snapshot(payload: dict[str, object]) -> dict[str, object]:
    errors = payload.get("errors")
    if errors:
        raise WatchdogError(f"GitHub GraphQL gaf fouten: {safe_value(errors)}")
    try:
        connection = payload["data"]["repositoryOwner"]["repositories"]  # type: ignore[index]
        nodes = connection["nodes"]
        page_info = connection["pageInfo"]
    except (KeyError, TypeError) as exc:
        raise WatchdogError("GitHub GraphQL-respons mist repositorydata") from exc
    if not isinstance(connection, dict) or not isinstance(nodes, list) or not isinstance(page_info, dict):
        raise WatchdogError("GitHub GraphQL-respons bevat ongeldige repositorydata")
    has_next_page = page_info.get("hasNextPage")
    if not isinstance(has_next_page, bool):
        raise WatchdogError("GitHub GraphQL pageInfo.hasNextPage moet een boolean zijn")
    if has_next_page:
        raise WatchdogError("meer dan 100 publieke repositories; pagination moet eerst expliciet worden ondersteund")
    repositories: list[dict[str, object]] = []
    for node in nodes:
        if not isinstance(node, dict):
            raise WatchdogError("GitHub GraphQL bevat een ongeldige repositorynode")
        default_branch = node.get("defaultBranchRef") or {}
        target = default_branch.get("target") if isinstance(default_branch, dict) else {}
        release = node.get("latestRelease") or {}
        parent = node.get("parent") or {}
        repositories.append(
            {
                "name": node.get("name"),
                "url": node.get("url"),
                "description": node.get("description"),
                "homepage_url": node.get("homepageUrl"),
                "pushed_at": node.get("pushedAt"),
                "head_oid": target.get("oid") if isinstance(target, dict) else None,
                "is_archived": node.get("isArchived"),
                "is_fork": node.get("isFork"),
                "parent": parent.get("nameWithOwner") if isinstance(parent, dict) else None,
                "latest_release_tag": release.get("tagName") if isinstance(release, dict) else None,
                "latest_release_published_at": release.get("publishedAt") if isinstance(release, dict) else None,
                "latest_release_url": release.get("url") if isinstance(release, dict) else None,
            }
        )
    return {"repositories": repositories}


def fetch_github_snapshot(owner: str) -> dict[str, object]:
    try:
        completed = subprocess.run(
            ["gh", "api", "graphql", "-f", f"query={GRAPHQL_QUERY}", "-F", f"login={owner}"],
            text=True,
            capture_output=True,
            check=False,
            timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise WatchdogError(f"GitHub-query kon niet starten: {exc}") from exc
    if completed.returncode != 0:
        detail = safe_value(completed.stderr or completed.stdout)
        raise WatchdogError(f"GitHub-query faalde: {detail}")
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise WatchdogError("GitHub-query gaf geen geldige JSON") from exc
    if not isinstance(payload, dict):
        raise WatchdogError("GitHub-query gaf geen JSON-object")
    return normalize_graphql_snapshot(payload)


def _check_homepage(url: str, timeout: float) -> tuple[str, dict[str, object]]:
    try:
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "viggomeesters-freshness-watchdog/1", "Range": "bytes=0-0"},
        )
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return url, {"status": response.status, "final_url": response.geturl()}
    except urllib.error.HTTPError as exc:
        return url, {"status": exc.code, "final_url": exc.geturl()}
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
        return url, {"status": "error", "final_url": None, "error": safe_value(exc)}


def fetch_homepage_results(urls: list[str], *, timeout: float = 12.0, workers: int = 8) -> dict[str, dict[str, object]]:
    unique = sorted(set(urls))
    results: dict[str, dict[str, object]] = {}
    with ThreadPoolExecutor(max_workers=min(workers, max(1, len(unique)))) as executor:
        futures = [executor.submit(_check_homepage, url, timeout) for url in unique]
        for future in as_completed(futures):
            url, result = future.result()
            results[url] = result
    return results


def _add_change(
    findings: list[Finding],
    repo: str,
    field: str,
    old: object,
    new: object,
    action: str,
    *,
    severity: str = "warning",
    urls: bool = False,
    optional_text: bool = False,
) -> None:
    if urls:
        equal = canonical_url(old) == canonical_url(new)
    elif optional_text:
        equal = (old or None) == (new or None)
    else:
        equal = old == new
    if not equal:
        findings.append(Finding(severity, repo, field, old, new, action))


def compare_inventory(
    inventory: dict[str, object],
    snapshot: dict[str, object],
    *,
    today: date | None = None,
    homepage_results: dict[str, dict[str, object]] | None = None,
    expiry_warning_days: int = EXPIRY_WARNING_DAYS,
) -> list[Finding]:
    today = today or date.today()
    active = inventory.get("repositories")
    excluded = inventory.get("excluded_repositories")
    live = snapshot.get("repositories")
    audit = inventory.get("freshness_audit")
    if not isinstance(active, list) or not isinstance(excluded, list) or not isinstance(live, list):
        raise WatchdogError("inventory of snapshot mist een repositorylijst")
    if not isinstance(audit, dict):
        raise WatchdogError("inventory mist freshness_audit")

    expected_active = {item.get("name"): item for item in active if isinstance(item, dict) and item.get("name")}
    expected_excluded = {item.get("name"): item for item in excluded if isinstance(item, dict) and item.get("name")}
    current = {item.get("name"): item for item in live if isinstance(item, dict) and item.get("name")}
    if len(current) != len(live):
        raise WatchdogError("snapshot bevat ongeldige of dubbele repositorynamen")

    self_hosted_repo: str | None = None
    ignored_self_fields: set[str] = set()
    watchdog_config = inventory.get("freshness_watchdog")
    if watchdog_config is not None:
        if not isinstance(watchdog_config, dict):
            raise WatchdogError("freshness_watchdog moet een object zijn")
        candidate = watchdog_config.get("self_hosted_inventory_repository")
        ignored = watchdog_config.get("ignored_self_referential_fields")
        reason = watchdog_config.get("reason")
        if not isinstance(candidate, str) or candidate not in expected_active:
            raise WatchdogError("self-hosted inventory repository is niet actief geclassificeerd")
        if not isinstance(ignored, list) or set(ignored) != {"pushed_at", "head_oid"}:
            raise WatchdogError("self-hosted uitzondering mag uitsluitend pushed_at en head_oid negeren")
        if not isinstance(reason, str) or not reason.strip():
            raise WatchdogError("self-hosted uitzondering vereist een expliciete reden")
        self_hosted_repo = candidate
        ignored_self_fields = set(ignored)

    findings: list[Finding] = []
    expected_names = set(expected_active) | set(expected_excluded)
    for name in sorted(expected_names - set(current)):
        findings.append(
            Finding(
                "critical",
                str(name),
                "repository",
                "publiek en geclassificeerd",
                "ontbreekt publiek",
                "Controleer rename, verwijdering of visibility en werk de classificatie bewust bij.",
            )
        )
    for name in sorted(set(current) - expected_names):
        findings.append(
            Finding(
                "critical",
                str(name),
                "repository",
                "niet in audit",
                "publiek maar niet geclassificeerd",
                "Classificeer als sitevermelding, bewuste uitsluiting, archief, fork of historisch item.",
            )
        )

    for name in sorted(set(expected_active) & set(current)):
        expected = expected_active[name]
        actual = current[name]
        freshness = expected.get("freshness")
        if not isinstance(freshness, dict):
            raise WatchdogError(f"{name}: inventory mist freshness-evidence")
        action = "Herbeoordeel README, publieke sitecopy en gedateerd auditbewijs."
        _add_change(findings, str(name), "is_archived", False, actual.get("is_archived"), action, severity="critical")
        _add_change(findings, str(name), "is_fork", False, actual.get("is_fork"), action, severity="critical")
        if name != self_hosted_repo or "pushed_at" not in ignored_self_fields:
            _add_change(findings, str(name), "pushed_at", expected.get("pushed_at"), actual.get("pushed_at"), action)
        if name != self_hosted_repo or "head_oid" not in ignored_self_fields:
            _add_change(findings, str(name), "head_oid", freshness.get("head_oid"), actual.get("head_oid"), action)
        _add_change(
            findings,
            str(name),
            "description",
            expected.get("description"),
            actual.get("description"),
            action,
            optional_text=True,
        )
        _add_change(
            findings,
            str(name),
            "homepage_url",
            freshness.get("homepage_url"),
            actual.get("homepage_url"),
            action,
            urls=True,
        )
        _add_change(
            findings,
            str(name),
            "latest_release_tag",
            freshness.get("latest_release_tag"),
            actual.get("latest_release_tag"),
            action,
        )
        _add_change(
            findings,
            str(name),
            "latest_release_published_at",
            freshness.get("latest_release_published_at"),
            actual.get("latest_release_published_at"),
            action,
        )
        _add_change(
            findings,
            str(name),
            "latest_release_url",
            freshness.get("latest_release_url"),
            actual.get("latest_release_url"),
            action,
            urls=True,
        )

    for name in sorted(set(expected_excluded) & set(current)):
        expected = expected_excluded[name]
        actual = current[name]
        action = "Herbeoordeel de expliciete uitsluitingsclassificatie en publieke vermeldingen."
        for field in ("pushed_at", "head_oid", "is_archived", "is_fork", "parent"):
            _add_change(
                findings,
                str(name),
                field,
                expected.get(field),
                actual.get(field),
                action,
                severity="critical" if field in {"is_archived", "is_fork", "parent"} else "warning",
            )

    if homepage_results is not None:
        for expected in expected_active.values():
            freshness = expected.get("freshness")
            if not isinstance(freshness, dict):
                continue
            homepage = freshness.get("homepage_url")
            if not isinstance(homepage, str) or not homepage:
                continue
            result = homepage_results.get(homepage)
            if result is None:
                findings.append(
                    Finding(
                        "critical",
                        str(expected.get("name")),
                        "homepage",
                        homepage,
                        "niet gecontroleerd",
                        "Herstel de homepagecheck; een ontbrekende meting mag niet stil passeren.",
                    )
                )
                continue
            status = result.get("status")
            final_url = result.get("final_url")
            if not isinstance(status, int) or not 200 <= status < 400:
                findings.append(
                    Finding(
                        "critical",
                        str(expected.get("name")),
                        "homepage",
                        f"{homepage} (eerder succesvol)",
                        f"status {safe_value(status)}; {safe_value(final_url or result.get('error'))}",
                        "Controleer deployment, redirect en de publieke siteverwijzing.",
                    )
                )
            reviewed_final = freshness.get("homepage_final_url")
            if reviewed_final and isinstance(final_url, str) and canonical_url(reviewed_final) != canonical_url(final_url):
                findings.append(
                    Finding(
                        "warning",
                        str(expected.get("name")),
                        "homepage_final_url",
                        reviewed_final,
                        final_url,
                        "Controleer of de redirect/canonical bewust is en vernieuw het auditbewijs.",
                    )
                )

    expires_raw = audit.get("expires_on")
    try:
        expires = date.fromisoformat(str(expires_raw))
    except ValueError as exc:
        raise WatchdogError(f"ongeldige auditvervaldatum: {safe_value(expires_raw)}") from exc
    days_left = (expires - today).days
    if days_left < 0:
        findings.append(
            Finding(
                "critical",
                "audit",
                "audit_expiry",
                expires.isoformat(),
                f"{abs(days_left)} dag(en) verlopen",
                "Voer de volledige GitHub/README/release/homepage-review opnieuw uit.",
            )
        )
    elif days_left <= expiry_warning_days:
        findings.append(
            Finding(
                "warning",
                "audit",
                "audit_expiry",
                expires.isoformat(),
                f"nog {days_left} dag(en) geldig",
                "Plan de volgende volledige freshnessaudit vóór de vervaldatum.",
            )
        )
    return findings


def render_alert(findings: list[Finding], *, today: date | None = None, max_findings: int = MAX_FINDINGS) -> str:
    if not findings:
        return ""
    today = today or date.today()
    severity_order = {"critical": 0, "warning": 1, "info": 2}
    ordered = sorted(findings, key=lambda item: (severity_order.get(item.severity, 9), item.repo, item.field))
    bounded_limit = min(MAX_FINDINGS, max(1, max_findings))
    shown = ordered[:bounded_limit]
    lines = [f"⚠️ Projectversheid vraagt review — {today.isoformat()}", ""]
    for finding in shown:
        label = "KRITIEK" if finding.severity == "critical" else "LET OP"
        lines.extend(
            [
                f"- {label} · {safe_value(finding.repo)} · {safe_value(finding.field)}",
                f"  Oud: {safe_value(finding.old)}",
                f"  Nieuw: {safe_value(finding.new)}",
                f"  Actie: {safe_value(finding.action)}",
            ]
        )
    remaining = len(ordered) - len(shown)
    if remaining:
        lines.extend(["", f"+ {remaining} aanvullende bevinding(en); voer de lokale watchdog handmatig uit voor de volledige lijst."])
    lines.extend(["", "Geen automatische wijzigingen uitgevoerd."])
    return "\n".join(lines) + "\n"


def stateful_output(findings: list[Finding], alert: str, state_file: Path | None) -> str:
    if state_file is None:
        return alert
    if not findings:
        try:
            state_file.unlink(missing_ok=True)
        except OSError as exc:
            raise WatchdogError(f"kan opgeloste watchdogstate niet wissen: {exc}") from exc
        return ""
    serialized = json.dumps([item._asdict() for item in findings], ensure_ascii=False, sort_keys=True, default=str)
    fingerprint = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    previous = None
    try:
        if state_file.is_file():
            previous_payload = json.loads(state_file.read_text(encoding="utf-8"))
            if isinstance(previous_payload, dict):
                previous = previous_payload.get("fingerprint")
    except (OSError, json.JSONDecodeError):
        previous = None
    state_file.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps({"schema": "viggomeesters.project-freshness-watchdog-state.v1", "fingerprint": fingerprint}, indent=2)
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=state_file.parent, delete=False) as handle:
            handle.write(payload + "\n")
            temporary = Path(handle.name)
        os.chmod(temporary, 0o600)
        temporary.replace(state_file)
    except OSError as exc:
        raise WatchdogError(f"kan watchdogstate niet opslaan: {exc}") from exc
    return "" if previous == fingerprint else alert


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Silent public-project freshness watchdog")
    parser.add_argument("--inventory", default=DEFAULT_INVENTORY, help="Local path or HTTP(S) URL to public-projects.json")
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--live", action="store_true", help="Fetch current GitHub metadata (default)")
    source.add_argument("--snapshot", help="Use a local JSON snapshot instead of GitHub")
    parser.add_argument("--skip-homepages", action="store_true", help="Skip public homepage HTTP checks")
    parser.add_argument("--today", help="Override current date for deterministic verification")
    parser.add_argument("--expiry-warning-days", type=int, default=EXPIRY_WARNING_DAYS)
    parser.add_argument("--state-file", type=Path, default=DEFAULT_STATE_FILE)
    parser.add_argument("--no-state", action="store_true", help="Always print current drift; do not deduplicate")
    parser.add_argument("--max-findings", type=int, default=MAX_FINDINGS)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        today = date.fromisoformat(args.today) if args.today else date.today()
        inventory = load_json(args.inventory)
        if args.snapshot:
            raw_snapshot = load_json(args.snapshot)
            snapshot = normalize_graphql_snapshot(raw_snapshot) if "data" in raw_snapshot else raw_snapshot
        else:
            owner = inventory.get("account")
            if not isinstance(owner, str) or not owner:
                raise WatchdogError("inventory mist GitHub-account")
            snapshot = fetch_github_snapshot(owner)
        homepage_results = None
        if not args.skip_homepages:
            urls = []
            for item in inventory.get("repositories", []):
                if not isinstance(item, dict):
                    continue
                freshness = item.get("freshness")
                homepage = freshness.get("homepage_url") if isinstance(freshness, dict) else None
                if isinstance(homepage, str) and homepage:
                    urls.append(homepage)
            homepage_results = fetch_homepage_results(urls)
        findings = compare_inventory(
            inventory,
            snapshot,
            today=today,
            homepage_results=homepage_results,
            expiry_warning_days=args.expiry_warning_days,
        )
        alert = render_alert(findings, today=today, max_findings=args.max_findings)
        state_file = None if args.no_state else args.state_file.expanduser()
        output = stateful_output(findings, alert, state_file)
        if output:
            print(output, end="")
        return 0
    except WatchdogError as exc:
        print(f"Projectversheidswatchdog faalde: {safe_value(exc)}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
