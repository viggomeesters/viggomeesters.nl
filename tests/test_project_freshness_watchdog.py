from __future__ import annotations

import importlib.util
import copy
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "watch-public-project-freshness.py"
SPEC = importlib.util.spec_from_file_location("project_freshness_watchdog", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def inventory() -> dict[str, object]:
    return {
        "account": "viggomeesters",
        "freshness_audit": {
            "reviewed_on": "2026-08-31",
            "expires_on": "2026-11-29",
            "policy_days": 90,
        },
        "repositories": [
            {
                "name": "alpha",
                "url": "https://github.com/viggomeesters/alpha",
                "description": "Reviewed description",
                "pushed_at": "2026-08-30T10:00:00Z",
                "freshness": {
                    "head_oid": "a" * 40,
                    "latest_release_tag": "v1.0.0",
                    "latest_release_published_at": "2026-08-29T09:00:00Z",
                    "latest_release_url": "https://github.com/viggomeesters/alpha/releases/tag/v1.0.0",
                    "homepage_url": "https://alpha.example/",
                },
            }
        ],
        "excluded_repositories": [
            {
                "name": "old-fork",
                "url": "https://github.com/viggomeesters/old-fork",
                "pushed_at": "2026-08-01T10:00:00Z",
                "head_oid": "b" * 40,
                "is_archived": True,
                "is_fork": True,
                "parent": "upstream/old-fork",
                "classification": "archived_fork",
            }
        ],
    }


def snapshot() -> dict[str, object]:
    return {
        "repositories": [
            {
                "name": "alpha",
                "url": "https://github.com/viggomeesters/alpha",
                "description": "Reviewed description",
                "homepage_url": "https://alpha.example",
                "pushed_at": "2026-08-30T10:00:00Z",
                "head_oid": "a" * 40,
                "is_archived": False,
                "is_fork": False,
                "parent": None,
                "latest_release_tag": "v1.0.0",
                "latest_release_published_at": "2026-08-29T09:00:00Z",
                "latest_release_url": "https://github.com/viggomeesters/alpha/releases/tag/v1.0.0",
            },
            {
                "name": "old-fork",
                "url": "https://github.com/viggomeesters/old-fork",
                "description": "Fork",
                "homepage_url": None,
                "pushed_at": "2026-08-01T10:00:00Z",
                "head_oid": "b" * 40,
                "is_archived": True,
                "is_fork": True,
                "parent": "upstream/old-fork",
                "latest_release_tag": None,
                "latest_release_published_at": None,
                "latest_release_url": None,
            },
        ]
    }


class ProjectFreshnessWatchdogContract(unittest.TestCase):
    def test_comparison_is_read_only(self) -> None:
        expected = inventory()
        current = snapshot()
        expected_before = copy.deepcopy(expected)
        current_before = copy.deepcopy(current)
        MODULE.compare_inventory(expected, current, today=date(2026, 9, 1))
        self.assertEqual(expected, expected_before)
        self.assertEqual(current, current_before)

    def test_matching_snapshot_and_healthy_homepage_stay_silent(self) -> None:
        expected = inventory()
        current = snapshot()
        expected["repositories"][0]["description"] = ""
        current["repositories"][0]["description"] = None
        findings = MODULE.compare_inventory(
            expected,
            current,
            today=date(2026, 9, 1),
            homepage_results={"https://alpha.example/": {"status": 200, "final_url": "https://alpha.example/"}},
        )
        self.assertEqual(findings, [])
        self.assertEqual(MODULE.render_alert(findings, today=date(2026, 9, 1)), "")

    def test_state_file_only_emits_each_distinct_drift_once(self) -> None:
        current = snapshot()
        current["repositories"][0]["head_oid"] = "c" * 40
        findings = MODULE.compare_inventory(inventory(), current, today=date(2026, 9, 1))
        alert = MODULE.render_alert(findings, today=date(2026, 9, 1))

        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory) / "watchdog.json"
            self.assertEqual(MODULE.stateful_output(findings, alert, state), alert)
            self.assertEqual(MODULE.stateful_output(findings, alert, state), "")
            self.assertTrue(state.is_file())
            self.assertEqual(MODULE.stateful_output([], "", state), "")
            self.assertFalse(state.exists())

    def test_self_hosted_inventory_exception_only_skips_unsatisfiable_head_and_push(self) -> None:
        expected = inventory()
        expected["freshness_watchdog"] = {
            "self_hosted_inventory_repository": "alpha",
            "ignored_self_referential_fields": ["pushed_at", "head_oid"],
            "reason": "The inventory is committed in this repository.",
        }
        current = snapshot()
        current["repositories"][0]["pushed_at"] = "2026-09-01T08:00:00Z"
        current["repositories"][0]["head_oid"] = "c" * 40
        current["repositories"][0]["description"] = "Changed description"

        findings = MODULE.compare_inventory(expected, current, today=date(2026, 9, 1))
        self.assertEqual([item.field for item in findings], ["description"])

        expected["freshness_watchdog"]["ignored_self_referential_fields"].append("description")
        with self.assertRaises(MODULE.WatchdogError):
            MODULE.compare_inventory(expected, current, today=date(2026, 9, 1))

    def test_active_metadata_drift_reports_old_new_and_action(self) -> None:
        current = snapshot()
        repo = current["repositories"][0]
        repo["description"] = "Changed description"
        repo["pushed_at"] = "2026-09-01T08:00:00Z"
        repo["head_oid"] = "c" * 40
        repo["latest_release_tag"] = "v1.1.0"
        repo["latest_release_published_at"] = "2026-09-01T07:00:00Z"
        repo["latest_release_url"] = "https://github.com/viggomeesters/alpha/releases/tag/v1.1.0"

        findings = MODULE.compare_inventory(inventory(), current, today=date(2026, 9, 1))
        alert = MODULE.render_alert(findings, today=date(2026, 9, 1))

        self.assertIn("alpha", alert)
        self.assertIn("description", alert)
        self.assertIn("Reviewed description", alert)
        self.assertIn("Changed description", alert)
        self.assertIn("v1.0.0", alert)
        self.assertIn("v1.1.0", alert)
        self.assertIn("Actie:", alert)
        self.assertIn("Geen automatische wijzigingen uitgevoerd", alert)

    def test_unexpected_missing_and_classification_drift_are_alerted(self) -> None:
        current = snapshot()
        current["repositories"] = [repo for repo in current["repositories"] if repo["name"] != "alpha"]
        current["repositories"][0]["is_archived"] = False
        current["repositories"].append(
            {
                "name": "new-public-repo",
                "url": "https://github.com/viggomeesters/new-public-repo",
                "description": "New",
                "homepage_url": None,
                "pushed_at": "2026-09-01T09:00:00Z",
                "head_oid": "d" * 40,
                "is_archived": False,
                "is_fork": False,
                "parent": None,
                "latest_release_tag": None,
                "latest_release_published_at": None,
                "latest_release_url": None,
            }
        )

        alert = MODULE.render_alert(
            MODULE.compare_inventory(inventory(), current, today=date(2026, 9, 1)),
            today=date(2026, 9, 1),
        )
        self.assertIn("alpha", alert)
        self.assertIn("ontbreekt publiek", alert)
        self.assertIn("new-public-repo", alert)
        self.assertIn("niet geclassificeerd", alert)
        self.assertIn("old-fork", alert)
        self.assertIn("is_archived", alert)

    def test_expiry_warning_and_expired_audit_alert(self) -> None:
        warning = MODULE.compare_inventory(inventory(), snapshot(), today=date(2026, 11, 20))
        expired = MODULE.compare_inventory(inventory(), snapshot(), today=date(2026, 11, 30))
        self.assertTrue(any(item.field == "audit_expiry" and item.severity == "warning" for item in warning))
        self.assertTrue(any(item.field == "audit_expiry" and item.severity == "critical" for item in expired))

    def test_dead_homepage_is_alerted_with_status(self) -> None:
        findings = MODULE.compare_inventory(
            inventory(),
            snapshot(),
            today=date(2026, 9, 1),
            homepage_results={"https://alpha.example/": {"status": 503, "final_url": "https://alpha.example/error"}},
        )
        alert = MODULE.render_alert(findings, today=date(2026, 9, 1))
        self.assertIn("homepage", alert)
        self.assertIn("503", alert)
        self.assertIn("https://alpha.example/error", alert)

    def test_malformed_homepage_is_returned_as_a_failed_measurement(self) -> None:
        _, result = MODULE._check_homepage("not a URL", 0.01)
        self.assertEqual(result["status"], "error")
        self.assertIn("error", result)

    def test_graphql_payload_normalization_and_pagination_guard(self) -> None:
        payload = {
            "data": {
                "repositoryOwner": {
                    "repositories": {
                        "nodes": [
                            {
                                "name": "alpha",
                                "url": "https://github.com/viggomeesters/alpha",
                                "description": "Reviewed description",
                                "homepageUrl": "https://alpha.example",
                                "pushedAt": "2026-08-30T10:00:00Z",
                                "isArchived": False,
                                "isFork": False,
                                "parent": None,
                                "defaultBranchRef": {"target": {"oid": "a" * 40}},
                                "latestRelease": {
                                    "tagName": "v1.0.0",
                                    "publishedAt": "2026-08-29T09:00:00Z",
                                    "url": "https://github.com/viggomeesters/alpha/releases/tag/v1.0.0",
                                },
                            }
                        ],
                        "pageInfo": {"hasNextPage": False, "endCursor": None},
                    }
                }
            }
        }
        normalized = MODULE.normalize_graphql_snapshot(payload)
        self.assertEqual(normalized["repositories"][0]["head_oid"], "a" * 40)
        payload["data"]["repositoryOwner"]["repositories"]["pageInfo"]["hasNextPage"] = True
        with self.assertRaises(MODULE.WatchdogError):
            MODULE.normalize_graphql_snapshot(payload)
        payload["data"]["repositoryOwner"]["repositories"]["pageInfo"] = None
        with self.assertRaises(MODULE.WatchdogError):
            MODULE.normalize_graphql_snapshot(payload)
        for malformed in ({}, {"hasNextPage": None}, {"hasNextPage": "false"}):
            payload["data"]["repositoryOwner"]["repositories"]["pageInfo"] = malformed
            with self.subTest(page_info=malformed), self.assertRaises(MODULE.WatchdogError):
                MODULE.normalize_graphql_snapshot(payload)

    def test_alert_is_bounded_and_does_not_echo_secret_like_fields(self) -> None:
        current = snapshot()
        for index in range(40):
            current["repositories"].append(
                {
                    "name": f"unexpected-{index:02d}",
                    "url": f"https://github.com/viggomeesters/unexpected-{index:02d}",
                    "description": "token=ghp_should_never_be_echoed",
                    "homepage_url": None,
                    "pushed_at": "2026-09-01T09:00:00Z",
                    "head_oid": "d" * 40,
                    "is_archived": False,
                    "is_fork": False,
                    "parent": None,
                    "latest_release_tag": None,
                    "latest_release_published_at": None,
                    "latest_release_url": None,
                }
            )
        findings = MODULE.compare_inventory(inventory(), current, today=date(2026, 9, 1))
        alert = MODULE.render_alert(findings, today=date(2026, 9, 1), max_findings=10)
        self.assertLess(len(alert.splitlines()), 70)
        self.assertIn("30 aanvullende bevinding", alert)
        self.assertNotIn("ghp_should_never_be_echoed", alert)

        caller_cannot_raise_limit = MODULE.render_alert(findings, today=date(2026, 9, 1), max_findings=999)
        self.assertEqual(caller_cannot_raise_limit.count("- KRITIEK"), MODULE.MAX_FINDINGS)
        self.assertIn("20 aanvullende bevinding", caller_cannot_raise_limit)


if __name__ == "__main__":
    unittest.main()
