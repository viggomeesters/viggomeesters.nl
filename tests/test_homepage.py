from __future__ import annotations

import html
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOMEPAGE = ROOT / "index.html"


def visible_text(markup: str) -> str:
    markup = re.sub(r"<(script|style)\b[\s\S]*?</\1>", " ", markup, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", markup)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


class HomepageGatewayContract(unittest.TestCase):
    def setUp(self) -> None:
        self.markup = HOMEPAGE.read_text(encoding="utf-8")
        self.text = visible_text(self.markup)

    def test_homepage_is_a_four_gateway_front_door(self) -> None:
        gateways = re.findall(
            r'<a class="gateway"[^>]*href="([^"]+)"[^>]*>[\s\S]*?<h2>([^<]+)</h2>',
            self.markup,
        )
        self.assertEqual(
            gateways,
            [
                ("/timeline/", "Timeline"),
                ("/apps/", "Apps"),
                ("/systems/", "Systems"),
                ("/guides/", "Writing"),
            ],
        )
        self.assertEqual(self.markup.count("<h1"), 1)
        for term in ("Viggo Meesters", "data migration", "AI systems"):
            self.assertIn(term.casefold(), self.text.casefold())

    def test_each_gateway_owns_a_semantic_route_colour_shared_with_its_hub(self) -> None:
        route_colours = {
            "timeline": ("/timeline/", "#38bdf8"),
            "apps": ("/apps/", "#a78bfa"),
            "systems": ("/systems/", "#4ade80"),
            "writing": ("/guides/", "#f59e0b"),
        }

        for route, (href, colour) in route_colours.items():
            with self.subTest(route=route):
                self.assertRegex(
                    self.markup,
                    rf'<a class="gateway" data-route="{route}" href="{re.escape(href)}">',
                )
                self.assertIn(f'[data-route="{route}"]{{--route-accent:{colour};', self.markup)

                hub = ROOT / href.strip("/") / "index.html"
                self.assertIn(f"--accent:{colour};", hub.read_text(encoding="utf-8"))

        self.assertIn("background:rgba(var(--route-rgb),.055)", self.markup)
        self.assertIn("color:var(--route-accent)", self.markup)

    def test_homepage_no_longer_duplicates_the_catalogs(self) -> None:
        for legacy in (
            'class="tile flagship-card"',
            'id="selected-work"',
            'id="contact-form"',
            "trendwatch/status.json",
            "tech-news/status.json",
        ):
            self.assertNotIn(legacy, self.markup)


if __name__ == "__main__":
    unittest.main()
