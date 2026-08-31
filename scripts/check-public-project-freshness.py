#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "public-projects.json"
REPORTS = ROOT / "reports" / "project-freshness"
REVIEW_WINDOW_DAYS = 90
ALLOWED_OUTCOMES = {"current", "corrected"}
ALLOWED_SITE_SCOPES = {"timeline_only", "timeline_and_variants", "detail_page", "portfolio_hub"}
ALLOWED_EXCLUSION_CLASSIFICATIONS = {
    "archived_fork",
    "active_fork",
    "infrastructure_fork",
    "archived_source_successor",
}
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def parse_day(value: object, field: str, errors: list[str]) -> date | None:
    if not isinstance(value, str):
        errors.append(f"{field}: expected ISO date string")
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        errors.append(f"{field}: invalid ISO date {value!r}")
        return None


def valid_timestamp(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def derived_counts(payload: dict[str, object]) -> dict[str, int]:
    repositories = payload.get("repositories")
    if not isinstance(repositories, list):
        return {}
    current = corrected = timeline_only = timeline_and_variants = detail_page = portfolio_hub = 0
    published_releases = homepage_urls_checked = 0
    for item in repositories:
        if not isinstance(item, dict):
            continue
        freshness = item.get("freshness")
        if not isinstance(freshness, dict):
            continue
        outcome = freshness.get("outcome")
        if outcome == "current":
            current += 1
        elif outcome == "corrected":
            corrected += 1
        site_scope = freshness.get("site_scope")
        if site_scope == "timeline_only":
            timeline_only += 1
        elif site_scope == "timeline_and_variants":
            timeline_and_variants += 1
        elif site_scope == "detail_page":
            detail_page += 1
        elif site_scope == "portfolio_hub":
            portfolio_hub += 1
        if freshness.get("latest_release_tag"):
            published_releases += 1
        if freshness.get("homepage_url"):
            homepage_urls_checked += 1
    return {
        "repositories_reviewed": len(repositories),
        "current": current,
        "corrected": corrected,
        "timeline_only": timeline_only,
        "timeline_and_variants": timeline_and_variants,
        "detail_page": detail_page,
        "portfolio_hub": portfolio_hub,
        "published_releases": published_releases,
        "homepage_urls_checked": homepage_urls_checked,
        "excluded_public_mentions": len(payload.get("excluded_repositories", []))
        if isinstance(payload.get("excluded_repositories"), list)
        else 0,
        "renamed_aliases_corrected": len(payload.get("renamed_aliases", []))
        if isinstance(payload.get("renamed_aliases"), list)
        else 0,
    }


def validate_payload(payload: dict[str, object], today: date | None = None) -> list[str]:
    today = today or date.today()
    errors: list[str] = []
    audit = payload.get("freshness_audit")
    if not isinstance(audit, dict):
        return ["freshness_audit: missing object"]

    if audit.get("policy_days") != REVIEW_WINDOW_DAYS:
        errors.append(f"freshness_audit.policy_days must be {REVIEW_WINDOW_DAYS}")

    reviewed_on_raw = audit.get("reviewed_on")
    reviewed_on = parse_day(reviewed_on_raw, "freshness_audit.reviewed_on", errors)
    expires_on = parse_day(audit.get("expires_on"), "freshness_audit.expires_on", errors)
    if reviewed_on and expires_on:
        expected_expiry = reviewed_on + timedelta(days=REVIEW_WINDOW_DAYS)
        if expires_on != expected_expiry:
            errors.append(
                f"freshness_audit.expires_on: expected {expected_expiry.isoformat()} for {REVIEW_WINDOW_DAYS}-day policy"
            )
        if today > expires_on:
            errors.append(
                f"freshness audit expired on {expires_on.isoformat()}; rerun the GitHub/README/live-link review"
            )

    if payload.get("snapshot_date") != reviewed_on_raw:
        errors.append("snapshot_date must match freshness_audit.reviewed_on")

    repositories = payload.get("repositories")
    if not isinstance(repositories, list):
        return errors + ["repositories: expected list"]

    names: set[str] = set()
    for index, item in enumerate(repositories):
        if not isinstance(item, dict):
            errors.append(f"repositories[{index}]: expected object")
            continue
        name = item.get("name")
        if not isinstance(name, str) or not name:
            errors.append(f"repositories[{index}].name: missing")
            continue
        if name in names:
            errors.append(f"{name}: duplicate repository")
        names.add(name)

        freshness = item.get("freshness")
        if not isinstance(freshness, dict):
            errors.append(f"{name}: missing freshness evidence")
            continue
        if reviewed_on and freshness.get("reviewed_on") != reviewed_on.isoformat():
            errors.append(f"{name}: freshness.reviewed_on does not match audit date")
        if freshness.get("observed_pushed_at") != item.get("pushed_at"):
            errors.append(f"{name}: new push metadata invalidates the previous review")
        if freshness.get("observed_description") != item.get("description"):
            errors.append(f"{name}: changed repository description invalidates the previous review")
        head_oid = freshness.get("head_oid")
        if not isinstance(head_oid, str) or not SHA_RE.fullmatch(head_oid):
            errors.append(f"{name}: invalid or missing reviewed head_oid")

        outcome = freshness.get("outcome")
        if outcome not in ALLOWED_OUTCOMES:
            errors.append(f"{name}: invalid freshness outcome {outcome!r}")
        site_scope = freshness.get("site_scope")
        if site_scope not in ALLOWED_SITE_SCOPES:
            errors.append(f"{name}: invalid site_scope {site_scope!r}")

        sources = freshness.get("sources")
        expected_repo = item.get("url")
        if not isinstance(sources, list) or expected_repo not in sources:
            errors.append(f"{name}: sources must include the canonical repository URL")
        readme_url = f"{expected_repo}#readme"
        if isinstance(sources, list) and readme_url not in sources:
            errors.append(f"{name}: sources must include README evidence")

        homepage_url = freshness.get("homepage_url")
        homepage_status = freshness.get("homepage_status")
        homepage_final_url = freshness.get("homepage_final_url")
        if homepage_url:
            if not isinstance(homepage_status, int) or not 200 <= homepage_status < 400:
                errors.append(f"{name}: homepage evidence is not a successful HTTP status")
            if not isinstance(homepage_final_url, str) or not homepage_final_url.startswith(("http://", "https://")):
                errors.append(f"{name}: homepage_final_url must record the successful destination")
            if isinstance(sources, list) and homepage_url not in sources:
                errors.append(f"{name}: sources must include homepage evidence")
        elif homepage_status is not None or homepage_final_url is not None:
            errors.append(f"{name}: homepage status/final URL must be null when homepage_url is null")

        release_tag = freshness.get("latest_release_tag")
        release_url = freshness.get("latest_release_url")
        release_published_at = freshness.get("latest_release_published_at")
        if bool(release_tag) != bool(release_url):
            errors.append(f"{name}: latest release tag/url must both be present or both be null")
        if release_tag:
            if not valid_timestamp(release_published_at):
                errors.append(f"{name}: latest_release_published_at must be a valid timestamp")
            if isinstance(sources, list) and release_url not in sources:
                errors.append(f"{name}: sources must include latest release URL")
        elif release_published_at is not None:
            errors.append(f"{name}: release timestamp must be null when no latest release exists")

    exclusions = payload.get("excluded_repositories")
    if not isinstance(exclusions, list):
        errors.append("excluded_repositories: expected list")
        exclusions = []
    exclusion_names: set[str] = set()
    for index, item in enumerate(exclusions):
        if not isinstance(item, dict):
            errors.append(f"excluded_repositories[{index}]: expected object")
            continue
        name = item.get("name")
        if not isinstance(name, str) or not name:
            errors.append(f"excluded_repositories[{index}].name: missing")
            continue
        if name in names or name in exclusion_names:
            errors.append(f"{name}: duplicate active/excluded classification")
        exclusion_names.add(name)
        if reviewed_on and item.get("reviewed_on") != reviewed_on.isoformat():
            errors.append(f"{name}: excluded review date does not match audit date")
        if item.get("classification") not in ALLOWED_EXCLUSION_CLASSIFICATIONS:
            errors.append(f"{name}: invalid exclusion classification {item.get('classification')!r}")
        if not isinstance(item.get("url"), str) or not item["url"].startswith("https://github.com/viggomeesters/"):
            errors.append(f"{name}: invalid excluded repository URL")
        if not valid_timestamp(item.get("pushed_at")):
            errors.append(f"{name}: excluded pushed_at must be a valid timestamp")
        if not isinstance(item.get("head_oid"), str) or not SHA_RE.fullmatch(item["head_oid"]):
            errors.append(f"{name}: invalid excluded head_oid")
        classification = item.get("classification")
        archived = item.get("is_archived")
        fork = item.get("is_fork")
        parent = item.get("parent")
        expected_state = {
            "archived_fork": (True, True),
            "active_fork": (False, True),
            "infrastructure_fork": (False, True),
            "archived_source_successor": (True, False),
        }.get(classification)
        if expected_state and (archived, fork) != expected_state:
            errors.append(f"{name}: archive/fork state does not match {classification}")
        if fork and not isinstance(parent, str):
            errors.append(f"{name}: fork classification requires parent repository evidence")
        if not fork and parent is not None:
            errors.append(f"{name}: non-fork exclusion must not declare a parent")
        if not isinstance(item.get("site_evidence"), list) or not item["site_evidence"]:
            errors.append(f"{name}: excluded repository requires site_evidence")

    aliases = payload.get("renamed_aliases")
    if not isinstance(aliases, list):
        errors.append("renamed_aliases: expected list")
        aliases = []
    alias_names: set[str] = set()
    for index, alias in enumerate(aliases):
        if not isinstance(alias, dict):
            errors.append(f"renamed_aliases[{index}]: expected object")
            continue
        name = alias.get("name")
        if not isinstance(name, str) or not name:
            errors.append(f"renamed_aliases[{index}].name: missing")
            continue
        if name in alias_names:
            errors.append(f"{name}: duplicate renamed alias")
        alias_names.add(name)
        if reviewed_on and alias.get("reviewed_on") != reviewed_on.isoformat():
            errors.append(f"{name}: alias review date does not match audit date")
        status = alias.get("http_status")
        if not isinstance(status, int) or not 200 <= status < 400:
            errors.append(f"{name}: alias redirect does not have a successful HTTP status")
        canonical = alias.get("canonical_repository")
        if canonical not in names:
            errors.append(f"{name}: canonical repository {canonical!r} is not active")
        if not isinstance(alias.get("previous_url"), str) or not alias["previous_url"].startswith("https://github.com/viggomeesters/"):
            errors.append(f"{name}: invalid previous alias URL")
        if not isinstance(alias.get("canonical_url"), str) or alias["canonical_url"] != f"https://github.com/viggomeesters/{canonical}":
            errors.append(f"{name}: canonical alias URL does not match repository name")
        if not isinstance(alias.get("corrected_files"), list) or not alias["corrected_files"]:
            errors.append(f"{name}: alias requires corrected_files evidence")

    summary = audit.get("summary")
    expected = derived_counts(payload)
    if not isinstance(summary, dict):
        errors.append("freshness_audit.summary: missing object")
    else:
        for key, value in expected.items():
            if summary.get(key) != value:
                errors.append(f"freshness_audit.summary.{key}: expected {value}, got {summary.get(key)!r}")

    return errors


def validate_report(payload: dict[str, object], report: dict[str, object]) -> list[str]:
    errors: list[str] = []
    audit = payload.get("freshness_audit")
    if not isinstance(audit, dict):
        return ["cannot validate report without freshness_audit"]
    expected = derived_counts(payload)
    if report.get("schema") != "viggomeesters.project-freshness-audit.v1":
        errors.append("dated report has an unexpected schema")
    if report.get("reviewed_on") != audit.get("reviewed_on"):
        errors.append("dated report review date does not match data/public-projects.json")
    if report.get("expires_on") != audit.get("expires_on"):
        errors.append("dated report expiry does not match data/public-projects.json")
    if report.get("repositories_reviewed") != expected.get("repositories_reviewed"):
        errors.append("dated report repository count does not match inventory")

    evidence = report.get("evidence")
    if not isinstance(evidence, dict):
        errors.append("dated report evidence must be an object")
    else:
        report_expected = {
            "active_public_source_repositories": expected.get("repositories_reviewed"),
            "published_releases": expected.get("published_releases"),
            "homepage_urls_checked": expected.get("homepage_urls_checked"),
            "homepage_http_successes": expected.get("homepage_urls_checked"),
            "active_repository_cards_corrected": expected.get("corrected"),
            "excluded_public_repository_mentions_classified": expected.get("excluded_public_mentions"),
            "renamed_aliases_corrected": expected.get("renamed_aliases_corrected"),
            "design_variant_canonical_links_checked": sum(
                len(alias.get("corrected_files", []))
                for alias in payload.get("renamed_aliases", [])
                if isinstance(alias, dict)
            ),
        }
        for key, value in report_expected.items():
            if evidence.get(key) != value:
                errors.append(f"dated report evidence.{key}: expected {value}, got {evidence.get(key)!r}")
    return errors


def main() -> int:
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    errors = validate_payload(payload)
    audit = payload.get("freshness_audit", {})
    reviewed_on = audit.get("reviewed_on") if isinstance(audit, dict) else None
    report_path = REPORTS / f"{reviewed_on}.json"
    if not isinstance(reviewed_on, str) or not report_path.is_file():
        errors.append(f"missing dated audit report for review date {reviewed_on!r}")
    else:
        report = json.loads(report_path.read_text(encoding="utf-8"))
        errors.extend(validate_report(payload, report))

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"Public project freshness failed with {len(errors)} issue(s).", file=sys.stderr)
        return 1

    audit = payload["freshness_audit"]
    summary = audit["summary"]
    print(
        "Public project freshness passed: "
        f"{summary['repositories_reviewed']} repositories reviewed on {audit['reviewed_on']}; "
        f"{summary['corrected']} corrected, expires {audit['expires_on']}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
