import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_feed_checker():
    spec = importlib.util.spec_from_file_location("feed_link_checker", ROOT / "scripts" / "check-feed-links.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


class ProductionOperationsContract(unittest.TestCase):
    def test_security_routing_and_error_page_are_explicit(self) -> None:
        vercel = json.loads((ROOT / "vercel.json").read_text(encoding="utf-8"))
        self.assertTrue(vercel["cleanUrls"])
        self.assertTrue(vercel["trailingSlash"])
        global_headers = next(entry["headers"] for entry in vercel["headers"] if entry["source"] == "/(.*)")
        csp = next(header["value"] for header in global_headers if header["key"] == "Content-Security-Policy")
        for directive in ("default-src 'self'", "object-src 'none'", "frame-ancestors 'none'", "form-action https://formspree.io"):
            self.assertIn(directive, csp)
        not_found = (ROOT / "404.html").read_text(encoding="utf-8")
        self.assertIn('name="robots" content="noindex, follow"', not_found)
        self.assertIn('href="/"', not_found)

    def test_feed_link_checker_fails_on_proven_dead_link(self) -> None:
        checker = load_feed_checker()
        self.assertEqual(checker.check(ROOT), [])
        with tempfile.TemporaryDirectory() as tmp:
            site = Path(tmp)
            (site / "scripts").mkdir()
            (site / "trendwatch").mkdir()
            (site / "tech-news").mkdir()
            shutil.copy(ROOT / "scripts" / "feed-link-policy.json", site / "scripts" / "feed-link-policy.json")
            policy = json.loads((site / "scripts" / "feed-link-policy.json").read_text(encoding="utf-8"))
            dead = policy["blocked_urls"][0]
            (site / "trendwatch" / "data.json").write_text(json.dumps({"items": [{"url": dead}]}), encoding="utf-8")
            (site / "tech-news" / "data.json").write_text(json.dumps({"items": []}), encoding="utf-8")
            self.assertTrue(any("blocked dead URL" in error for error in checker.check(site)))

    def test_versions_release_docs_and_changed_sitemap_dates_agree(self) -> None:
        package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
        lock = json.loads((ROOT / "package-lock.json").read_text(encoding="utf-8"))
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertEqual(package["version"], "1.3.0")
        self.assertEqual(lock["version"], package["version"])
        self.assertEqual(lock["packages"][""]["version"], package["version"])
        self.assertIn("version-v1.3", readme)
        self.assertIn("## 1.3.0", changelog)
        sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
        marker = "<loc>https://viggomeesters.com/</loc>\n    <lastmod>2026-07-17</lastmod>"
        self.assertIn(marker, sitemap)
        for route in ("/skills/", "/tech-news/", "/trendwatch/"):
            marker = f"<loc>https://viggomeesters.com{route}</loc>\n    <lastmod>2026-07-12</lastmod>"
            self.assertIn(marker, sitemap)

    def test_nl_domain_blocker_is_documented_without_claiming_live_dns(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("SIDN RDAP reports `viggomeesters.nl` as `free`", readme)
        self.assertIn("registration/payment", readme)


if __name__ == "__main__":
    unittest.main()
