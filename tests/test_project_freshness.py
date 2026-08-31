from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check-public-project-freshness.py"
SPEC = importlib.util.spec_from_file_location("project_freshness", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class PublicProjectFreshnessContract(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = json.loads((ROOT / "data" / "public-projects.json").read_text(encoding="utf-8"))
        reviewed_on = self.payload["freshness_audit"]["reviewed_on"]
        self.report = json.loads(
            (ROOT / "reports" / "project-freshness" / f"{reviewed_on}.json").read_text(encoding="utf-8")
        )

    def test_current_inventory_has_valid_freshness_evidence(self) -> None:
        self.assertEqual(MODULE.validate_payload(self.payload, date(2026, 8, 31)), [])
        self.assertEqual(MODULE.validate_report(self.payload, self.report), [])

    def test_missing_repository_evidence_fails_closed(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["repositories"][0].pop("freshness")
        errors = MODULE.validate_payload(payload, date(2026, 8, 31))
        self.assertTrue(any("missing freshness evidence" in error for error in errors), errors)

    def test_new_push_invalidates_previous_review(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["repositories"][0]["pushed_at"] = "2026-09-01T00:00:00Z"
        errors = MODULE.validate_payload(payload, today=date(2026, 9, 1))
        self.assertTrue(any("new push metadata" in error for error in errors), errors)

    def test_changed_description_invalidates_previous_review(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["repositories"][0]["description"] = "Changed on GitHub without a code push"
        errors = MODULE.validate_payload(payload, today=date(2026, 9, 1))
        self.assertTrue(any("changed repository description" in error for error in errors), errors)

    def test_policy_and_snapshot_date_cannot_lie(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["freshness_audit"]["policy_days"] = 7
        payload["snapshot_date"] = "2026-08-30"
        errors = MODULE.validate_payload(payload, date(2026, 8, 31))
        self.assertTrue(any("policy_days" in error for error in errors), errors)
        self.assertTrue(any("snapshot_date" in error for error in errors), errors)

    def test_release_and_homepage_evidence_are_structural(self) -> None:
        payload = copy.deepcopy(self.payload)
        released = next(item for item in payload["repositories"] if item["freshness"]["latest_release_tag"])
        released["freshness"]["latest_release_published_at"] = "not-a-timestamp"
        homepage = next(item for item in payload["repositories"] if item["freshness"]["homepage_url"])
        homepage["freshness"]["sources"].remove(homepage["freshness"]["homepage_url"])
        errors = MODULE.validate_payload(payload, date(2026, 8, 31))
        self.assertTrue(any("latest_release_published_at" in error for error in errors), errors)
        self.assertTrue(any("homepage evidence" in error for error in errors), errors)

    def test_report_expiry_and_derived_counts_cannot_lie(self) -> None:
        report = copy.deepcopy(self.report)
        report["expires_on"] = "2099-01-01"
        report["evidence"]["homepage_urls_checked"] = 999
        report["evidence"]["excluded_public_repository_mentions_classified"] = 999
        errors = MODULE.validate_report(self.payload, report)
        self.assertTrue(any("report expiry" in error for error in errors), errors)
        self.assertTrue(any("homepage_urls_checked" in error for error in errors), errors)
        self.assertTrue(any("excluded_public_repository_mentions_classified" in error for error in errors), errors)

    def test_exclusion_and_alias_evidence_fail_closed(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["excluded_repositories"][0]["is_archived"] = False
        payload["renamed_aliases"][0]["http_status"] = 404
        errors = MODULE.validate_payload(payload, date(2026, 8, 31))
        self.assertTrue(any("archive/fork state" in error for error in errors), errors)
        self.assertTrue(any("alias redirect" in error for error in errors), errors)

    def test_expired_audit_fails_closed(self) -> None:
        errors = MODULE.validate_payload(self.payload, date(2026, 11, 30))
        self.assertTrue(any("freshness audit expired" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
