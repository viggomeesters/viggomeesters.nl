from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PortfolioHubContract(unittest.TestCase):
    def test_new_hubs_are_public_and_discoverable(self) -> None:
        homepage = (ROOT / "index.html").read_text(encoding="utf-8")
        sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
        for route in ("/apps/", "/systems/"):
            self.assertIn(f'href="{route}"', homepage)
            self.assertIn(f"https://viggomeesters.com{route}", sitemap)

    def test_apps_hub_separates_try_now_from_install_or_inspect(self) -> None:
        page = ROOT / "apps" / "index.html"
        self.assertTrue(page.is_file())
        markup = page.read_text(encoding="utf-8")

        self.assertIn('<link rel="canonical" href="https://viggomeesters.com/apps/">', markup)
        self.assertEqual(markup.count("<h1"), 1)
        live = re.findall(
            r'<a class="app-card" data-kind="live" href="([^"]+)"[\s\S]*?<h3>([^<]+)</h3>',
            markup,
        )
        self.assertEqual(
            live,
            [
                ("https://sap-data-readiness.vercel.app", "SAP Data Readiness"),
                ("https://minimal-etl-modeler.vercel.app", "Minimal ETL Modeler"),
                ("https://visual-pm-app.vercel.app", "Visual PM"),
                ("https://normalized-salary-calculator.vercel.app", "Normalized Salary Calculator"),
                ("https://money-shower.vercel.app", "Money Shower"),
                ("https://getdimma.vercel.app", "Dimma"),
                ("https://kraamweek.vercel.app", "Kraamweek"),
                ("https://dayline-seven.vercel.app", "Dayline"),
            ],
        )
        inspectable = re.findall(
            r'<a class="app-card" data-kind="inspect" href="([^"]+)"[\s\S]*?<h3>([^<]+)</h3>',
            markup,
        )
        self.assertEqual(
            inspectable,
            [
                ("/mega-vault-viewer/", "Mega Vault Viewer"),
                ("/obsidian-plugins/", "Obsidian Plugins"),
                ("/raycast-life-os/", "Raycast Life OS"),
            ],
        )

    def test_systems_hub_separates_delivery_from_knowledge_infrastructure(self) -> None:
        page = ROOT / "systems" / "index.html"
        self.assertTrue(page.is_file())
        markup = page.read_text(encoding="utf-8")

        self.assertIn('<link rel="canonical" href="https://viggomeesters.com/systems/">', markup)
        self.assertEqual(markup.count("<h1"), 1)
        delivery = re.findall(
            r'<a class="system-card" data-layer="delivery" href="([^"]+)">[\s\S]*?<h3>([^<]+)</h3>',
            markup,
        )
        self.assertEqual(
            delivery,
            [
                ("/go-workflow-stack/", "Go Workflow Stack"),
                ("/go-project-template/", "Go Project Template"),
                ("/agent-workflow/", "Agent Workflow"),
                ("/skills/", "Reviewed Skills"),
            ],
        )
        knowledge = re.findall(
            r'<a class="system-card" data-layer="knowledge" href="([^"]+)">[\s\S]*?<h3>([^<]+)</h3>',
            markup,
        )
        self.assertEqual(
            knowledge,
            [
                ("/personal-knowledge-system/", "Personal Knowledge System"),
                ("/vault-layer/", "VaultLayer"),
                ("/sap-agent-context/", "SAP Agent Context"),
                ("/nederlandse-huizenkoop-agent-context/", "Homebuying Agent Context"),
            ],
        )


if __name__ == "__main__":
    unittest.main()
