from __future__ import annotations

import html
import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
HOMEPAGE = REPO_ROOT / "index.html"


def visible_text(markup: str) -> str:
    markup = re.sub(r"<(script|style)\b[\s\S]*?</\1>", " ", markup, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", markup)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


class HomepagePortfolioContract(unittest.TestCase):
    def setUp(self) -> None:
        self.markup = HOMEPAGE.read_text(encoding="utf-8")
        self.text = visible_text(self.markup.split("<body>", 1)[1])

    def test_hero_leads_with_audience_value_and_one_primary_cta(self) -> None:
        selected_work = self.markup.index('id="selected-work"')
        hero = self.markup[:selected_work]

        self.assertEqual(hero.count('class="hero-cta"'), 1)
        self.assertIn('href="#selected-work"', hero)
        for term in ("delivery teams", "auditable workflows", "SAP", "ETL", "Alteryx"):
            self.assertIn(term, visible_text(hero))

    def test_four_flagship_cases_have_problem_result_proof_and_public_evidence(self) -> None:
        cases = re.findall(
            r'<article class="tile flagship-card"[\s\S]*?</article>',
            self.markup,
        )
        self.assertEqual(len(cases), 4)

        names = []
        for case in cases:
            name_match = re.search(r"<h3>([^<]+)</h3>", case)
            self.assertIsNotNone(name_match)
            names.append(html.unescape(name_match.group(1)))
            for label in ("Problem", "Result", "Proof"):
                self.assertIn(f"<dt>{label}</dt>", case)
            self.assertRegex(case, r'<a href="[^"]+"')

        self.assertEqual(
            names,
            [
                "Minimal ETL Modeler",
                "SAP Agent Context",
                "Alteryx Viewer",
                "Mega Vault Viewer",
            ],
        )
        for href in (
            "https://minimal-etl-modeler.vercel.app",
            "https://github.com/viggomeesters/sap-agent-context",
            "https://github.com/viggomeesters/obsidian-alteryx-viewer",
            "https://github.com/viggomeesters/mega-vault-viewer",
        ):
            self.assertIn(f'href="{href}"', self.markup)

    def test_professional_data_expertise_is_visible(self) -> None:
        for term in ("sap migration", "data migration", "etl", "alteryx", "csv/xlsx", "field mapping"):
            self.assertIn(term, self.text.casefold())


if __name__ == "__main__":
    unittest.main()
