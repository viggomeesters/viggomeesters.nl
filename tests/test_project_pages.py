from __future__ import annotations

import html
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "projects" / "data.json"


class ProjectPageContract(unittest.TestCase):
    def test_every_professional_source_project_has_a_first_party_page(self) -> None:
        self.assertTrue(CATALOG.is_file(), "projects/data.json is the required source of truth")
        projects = json.loads(CATALOG.read_text(encoding="utf-8"))
        self.assertEqual(len(projects), 36)
        self.assertEqual(len({project["slug"] for project in projects}), 36)

        timeline = (ROOT / "timeline" / "index.html").read_text(encoding="utf-8")
        sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")

        for project in projects:
            with self.subTest(project=project["slug"]):
                route = f'/projects/{project["slug"]}/'
                page = ROOT / route.strip("/") / "index.html"
                self.assertTrue(page.is_file())
                markup = page.read_text(encoding="utf-8")

                self.assertIn(
                    f'<link rel="canonical" href="https://viggomeesters.com{route}">',
                    markup,
                )
                self.assertEqual(markup.count("<h1"), 1)
                self.assertIn(html.escape(project["title"]), markup)
                self.assertIn(html.escape(project["period"]), markup)
                self.assertIn(html.escape(project["role"]), markup)
                title = re.search(r"<title>(.*?)</title>", markup, re.DOTALL)
                description = re.search(
                    r'<meta name="description" content="(.*?)">', markup, re.DOTALL
                )
                self.assertIsNotNone(title)
                self.assertIsNotNone(description)
                self.assertGreaterEqual(len(title.group(1)), 25)
                self.assertGreaterEqual(len(description.group(1)), 80)
                self.assertIn('data-detail-status="needs-input"', markup)
                self.assertNotIn("TODO", markup)

                self.assertIn(f'href="{route}"', timeline)
                self.assertIn(f"https://viggomeesters.com{route}", sitemap)

    def test_project_index_exposes_all_projects_and_the_known_content_gaps(self) -> None:
        projects = json.loads(CATALOG.read_text(encoding="utf-8"))
        page = ROOT / "projects" / "index.html"
        self.assertTrue(page.is_file())
        markup = page.read_text(encoding="utf-8")

        self.assertEqual(markup.count('class="project-row"'), len(projects))
        self.assertIn("What can still be added", markup)
        self.assertIn("36 projects", markup)


if __name__ == "__main__":
    unittest.main()
