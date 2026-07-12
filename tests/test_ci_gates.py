from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SEO_AUDIT = REPO_ROOT / "scripts" / "seo-audit.mjs"
CHECK_ALL = REPO_ROOT / "scripts" / "check-all.sh"
SITE_CHECK = REPO_ROOT / "scripts" / "check-site.mjs"


def snapshot(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in root.rglob("*")
        if path.is_file()
    }


def valid_page(title: str = "Synthetic Portfolio Page With Clear Purpose") -> str:
    description = (
        "A synthetic public page used to prove that the SEO regression gate is read-only "
        "and fails when a newly introduced issue is not present in the reviewed baseline."
    )
    words = " ".join(["evidence"] * 260)
    return f'''<!doctype html>
<html lang="en"><head>
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="https://viggomeesters.com/">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="https://viggomeesters.com/">
<meta property="og:image" content="https://viggomeesters.com/og-image.png">
<meta name="twitter:card" content="summary_large_image">
<script defer src="/_vercel/insights/script.js"></script>
</head><body><h1>Synthetic portfolio</h1><p>{words}</p></body></html>'''


class ContinuousIntegrationContract(unittest.TestCase):
    def test_site_check_fails_on_a11y_and_local_link_regressions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            site = Path(tmp) / "site"
            shutil.copytree(
                REPO_ROOT,
                site,
                ignore=shutil.ignore_patterns(".git", ".vercel", "node_modules", "__pycache__"),
            )

            news = site / "tech-news" / "index.html"
            original_news = news.read_text(encoding="utf-8")
            news.write_text(
                original_news.replace(' aria-label="Filter technology news"', "", 1),
                encoding="utf-8",
            )
            a11y = subprocess.run(
                ["node", str(SITE_CHECK)],
                cwd=site,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(a11y.returncode, 0)
            self.assertIn("form control missing accessible label", a11y.stdout + a11y.stderr)

            news.write_text(original_news, encoding="utf-8")
            homepage = site / "index.html"
            homepage.write_text(
                homepage.read_text(encoding="utf-8").replace(
                    'href="/guides/"', 'href="/synthetic-missing-route/"', 1
                ),
                encoding="utf-8",
            )
            link = subprocess.run(
                ["node", str(SITE_CHECK)],
                cwd=site,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(link.returncode, 0)
            self.assertIn("broken local reference", link.stdout + link.stderr)

    def test_full_gate_detects_content_mutation_in_already_dirty_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            tracked = root / "tracked.txt"
            tracked.write_text("base\n", encoding="utf-8")
            subprocess.run(["git", "add", "tracked.txt"], cwd=root, check=True)
            subprocess.run(
                [
                    "git",
                    "-c",
                    "user.name=CI fixture",
                    "-c",
                    "user.email=ci-fixture@example.invalid",
                    "commit",
                    "-qm",
                    "base",
                ],
                cwd=root,
                check=True,
            )
            tracked.write_text("pre-existing user change\n", encoding="utf-8")

            fake_bin = root / "fake-bin"
            fake_bin.mkdir()
            fake_npm = fake_bin / "npm"
            fake_npm.write_text(
                '#!/usr/bin/env bash\nprintf "gate mutation\\n" >> tracked.txt\n',
                encoding="utf-8",
            )
            fake_npm.chmod(0o755)
            env = {**os.environ, "PATH": f"{fake_bin}:{os.environ['PATH']}"}

            result = subprocess.run(
                ["bash", str(CHECK_ALL)],
                cwd=root,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("mutated the working tree", result.stdout + result.stderr)

    def test_seo_check_is_read_only_and_fails_on_new_regression(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "index.html").write_text(valid_page(), encoding="utf-8")
            (root / "sitemap.xml").write_text(
                '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://viggomeesters.com/</loc>
    <lastmod>2026-07-12</lastmod>
    <priority>1.0</priority>
  </url>
</urlset>
''',
                encoding="utf-8",
            )

            update = subprocess.run(
                ["node", str(SEO_AUDIT), "--update"],
                cwd=root,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(update.returncode, 0, update.stderr or update.stdout)
            before_check = snapshot(root)

            clean = subprocess.run(
                ["node", str(SEO_AUDIT)],
                cwd=root,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(clean.returncode, 0, clean.stderr or clean.stdout)
            self.assertEqual(snapshot(root), before_check)

            (root / "index.html").write_text(valid_page("Short"), encoding="utf-8")
            reports_before_failure = snapshot(root / "reports")
            regression = subprocess.run(
                ["node", str(SEO_AUDIT)],
                cwd=root,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(regression.returncode, 0)
            self.assertIn("short_title", regression.stdout + regression.stderr)
            self.assertEqual(snapshot(root / "reports"), reports_before_failure)

    def test_github_actions_runs_the_documented_full_gate(self) -> None:
        package = json.loads((REPO_ROOT / "package.json").read_text(encoding="utf-8"))
        workflow = (REPO_ROOT / ".github" / "workflows" / "quality.yml").read_text(
            encoding="utf-8"
        )
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

        self.assertEqual(package["scripts"]["check:all"], "bash scripts/check-all.sh")
        self.assertIn("pull_request:", workflow)
        self.assertIn("branches: [main]", workflow)
        self.assertIn("contents: read", workflow)
        self.assertIn("run: npm run check:all", workflow)
        self.assertIn("npm run check:all", readme)
        self.assertIn("npm run check:seo:update", readme)


if __name__ == "__main__":
    unittest.main()
