import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class WatcherExperienceContract(unittest.TestCase):
    def test_watchers_progressively_render_and_announce_compact_status(self) -> None:
        for relative in ("trendwatch/index.html", "tech-news/index.html"):
            with self.subTest(page=relative):
                html = (ROOT / relative).read_text(encoding="utf-8")
                self.assertIn("const PAGE_SIZE = 24", html)
                self.assertIn("rows.slice(0, visibleCount)", html)
                self.assertIn('id="load-more"', html)
                self.assertIn('id="feed-status" role="status" aria-live="polite"', html)
                feed_tag = re.search(r'<section class="feed"[^>]*>', html)
                self.assertIsNotNone(feed_tag)
                self.assertNotIn("aria-live", feed_tag.group(0))

    def test_watcher_filter_state_is_url_persistent(self) -> None:
        trend = (ROOT / "trendwatch/index.html").read_text(encoding="utf-8")
        news = (ROOT / "tech-news/index.html").read_text(encoding="utf-8")
        for html in (trend, news):
            self.assertIn("new URLSearchParams(location.search)", html)
            self.assertIn("history.replaceState", html)
            self.assertIn("params.set('q'", html)
            self.assertIn("params.set('filter'", html)
        self.assertIn("params.set('sort'", trend)

    def test_status_snapshots_match_full_feed_metadata(self) -> None:
        for directory in ("trendwatch", "tech-news"):
            with self.subTest(feed=directory):
                data = json.loads((ROOT / directory / "data.json").read_text(encoding="utf-8"))
                status = json.loads((ROOT / directory / "status.json").read_text(encoding="utf-8"))
                for key in ("generatedAt", "total", "usefulOpen"):
                    self.assertEqual(status[key], data[key])
                self.assertNotIn("items", status)
                self.assertLess((ROOT / directory / "status.json").stat().st_size, 512)

if __name__ == "__main__":
    unittest.main()
