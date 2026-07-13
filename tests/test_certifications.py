from __future__ import annotations

import hashlib
import html
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "certifications" / "data.json"


class CertificationArchiveContract(unittest.TestCase):
    def test_all_credentials_are_catalogued_with_local_proof_where_available(self) -> None:
        self.assertTrue(CATALOG.is_file(), "certifications/data.json is required")
        credentials = json.loads(CATALOG.read_text(encoding="utf-8"))

        self.assertEqual(len(credentials), 36)
        self.assertEqual(len({item["slug"] for item in credentials}), 36)
        self.assertEqual(
            [item["issued"] for item in credentials],
            sorted((item["issued"] for item in credentials), reverse=True),
        )

        hosted = 0
        unavailable = []
        for item in credentials:
            with self.subTest(credential=item["slug"]):
                self.assertTrue(item["title"])
                self.assertTrue(item["issuer"])
                self.assertTrue(item["verification_url"].startswith("https://"))
                artifact = item["artifact"]
                self.assertIn(artifact["status"], {"hosted", "source_unavailable"})

                if artifact["status"] == "hosted":
                    hosted += 1
                    path = ROOT / artifact["path"].lstrip("/")
                    self.assertTrue(path.is_file(), path)
                    self.assertGreater(path.stat().st_size, 10_000, path)
                    self.assertEqual(
                        hashlib.sha256(path.read_bytes()).hexdigest(),
                        artifact["sha256"],
                    )
                    self.assertIn(artifact["mime_type"], {"application/pdf", "image/png", "image/jpeg"})
                    self.assertIn(artifact["provenance"], {"vault_cas", "official_verification_page"})
                else:
                    unavailable.append(item)
                    self.assertEqual(item["issuer"], "Aiden Academy")
                    self.assertIn("authentication", artifact["reason"].lower())

        self.assertEqual(hosted, 30)
        self.assertEqual(len(unavailable), 6)

    def test_archive_and_timeline_expose_every_credential(self) -> None:
        credentials = json.loads(CATALOG.read_text(encoding="utf-8"))
        archive = (ROOT / "certifications" / "index.html").read_text(encoding="utf-8")
        timeline = (ROOT / "timeline" / "index.html").read_text(encoding="utf-8")
        sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
        visible_text = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", archive)).split())

        self.assertEqual(archive.count('class="credential-row"'), 36)
        self.assertIn("30 locally hosted proofs", visible_text)
        self.assertIn("6 source files still needed", visible_text)
        self.assertIn("https://viggomeesters.com/certifications/", sitemap)

        learning_cards = re.findall(
            r'<article class="timeline-entry"[^>]+data-type="certificate"[^>]*>',
            timeline,
        )
        self.assertEqual(
            len(learning_cards),
            36,
            "every credential should have its own timeline card",
        )

        for item in credentials:
            with self.subTest(credential=item["slug"]):
                self.assertIn(f'id="{item["slug"]}"', archive)
                self.assertIn(item["title"], archive)
                self.assertIn(f'/certifications/#{item["slug"]}', timeline)
                self.assertIn(f'data-certification="{item["slug"]}"', timeline)


if __name__ == "__main__":
    unittest.main()
