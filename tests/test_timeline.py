from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TIMELINE = ROOT / "timeline" / "index.html"


class TimelineContract(unittest.TestCase):
    def setUp(self) -> None:
        self.markup = TIMELINE.read_text(encoding="utf-8") if TIMELINE.exists() else ""

    def test_timeline_is_public_and_discoverable(self) -> None:
        self.assertTrue(TIMELINE.is_file())
        markup = TIMELINE.read_text(encoding="utf-8")
        homepage = (ROOT / "index.html").read_text(encoding="utf-8")
        sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")

        self.assertIn('<link rel="canonical" href="https://viggomeesters.com/timeline/">', markup)
        self.assertEqual(markup.count("<h1"), 1)
        self.assertIn('href="/timeline/"', homepage)
        self.assertIn("https://viggomeesters.com/timeline/", sitemap)

    def test_entries_are_curated_and_reverse_chronological(self) -> None:
        entries = re.findall(
            r'<article class="timeline-entry[^\"]*" data-date="([0-9-]+)" data-type="([a-z-]+)"',
            self.markup,
        )
        self.assertGreaterEqual(len(entries), 14)
        dates = [date for date, _ in entries]
        self.assertEqual(dates, sorted(dates, reverse=True))
        self.assertTrue({"project", "repository", "workflow", "writing"}.issubset({kind for _, kind in entries}))
        self.assertEqual(self.markup.count("<time "), len(entries))
        self.assertNotIn("coming soon", self.markup.casefold())

    def test_timeline_connects_the_complete_professional_record_and_public_hubs(self) -> None:
        professional_projects = (
            "Alteryx Flow Agent Toolkit",
            "SDP Dashboard",
            "Alteryx Template Flows",
            "Smart Data Platform",
            "Minimal ETL Modeler",
            "Gemeente Groningen",
            "Hitachi Construction Machinery Europe",
            "Universiteit Utrecht",
            "Cramo Fleet",
            "LC Packaging NL",
            "Cramo Baltics",
            "Mepal",
            "OKR Coaching",
            "Cramo Sweden &amp; Norway",
            "Boels Fleet NL",
            "Cramo Finland",
            "Traineeship 2.0",
            "RPA Invoicing for LiveKindly",
            "Automated Content Generator",
            "Learning Technology Vision",
            "ZES Battery Container",
            "Special Events for Withlocals",
            "Veilig Op Reis tas",
            "Warehouse Management System — part 2",
            "Customer Satisfaction Analysis",
            "Value Proposition Design for De Uitvindfabriek",
            "Serious Game for Agile Working",
            "Warehouse Management System — part 1",
            "Culture Research at Oriëntal Green House",
            "Business Academy Event",
            "Handlefy Storage Application Database",
            "Optimize Data Entry at Versteijnen Logistics",
            "BPMN Goods Documents at Versteijnen Logistics",
            "Optimize Banking Process at Gors",
            "ProActive Banking Implementation Research",
            "Optimize Creditor Process at Gors",
        )
        for title in professional_projects:
            with self.subTest(title=title):
                self.assertIn(title, self.markup)

        connected_hubs = re.findall(
            r'<a class="(?:app|system)-card"[^>]+href="([^"]+)"',
            (ROOT / "apps" / "index.html").read_text(encoding="utf-8")
            + (ROOT / "systems" / "index.html").read_text(encoding="utf-8"),
        )
        for href in connected_hubs:
            with self.subTest(href=href):
                self.assertIn(f'href="{href}"', self.markup)

        articles = re.findall(r'<article class="timeline-entry[^>]*>[\s\S]*?</article>', self.markup)
        self.assertGreaterEqual(len(articles), 55)
        self.assertTrue(all('class="proof-links"' in article for article in articles))

    def test_filters_are_accessible_and_url_addressable(self) -> None:
        for kind in ("all", "career", "project", "repository", "workflow", "writing"):
            self.assertIn(f'data-filter="{kind}"', self.markup)
        self.assertIn('role="status"', self.markup)
        self.assertIn("URLSearchParams", self.markup)
        self.assertIn("history.replaceState", self.markup)
        self.assertIn("popstate", self.markup)


if __name__ == "__main__":
    unittest.main()
