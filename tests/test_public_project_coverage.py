from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check-public-project-coverage.py"
SPEC = importlib.util.spec_from_file_location("project_coverage", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class PublicProjectCoverageContract(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = json.loads((ROOT / "data" / "public-projects.json").read_text(encoding="utf-8"))
        self.pages = MODULE.public_pages()

    def test_all_public_repository_mentions_are_explicitly_classified(self) -> None:
        self.assertEqual(MODULE.validate_coverage(self.payload, self.pages), [])
        mentions = MODULE.repository_mentions(self.pages)
        active = {item["name"] for item in self.payload["repositories"]}
        excluded = {item["name"] for item in self.payload["excluded_repositories"]}
        self.assertEqual(set(mentions), active | excluded)
        self.assertEqual(len(active), 50)
        self.assertEqual(len(excluded), 6)

    def test_removing_historical_classification_exposes_unclassified_link(self) -> None:
        payload = copy.deepcopy(self.payload)
        removed = payload["excluded_repositories"].pop(0)
        errors = MODULE.validate_coverage(payload, self.pages)
        self.assertTrue(any(removed["name"] in error and "unclassified" in error for error in errors), errors)

    def test_old_alias_cannot_reappear_in_public_html(self) -> None:
        pages = dict(self.pages)
        alias = self.payload["renamed_aliases"][0]
        first_file = alias["corrected_files"][0]
        pages[first_file] += f'<a href="{alias["previous_url"]}">stale alias</a>'
        errors = MODULE.validate_coverage(self.payload, pages)
        self.assertTrue(any("renamed repository alias still appears" in error for error in errors), errors)

    def test_undeclared_additional_public_evidence_fails_closed(self) -> None:
        payload = copy.deepcopy(self.payload)
        vault = next(item for item in payload["repositories"] if item["name"] == "vault-schema")
        vault["site_evidence"].remove("variant-0.html")
        errors = MODULE.validate_coverage(payload, self.pages)
        self.assertTrue(any("undeclared public HTML evidence" in error for error in errors), errors)

    def test_every_corrected_variant_keeps_the_canonical_repository_url(self) -> None:
        pages = dict(self.pages)
        alias = self.payload["renamed_aliases"][0]
        first_file = alias["corrected_files"][0]
        pages[first_file] = pages[first_file].replace(alias["canonical_url"], "https://example.invalid/missing")
        errors = MODULE.validate_coverage(self.payload, pages)
        self.assertTrue(any("canonical URL missing" in error for error in errors), errors)

    def test_refresh_preserves_freshness_exclusions_and_aliases(self) -> None:
        live = [
            {
                key: item[key]
                for key in ("name", "url", "description", "created_at", "pushed_at")
            }
            for item in self.payload["repositories"]
        ]
        original_data = MODULE.DATA
        original_live = MODULE.live_repositories
        try:
            with tempfile.TemporaryDirectory() as directory:
                MODULE.DATA = Path(directory) / "public-projects.json"
                MODULE.DATA.write_text(json.dumps(self.payload), encoding="utf-8")
                MODULE.live_repositories = lambda: copy.deepcopy(live)
                self.assertEqual(MODULE.refresh(), 0)
                refreshed = json.loads(MODULE.DATA.read_text(encoding="utf-8"))
                self.assertEqual(refreshed["excluded_repositories"], self.payload["excluded_repositories"])
                self.assertEqual(refreshed["renamed_aliases"], self.payload["renamed_aliases"])
                self.assertEqual(
                    refreshed["repositories"][0]["freshness"],
                    self.payload["repositories"][0]["freshness"],
                )
        finally:
            MODULE.DATA = original_data
            MODULE.live_repositories = original_live


if __name__ == "__main__":
    unittest.main()
