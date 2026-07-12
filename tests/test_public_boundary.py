from __future__ import annotations

import json
import hashlib
import importlib.util
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
GENERATOR = REPO_ROOT / "scripts" / "generate-skills-pages.py"
BOUNDARY_CHECKER = REPO_ROOT / "scripts" / "check-public-boundary.py"
PUBLIC_SKILLS = REPO_ROOT / "scripts" / "public-skills.json"
PUBLIC_BOUNDARY = REPO_ROOT / "scripts" / "public-boundary.json"


def slugify(value: str) -> str:
    value = value.lower().replace("/", "-")
    return re.sub(r"[^a-z0-9_-]+", "-", value).strip("-") or "skill"


def file_snapshot(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file()
    }


def write_unvalidated_skills_tree(root: Path, entries: list[dict[str, str]]) -> None:
    spec = importlib.util.spec_from_file_location("test_skills_generator", GENERATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load skills generator")
    generator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(generator)
    generator.TODAY = "2026-01-01"
    generator.write_skills_tree(root / "skills", entries)


class PublicBoundaryContract(unittest.TestCase):
    def test_generator_publishes_only_allowlisted_reviewed_metadata(self) -> None:
        private_sentinel = "SYNTH_PRIVATE_7B3E_MUST_NOT_PUBLISH"

        with tempfile.TemporaryDirectory() as tmp:
            site_root = Path(tmp) / "site"
            fixture_root = Path(tmp) / "fixtures"
            site_root.mkdir()
            fixture_root.mkdir()
            stale = site_root / "skills" / "synthetic-private-demo"
            stale.mkdir(parents=True)
            (stale / "index.html").write_text(
                "<title>synthetic-private-demo — Hermes Skill Workflow</title>"
                f"<p>{private_sentinel}</p>",
                encoding="utf-8",
            )

            registry = fixture_root / "registry.json"
            registry.write_text(
                json.dumps(
                    {
                        "skills": [
                            {
                                "name": "synthetic-public-demo",
                                "category": "runtime-category",
                                "description": private_sentinel,
                                "source": "local",
                                "trust": "local",
                            },
                            {
                                "name": "synthetic-private-demo",
                                "category": "internal",
                                "description": private_sentinel,
                                "source": "local",
                                "trust": "local",
                            },
                        ]
                    }
                ),
                encoding="utf-8",
            )

            allowlist = fixture_root / "public-skills.json"
            allowlist.write_text(
                json.dumps(
                    {
                        "schema": "viggomeesters.public-skills.v1",
                        "skills": [
                            {
                                "name": "synthetic-public-demo",
                                "category": "public-capability",
                                "description": "A reviewed public description that contains no runtime context.",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(GENERATOR),
                    "--site-root",
                    str(site_root),
                    "--allowlist",
                    str(allowlist),
                    "--registry-json",
                    str(registry),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            data = json.loads((site_root / "skills" / "skills-data.json").read_text())
            self.assertEqual([skill["name"] for skill in data["skills"]], ["synthetic-public-demo"])
            self.assertEqual(data["skills"][0]["category"], "public-capability")
            self.assertEqual(
                data["skills"][0]["description"],
                "A reviewed public description that contains no runtime context.",
            )
            self.assertTrue((site_root / "skills" / "synthetic-public-demo" / "index.html").exists())
            self.assertFalse(stale.exists())

            generated = "\n".join(
                path.read_text(errors="ignore")
                for path in site_root.rglob("*")
                if path.is_file() and path.suffix in {".html", ".json", ".xml"}
            )
            self.assertNotIn("synthetic-private-demo", generated)
            self.assertNotIn(private_sentinel, generated)

    def test_generator_failure_leaves_existing_public_output_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            site_root = root / "site"
            fixture_root = root / "fixtures"
            stale = site_root / "skills" / "synthetic-private-demo"
            stale.mkdir(parents=True)
            fixture_root.mkdir()
            (stale / "index.html").write_text("stale-private-output", encoding="utf-8")
            (site_root / "skills" / "index.html").write_text("old-registry", encoding="utf-8")
            (site_root / "skills" / "skills-data.json").write_text(
                json.dumps({"skills": [{"name": "old-public-output"}]}), encoding="utf-8"
            )
            (site_root / "sitemap.xml").mkdir()

            registry = fixture_root / "registry.json"
            registry.write_text(
                json.dumps({"skills": [{"name": "synthetic-public-demo"}]}), encoding="utf-8"
            )
            allowlist = fixture_root / "public-skills.json"
            allowlist.write_text(
                json.dumps(
                    {
                        "schema": "viggomeesters.public-skills.v1",
                        "skills": [
                            {
                                "name": "synthetic-public-demo",
                                "category": "public-capability",
                                "description": "Reviewed demo metadata.",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            before = file_snapshot(site_root)

            result = subprocess.run(
                [
                    sys.executable,
                    str(GENERATOR),
                    "--site-root",
                    str(site_root),
                    "--allowlist",
                    str(allowlist),
                    "--registry-json",
                    str(registry),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(file_snapshot(site_root), before)

    def test_generator_rejects_unapproved_proper_noun_and_address_like_copy(self) -> None:
        private_sentinel = "SynthPerson at Examplelane 42"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            site_root = root / "site"
            fixture_root = root / "fixtures"
            site_root.mkdir()
            fixture_root.mkdir()
            registry = fixture_root / "registry.json"
            registry.write_text(
                json.dumps({"skills": [{"name": "synthetic-public-demo"}]}), encoding="utf-8"
            )
            allowlist = fixture_root / "public-skills.json"
            allowlist.write_text(
                json.dumps(
                    {
                        "schema": "viggomeesters.public-skills.v1",
                        "approved_proper_nouns": [],
                        "skills": [
                            {
                                "name": "synthetic-public-demo",
                                "category": "public-capability",
                                "description": f"Coordinate with {private_sentinel} for internal operations.",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(GENERATOR),
                    "--site-root",
                    str(site_root),
                    "--allowlist",
                    str(allowlist),
                    "--registry-json",
                    str(registry),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(file_snapshot(site_root), {})
            self.assertNotIn(private_sentinel, result.stdout + result.stderr)

    def test_repository_public_surface_matches_explicit_policy(self) -> None:
        self.assertTrue(PUBLIC_SKILLS.exists(), "missing reviewed public skills allowlist")
        self.assertTrue(PUBLIC_BOUNDARY.exists(), "missing public boundary policy")

        skill_policy = json.loads(PUBLIC_SKILLS.read_text(encoding="utf-8"))
        boundary_policy = json.loads(PUBLIC_BOUNDARY.read_text(encoding="utf-8"))
        allowed_names = {entry["name"] for entry in skill_policy["skills"]}
        allowed_slugs = {slugify(name) for name in allowed_names}

        sitemap = (REPO_ROOT / "sitemap.xml").read_text(encoding="utf-8")
        public_html = "\n".join(
            path.read_text(errors="ignore")
            for path in REPO_ROOT.rglob("*.html")
            if ".git" not in path.parts and ".vercel" not in path.parts
        )
        for route in boundary_policy["blocked_routes"]:
            route_path = REPO_ROOT / route.strip("/") / "index.html"
            self.assertFalse(route_path.exists(), f"blocked route still published: {route}")
            self.assertFalse(route_path.parent.exists(), f"blocked route directory still exists: {route}")
            self.assertNotIn(f"https://viggomeesters.com{route}", sitemap)
            self.assertNotRegex(public_html, rf'href=["\']{re.escape(route)}(?:["\']|#)')

        data = json.loads((REPO_ROOT / "skills" / "skills-data.json").read_text(encoding="utf-8"))
        self.assertEqual({skill["name"] for skill in data["skills"]}, allowed_names)
        detail_slugs = {
            child.name
            for child in (REPO_ROOT / "skills").iterdir()
            if child.is_dir() and (child / "index.html").exists()
        }
        self.assertEqual(detail_slugs, allowed_slugs)

        registry = (REPO_ROOT / "skills" / "index.html").read_text(encoding="utf-8")
        registry_slugs = set(re.findall(r'href="/skills/([^/]+)/"', registry))
        self.assertEqual(registry_slugs, allowed_slugs)

    def test_boundary_checker_detects_hashed_synthetic_private_marker(self) -> None:
        private_marker = "SYNTH_PRIVATE_PERSON_9X"
        marker_hash = hashlib.sha256(private_marker.casefold().encode()).hexdigest()

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "skills" / "synthetic-public-demo").mkdir(parents=True)
            (root / "index.html").write_text(f"<p>{private_marker}</p>", encoding="utf-8")
            (root / "skills" / "index.html").write_text(
                '<a href="/skills/synthetic-public-demo/">Demo</a>', encoding="utf-8"
            )
            (root / "skills" / "synthetic-public-demo" / "index.html").write_text(
                "<p>Reviewed demo</p>", encoding="utf-8"
            )
            (root / "skills" / "skills-data.json").write_text(
                json.dumps({"skills": [{"name": "synthetic-public-demo"}]}), encoding="utf-8"
            )
            (root / "sitemap.xml").write_text(
                "<urlset><url><loc>https://viggomeesters.com/</loc></url></urlset>",
                encoding="utf-8",
            )
            allowlist = root / "public-skills.json"
            allowlist.write_text(
                json.dumps(
                    {
                        "schema": "viggomeesters.public-skills.v1",
                        "skills": [
                            {
                                "name": "synthetic-public-demo",
                                "category": "public-capability",
                                "description": "Reviewed demo metadata.",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            policy = root / "public-boundary.json"
            policy.write_text(
                json.dumps(
                    {
                        "schema": "viggomeesters.public-boundary.v1",
                        "blocked_routes": [],
                        "forbidden_text_hashes": [
                            {"id": "synthetic-private-person", "words": 1, "sha256": marker_hash}
                        ],
                    }
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(BOUNDARY_CHECKER),
                    "--root",
                    str(root),
                    "--public-skills",
                    str(allowlist),
                    "--policy",
                    str(policy),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            output = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("synthetic-private-person", output)
            self.assertNotIn(private_marker, output)

    def test_boundary_checker_rejects_blocked_route_in_deployed_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "skills" / "synthetic-public-demo").mkdir(parents=True)
            (root / "reports" / "seo").mkdir(parents=True)
            (root / "index.html").write_text("<p>Safe home</p>", encoding="utf-8")
            (root / "skills" / "index.html").write_text(
                '<a href="/skills/synthetic-public-demo/">Demo</a>', encoding="utf-8"
            )
            (root / "skills" / "synthetic-public-demo" / "index.html").write_text(
                "<p>Reviewed demo</p>", encoding="utf-8"
            )
            (root / "skills" / "skills-data.json").write_text(
                json.dumps({"skills": [{"name": "synthetic-public-demo"}]}), encoding="utf-8"
            )
            (root / "sitemap.xml").write_text("<urlset></urlset>", encoding="utf-8")
            (root / "reports" / "seo" / "baseline.json").write_text(
                json.dumps({"url": "https://viggomeesters.com/synthetic-private-route/"}),
                encoding="utf-8",
            )
            allowlist = root / "public-skills.json"
            allowlist.write_text(
                json.dumps(
                    {
                        "schema": "viggomeesters.public-skills.v1",
                        "skills": [
                            {
                                "name": "synthetic-public-demo",
                                "category": "public-capability",
                                "description": "Reviewed demo metadata.",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            policy = root / "public-boundary.json"
            policy.write_text(
                json.dumps(
                    {
                        "schema": "viggomeesters.public-boundary.v1",
                        "blocked_routes": ["/synthetic-private-route/"],
                        "forbidden_text_hashes": [],
                    }
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(BOUNDARY_CHECKER),
                    "--root",
                    str(root),
                    "--public-skills",
                    str(allowlist),
                    "--policy",
                    str(policy),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("synthetic-private-route", result.stdout + result.stderr)

    def test_boundary_checker_rejects_copy_drift_under_allowed_skill_name(self) -> None:
        private_sentinel = "SYNTH_RUNTIME_COPY_4Q_MUST_NOT_PUBLISH"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            detail = root / "skills" / "synthetic-public-demo"
            detail.mkdir(parents=True)
            (root / "index.html").write_text("<p>Safe home</p>", encoding="utf-8")
            (root / "skills" / "index.html").write_text(
                f'<a href="/skills/synthetic-public-demo/"><p>{private_sentinel}</p></a>',
                encoding="utf-8",
            )
            (detail / "index.html").write_text(f"<p>{private_sentinel}</p>", encoding="utf-8")
            (root / "skills" / "skills-data.json").write_text(
                json.dumps(
                    {
                        "skills": [
                            {
                                "name": "synthetic-public-demo",
                                "category": "runtime-private",
                                "description": private_sentinel,
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            (root / "sitemap.xml").write_text("<urlset></urlset>", encoding="utf-8")
            allowlist = root / "public-skills.json"
            allowlist.write_text(
                json.dumps(
                    {
                        "schema": "viggomeesters.public-skills.v1",
                        "skills": [
                            {
                                "name": "synthetic-public-demo",
                                "category": "public-capability",
                                "description": "Reviewed demo metadata.",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            policy = root / "public-boundary.json"
            policy.write_text(
                json.dumps(
                    {
                        "schema": "viggomeesters.public-boundary.v1",
                        "blocked_routes": [],
                        "forbidden_text_hashes": [],
                    }
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(BOUNDARY_CHECKER),
                    "--root",
                    str(root),
                    "--public-skills",
                    str(allowlist),
                    "--policy",
                    str(policy),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            output = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("metadata", output)
            self.assertNotIn(private_sentinel, output)

    def test_boundary_checker_rejects_unsafe_copy_even_when_tree_matches_manifest(self) -> None:
        private_sentinel = "SynthPerson at Examplelane 42"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            entries = [
                {
                    "name": "synthetic-public-demo",
                    "category": "public-capability",
                    "description": f"Coordinate with {private_sentinel} for internal operations.",
                }
            ]
            write_unvalidated_skills_tree(root, entries)
            (root / "index.html").write_text("<p>Safe home</p>", encoding="utf-8")
            (root / "sitemap.xml").write_text("<urlset></urlset>", encoding="utf-8")
            allowlist = root / "public-skills.json"
            allowlist.write_text(
                json.dumps(
                    {
                        "schema": "viggomeesters.public-skills.v1",
                        "approved_proper_nouns": [],
                        "skills": entries,
                    }
                ),
                encoding="utf-8",
            )
            policy = root / "public-boundary.json"
            policy.write_text(
                json.dumps(
                    {
                        "schema": "viggomeesters.public-boundary.v1",
                        "blocked_routes": [],
                        "forbidden_text_hashes": [],
                    }
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(BOUNDARY_CHECKER),
                    "--root",
                    str(root),
                    "--public-skills",
                    str(allowlist),
                    "--policy",
                    str(policy),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            output = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("manifest", output)
            self.assertNotIn(private_sentinel, output)


if __name__ == "__main__":
    unittest.main()
