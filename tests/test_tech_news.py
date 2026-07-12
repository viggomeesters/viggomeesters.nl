from __future__ import annotations

import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
COLLECTOR = REPO_ROOT / "scripts" / "collect-tech-news-data.py"


def load_collector():
    spec = importlib.util.spec_from_file_location("tech_news_collector_under_test", COLLECTOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load Tech News collector")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class TechNewsClassifierContract(unittest.TestCase):
    def test_generic_capability_phrases_need_ai_product_context(self) -> None:
        collector = load_collector()
        cases = [
            "Tool use in chimpanzees reveals a cultural tradition",
            "Computer use policy changes for the public library",
        ]

        for index, title in enumerate(cases):
            with self.subTest(title=title):
                result = collector.score(
                    collector.Item(
                        title=title,
                        url=f"https://example.test/generic-capability-{index}",
                        source="Synthetic News",
                        published="2026-07-12T12:00:00+00:00",
                        summary="The report concerns people, rules, and everyday behavior.",
                    )
                )
                self.assertNotIn("ai-agents", result["areas"])
                self.assertEqual(result["action"], "Skip")

    def test_ai_product_described_as_an_agent_is_an_agent_topic(self) -> None:
        collector = load_collector()
        item = collector.Item(
            title="ChatGPT is now a partner for your most ambitious work",
            url="https://openai.com/example/chatgpt-work",
            source="OpenAI News",
            published="2026-07-12T12:00:00+00:00",
            summary=(
                "ChatGPT Work is an agent that can take action across your apps and "
                "files, stay with a project for hours, and turn a goal into finished work."
            ),
        )

        result = collector.score(item)

        self.assertIn("ai-agents", result["areas"])
        self.assertEqual(result["action"], "Read")

    def test_bare_human_agents_stay_ambiguous_when_ai_is_mentioned_elsewhere(self) -> None:
        collector = load_collector()
        cases = [
            "FBI agents adopt AI tools for translation",
            "Insurance agents use AI tools when comparing policies",
            "Literary agents discuss AI trends at a publishing conference",
        ]

        for index, title in enumerate(cases):
            with self.subTest(title=title):
                result = collector.score(
                    collector.Item(
                        title=title,
                        url=f"https://example.test/human-agents-{index}",
                        source="Synthetic News",
                        published="2026-07-12T12:00:00+00:00",
                        summary="The people remain responsible for the professional work.",
                    )
                )
                self.assertNotIn("ai-agents", result["areas"])
                self.assertEqual(result["action"], "Skip")

    def test_common_ai_agent_phrasings_are_classified_as_agent_topics(self) -> None:
        collector = load_collector()
        cases = [
            collector.Item(
                title="Autonomous agents can now browse the web",
                url="https://example.test/autonomous-agents",
                source="Synthetic News",
                published="2026-07-12T12:00:00+00:00",
                summary="The software completes tasks for users.",
            ),
            collector.Item(
                title="AI-powered agent helps developers",
                url="https://example.test/ai-powered-agent",
                source="Synthetic News",
                published="2026-07-12T12:00:00+00:00",
                summary="The assistant reviews code and proposes changes.",
            ),
            collector.Item(
                title="Better tools made Copilot code review worse",
                url="https://github.blog/example-agent-workflows",
                source="GitHub Blog",
                published="2026-07-12T12:00:00+00:00",
                summary="Unix-style code exploration tools reshaped agent workflows around pull request evidence.",
            ),
        ]

        for item in cases:
            with self.subTest(title=item.title):
                result = collector.score(item)
                self.assertIn("ai-agents", result["areas"])

    def test_human_agent_roles_are_not_promoted_by_ai_capability_words(self) -> None:
        collector = load_collector()
        cases = [
            collector.Item(
                title="Federal agents face a computer use audit",
                url="https://example.test/federal-computer-use",
                source="The Verge",
                published="2026-07-12T12:00:00+00:00",
                summary="The report concerns government enforcement procedures.",
            ),
            collector.Item(
                title="Real estate agents adopt AI tools",
                url="https://example.test/real-estate-ai-tools",
                source="Synthetic News",
                published="2026-07-12T12:00:00+00:00",
                summary="The people use translation software while preparing listings.",
            ),
        ]

        for item in cases:
            with self.subTest(title=item.title):
                result = collector.score(item)
                self.assertNotIn("ai-agents", result["areas"])
                self.assertEqual(result["action"], "Skip")

    def test_agent_topic_requires_ai_context(self) -> None:
        collector = load_collector()
        civic_item = collector.Item(
            title="ICE are heavily armed killers. They’re also huge losers",
            url="https://www.theverge.com/policy/964302/ice-donald-trump-killings",
            source="The Verge",
            published="2026-07-11T09:00:00-04:00",
            summary=(
                "Donald Trump's Homeland Security regime has been at the center of two "
                "critical stories in the past two weeks. In the first, federal agents "
                "shot and killed a man and quickly got to work justifying the use of "
                "force under the flimsiest of pretenses."
            ),
        )
        ai_item = collector.Item(
            title="OpenAI launches an autonomous coding agent with tool use",
            url="https://example.test/coding-agent",
            source="OpenAI News",
            published="2026-07-12T12:00:00+00:00",
            summary="The software agent uses an AI model to complete developer tasks.",
        )

        civic_score = collector.score(civic_item)
        ai_score = collector.score(ai_item)

        self.assertNotIn("ai-agents", civic_score["areas"])
        self.assertEqual(civic_score["action"], "Skip")
        self.assertIn("ai-agents", ai_score["areas"])
        self.assertIn(ai_score["action"], {"Read", "Watch"})

    def test_source_name_does_not_create_a_topic_match(self) -> None:
        collector = load_collector()
        neutral = collector.Item(
            title="Workplace notice for the coming week",
            url="https://example.test/neutral-notice",
            source="OpenAI News",
            published="2026-07-12T12:00:00+00:00",
            summary="The office cafeteria will use adjusted opening hours.",
        )

        result = collector.score(neutral)

        self.assertEqual(result["areas"], [])
        self.assertEqual(result["action"], "Skip")


class TechNewsIngestContract(unittest.TestCase):
    def test_structurally_corrupt_previous_snapshot_fails_before_collection(self) -> None:
        invalid_snapshots = [
            {"total": True, "items": []},
            {"total": 2, "items": [{"id": "only-one"}]},
            {"total": 1, "items": ["not-an-object"]},
            {"total": 1, "items": [{"id": "missing-public-fields"}]},
        ]
        for payload in invalid_snapshots:
            with self.subTest(payload=payload):
                collector = load_collector()
                with tempfile.TemporaryDirectory() as tmp:
                    output = Path(tmp) / "tech-news" / "data.json"
                    output.parent.mkdir()
                    previous = (json.dumps(payload) + "\n").encode()
                    output.write_bytes(previous)
                    collector.OUT = output
                    collection_called = False

                    def unexpected_collect(limit: int):
                        nonlocal collection_called
                        collection_called = True
                        return [], {}

                    collector.collect = unexpected_collect
                    stderr = io.StringIO()
                    with patch.object(sys, "argv", ["collect-tech-news-data.py", "--no-publish"]):
                        with redirect_stderr(stderr):
                            result = collector.main()

                    self.assertNotEqual(result, 0)
                    self.assertFalse(collection_called)
                    self.assertEqual(output.read_bytes(), previous)
                    self.assertIn("previous snapshot invalid", stderr.getvalue().lower())

    def test_successful_publish_targets_main_and_reads_remote_sha_back(self) -> None:
        collector = load_collector()
        calls: list[list[str]] = []
        expected_sha = "a" * 40

        def fake_run(cmd: list[str], **kwargs):
            calls.append(cmd)
            if cmd[:3] == ["git", "branch", "--show-current"]:
                return subprocess.CompletedProcess(cmd, 0, "main\n")
            if cmd == ["git", "status", "--porcelain"]:
                return subprocess.CompletedProcess(cmd, 0, " M tech-news/data.json\n")
            if cmd[:3] == ["git", "status", "--porcelain"]:
                return subprocess.CompletedProcess(cmd, 0, " M tech-news/data.json\n")
            if cmd[:2] == ["git", "fetch"]:
                return subprocess.CompletedProcess(cmd, 0, "")
            if cmd[:2] == ["git", "rev-list"]:
                return subprocess.CompletedProcess(cmd, 0, "0\t0\n")
            if cmd[:2] in (["git", "add"], ["git", "commit"], ["git", "push"]):
                return subprocess.CompletedProcess(cmd, 0, "synthetic success")
            if cmd[:2] == ["git", "rev-parse"]:
                return subprocess.CompletedProcess(cmd, 0, expected_sha + "\n")
            if cmd[:2] == ["git", "ls-remote"]:
                return subprocess.CompletedProcess(
                    cmd,
                    0,
                    f"{expected_sha}\trefs/heads/main\n",
                )
            raise AssertionError(f"unexpected command: {cmd}")

        collector.run = fake_run

        result = collector.publish_if_changed()

        self.assertEqual(result.state, "published")
        self.assertIn(
            ["git", "push", "--porcelain", "origin", "HEAD:main"],
            calls,
        )
        self.assertIn(
            ["git", "ls-remote", "--heads", "origin", "refs/heads/main"],
            calls,
        )

    def test_publish_rejects_non_main_branch_and_dirty_generator(self) -> None:
        for scenario in ("feature-branch", "dirty-generator"):
            with self.subTest(scenario=scenario):
                collector = load_collector()
                calls: list[list[str]] = []

                def fake_run(cmd: list[str], **kwargs):
                    calls.append(cmd)
                    if cmd[:3] == ["git", "branch", "--show-current"]:
                        branch = "feature/news\n" if scenario == "feature-branch" else "main\n"
                        return subprocess.CompletedProcess(cmd, 0, branch)
                    if cmd == ["git", "status", "--porcelain"]:
                        status = " M tech-news/data.json\n"
                        if scenario == "dirty-generator":
                            status += " M scripts/collect-tech-news-data.py\n"
                        return subprocess.CompletedProcess(cmd, 0, status)
                    if cmd[:3] == ["git", "status", "--porcelain"]:
                        return subprocess.CompletedProcess(cmd, 0, " M tech-news/data.json\n")
                    if cmd[:2] in (["git", "add"], ["git", "commit"], ["git", "push"]):
                        return subprocess.CompletedProcess(cmd, 0, "synthetic success")
                    raise AssertionError(f"unexpected command: {cmd}")

                collector.run = fake_run

                result = collector.publish_if_changed()

                self.assertEqual(result.state, "failed")
                self.assertFalse(
                    any(cmd[1] in {"add", "commit", "push"} for cmd in calls),
                    calls,
                )

    def test_retention_never_crowds_all_fresh_items_out_of_the_snapshot(self) -> None:
        collector = load_collector()
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "tech-news" / "data.json"
            output.parent.mkdir()
            previous_items = [
                {
                    "id": f"retained-{index}",
                    "title": f"Retained developer item {index}",
                    "url": f"https://example.test/retained-{index}",
                    "source": "Synthetic Failed",
                    "published": "2026-07-11T12:00:00+00:00",
                    "summary": "A previously collected developer tool release.",
                }
                for index in range(90)
            ]
            previous = (
                json.dumps({"total": len(previous_items), "items": previous_items}) + "\n"
            ).encode()
            output.write_bytes(previous)
            collector.OUT = output
            collector.FEEDS = {
                "Synthetic A": "https://example.test/a.xml",
                "Synthetic B": "https://example.test/b.xml",
                "Synthetic C": "https://example.test/c.xml",
                "Synthetic Failed": "https://example.test/failed.xml",
            }
            fresh_items = [
                {
                    "id": f"fresh-{index}",
                    "title": f"Fresh developer item {index}",
                    "url": f"https://example.test/fresh-{index}",
                    "source": "Synthetic A",
                    "published": "2026-07-12T12:00:00+00:00",
                    "summary": "A fresh developer tool release.",
                    "areas": ["developer-tools"],
                    "matchedKeywords": {"developer-tools": ["developer"]},
                    "scores": {"relevance": 2, "leverage": 1, "novelty": 4, "urgency": 2, "risk": 0},
                    "priority": 72,
                    "action": "Watch",
                    "actionDetail": "Synthetic fixture",
                }
                for index in range(45)
            ]
            collector.collect = lambda limit: (
                fresh_items[:limit],
                {"Synthetic Failed": "synthetic source outage"},
            )
            stderr = io.StringIO()

            with patch.object(sys, "argv", ["collect-tech-news-data.py", "--no-publish"]):
                with redirect_stderr(stderr):
                    result = collector.main()

            self.assertNotEqual(result, 0)
            self.assertEqual(output.read_bytes(), previous)
            self.assertIn("fresh", stderr.getvalue().lower())

    def test_partial_outage_retains_last_known_good_items_from_failed_sources(self) -> None:
        collector = load_collector()
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "tech-news" / "data.json"
            output.parent.mkdir()
            previous_items = [
                {
                    "id": "failed-source-lkg",
                    "title": "Federal agents publish a field report",
                    "url": "https://example.test/failed-source-lkg",
                    "source": "Synthetic Failed",
                    "published": "2026-07-11T12:00:00+00:00",
                    "summary": "The report describes a government enforcement operation.",
                    "areas": ["ai-agents"],
                    "matchedKeywords": {"ai-agents": ["agents"]},
                    "scores": {"relevance": 2, "leverage": 1, "novelty": 2, "urgency": 2, "risk": 0},
                    "priority": 72,
                    "action": "Watch",
                    "actionDetail": "Stale classification",
                },
                *[
                    {
                        "id": f"previous-{index}",
                        "title": f"Previous developer release {index}",
                        "url": f"https://example.test/previous-{index}",
                        "source": "Synthetic A",
                        "published": "2026-07-11T12:00:00+00:00",
                        "summary": "A developer tool release.",
                    }
                    for index in range(9)
                ],
            ]
            output.write_text(
                json.dumps({"total": len(previous_items), "items": previous_items}) + "\n",
                encoding="utf-8",
            )
            collector.OUT = output
            collector.FEEDS = {
                "Synthetic A": "https://example.test/a.xml",
                "Synthetic B": "https://example.test/b.xml",
                "Synthetic C": "https://example.test/c.xml",
                "Synthetic Failed": "https://example.test/failed.xml",
            }
            fresh_items = [
                {
                    "id": f"fresh-{index}",
                    "title": f"Fresh developer item {index}",
                    "url": f"https://example.test/fresh-{index}",
                    "source": "Synthetic A",
                    "published": "2026-07-12T12:00:00+00:00",
                    "summary": "A fresh developer tool release.",
                    "areas": ["developer-tools"],
                    "matchedKeywords": {"developer-tools": ["developer"]},
                    "scores": {"relevance": 2, "leverage": 1, "novelty": 4, "urgency": 2, "risk": 0},
                    "priority": 72,
                    "action": "Watch",
                    "actionDetail": "Synthetic fixture",
                }
                for index in range(10)
            ]
            collector.collect = lambda limit: (
                fresh_items[:limit],
                {"Synthetic Failed": "synthetic source outage"},
            )

            with patch.object(sys, "argv", ["collect-tech-news-data.py", "--no-publish"]):
                result = collector.main()

            payload = json.loads(output.read_text(encoding="utf-8"))
            retained = {item["id"]: item for item in payload["items"]}
            self.assertEqual(result, 0)
            self.assertIn("failed-source-lkg", retained)
            self.assertEqual(retained["failed-source-lkg"]["areas"], [])
            self.assertEqual(retained["failed-source-lkg"]["action"], "Skip")
            self.assertEqual(payload["retainedSources"], ["Synthetic Failed"])

    def test_total_feed_outage_preserves_last_known_good_and_returns_nonzero(self) -> None:
        collector = load_collector()
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "tech-news" / "data.json"
            output.parent.mkdir()
            previous = (
                json.dumps(
                    {
                        "total": 1,
                        "items": [
                            {
                                "id": "last-known-good",
                                "title": "Last known good item",
                                "url": "https://example.test/last-known-good",
                                "source": "Synthetic A",
                            }
                        ],
                    }
                )
                + "\n"
            ).encode()
            output.write_bytes(previous)
            collector.OUT = output
            collector.FEEDS = {
                "Synthetic A": "https://example.test/a.xml",
                "Synthetic B": "https://example.test/b.xml",
            }

            def fail_fetch(url: str, timeout: int = 30) -> bytes:
                raise TimeoutError(f"synthetic outage for {url}")

            collector.http_get = fail_fetch
            stdout = io.StringIO()
            stderr = io.StringIO()
            with patch.object(sys, "argv", ["collect-tech-news-data.py", "--no-publish"]):
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    result = collector.main()

            self.assertNotEqual(result, 0)
            self.assertEqual(output.read_bytes(), previous)
            self.assertIn("source", stderr.getvalue().lower())

    def test_large_snapshot_drop_preserves_last_known_good(self) -> None:
        collector = load_collector()
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "tech-news" / "data.json"
            output.parent.mkdir()
            previous_items = [
                {
                    "id": f"previous-{index}",
                    "title": f"Previous item {index}",
                    "url": f"https://example.test/previous-{index}",
                    "source": "Synthetic A",
                }
                for index in range(90)
            ]
            previous = (
                json.dumps({"total": len(previous_items), "items": previous_items})
                + "\n"
            ).encode()
            output.write_bytes(previous)
            collector.OUT = output
            collector.FEEDS = {
                "Synthetic A": "https://example.test/a.xml",
                "Synthetic B": "https://example.test/b.xml",
                "Synthetic C": "https://example.test/c.xml",
            }
            rows = [
                {"id": f"item-{index}", "action": "Watch", "published": "", "priority": 72}
                for index in range(10)
            ]
            collector.collect = lambda limit: (rows[:limit], {})
            stderr = io.StringIO()
            with patch.object(sys, "argv", ["collect-tech-news-data.py", "--no-publish"]):
                with redirect_stderr(stderr):
                    result = collector.main()

            self.assertNotEqual(result, 0)
            self.assertEqual(output.read_bytes(), previous)
            self.assertIn("retention", stderr.getvalue().lower())

    def test_commit_and_push_failures_return_nonzero_even_when_quiet(self) -> None:
        for failing_step in ("commit", "push"):
            with self.subTest(failing_step=failing_step):
                collector = load_collector()
                with tempfile.TemporaryDirectory() as tmp:
                    collector.OUT = Path(tmp) / "tech-news" / "data.json"
                    collector.FEEDS = {
                        "Synthetic A": "https://example.test/a.xml",
                        "Synthetic B": "https://example.test/b.xml",
                        "Synthetic C": "https://example.test/c.xml",
                    }
                    items = [
                        {
                            "id": f"item-{index}",
                            "title": f"Synthetic item {index}",
                            "url": f"https://example.test/item-{index}",
                            "source": "Synthetic A",
                            "published": "2026-07-12T12:00:00+00:00",
                            "summary": "Synthetic public fixture.",
                            "areas": ["developer-tools"],
                            "matchedKeywords": {"developer-tools": ["developer"]},
                            "scores": {
                                "relevance": 2,
                                "leverage": 1,
                                "novelty": 2,
                                "urgency": 2,
                                "risk": 0,
                            },
                            "priority": 72,
                            "action": "Watch",
                            "actionDetail": "Synthetic fixture",
                        }
                        for index in range(10)
                    ]
                    collector.collect = lambda limit: (items[:limit], {})

                    calls: list[list[str]] = []

                    def fake_run(cmd: list[str], *, cwd: Path = collector.SITE_REPO):
                        calls.append(cmd)
                        if cmd[:3] == ["git", "branch", "--show-current"]:
                            return subprocess.CompletedProcess(cmd, 0, "main\n")
                        if cmd[:2] == ["git", "status"]:
                            return subprocess.CompletedProcess(cmd, 0, " M tech-news/data.json\n")
                        if cmd[:2] == ["git", "fetch"]:
                            return subprocess.CompletedProcess(cmd, 0, "")
                        if cmd[:2] == ["git", "rev-list"]:
                            return subprocess.CompletedProcess(cmd, 0, "0\t0\n")
                        if cmd[:2] == ["git", "add"]:
                            return subprocess.CompletedProcess(cmd, 0, "")
                        if cmd[:2] == ["git", "commit"]:
                            return subprocess.CompletedProcess(
                                cmd,
                                1 if failing_step == "commit" else 0,
                                "synthetic commit failure" if failing_step == "commit" else "synthetic commit ok",
                            )
                        if cmd[:2] == ["git", "rev-parse"]:
                            return subprocess.CompletedProcess(cmd, 0, "a" * 40 + "\n")
                        if cmd[:2] == ["git", "push"]:
                            return subprocess.CompletedProcess(cmd, 1, "synthetic push failure")
                        raise AssertionError(f"unexpected command: {cmd}")

                    collector.run = fake_run
                    stdout = io.StringIO()
                    stderr = io.StringIO()
                    with patch.object(sys, "argv", ["collect-tech-news-data.py", "--quiet"]):
                        with redirect_stdout(stdout), redirect_stderr(stderr):
                            result = collector.main()

                    self.assertNotEqual(result, 0)
                    self.assertIn("synthetic", stderr.getvalue())
                    if failing_step == "commit":
                        self.assertFalse(any(cmd[:2] == ["git", "push"] for cmd in calls))

    def test_atomic_write_failure_preserves_previous_snapshot_and_skips_publish(self) -> None:
        collector = load_collector()
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "tech-news" / "data.json"
            output.parent.mkdir()
            previous = (
                json.dumps(
                    {
                        "total": 1,
                        "items": [
                            {
                                "id": "last-known-good",
                                "title": "Last known good item",
                                "url": "https://example.test/last-known-good",
                                "source": "Synthetic A",
                            }
                        ],
                    }
                )
                + "\n"
            ).encode()
            output.write_bytes(previous)
            collector.OUT = output
            collector.FEEDS = {
                "Synthetic A": "https://example.test/a.xml",
                "Synthetic B": "https://example.test/b.xml",
                "Synthetic C": "https://example.test/c.xml",
            }
            items = [
                {
                    "id": f"item-{index}",
                    "title": f"Synthetic item {index}",
                    "url": f"https://example.test/item-{index}",
                    "source": "Synthetic A",
                    "published": "2026-07-12T12:00:00+00:00",
                    "summary": "Synthetic public fixture.",
                    "areas": ["developer-tools"],
                    "matchedKeywords": {"developer-tools": ["developer"]},
                    "scores": {"relevance": 2, "leverage": 1, "novelty": 2, "urgency": 2, "risk": 0},
                    "priority": 72,
                    "action": "Watch",
                    "actionDetail": "Synthetic fixture",
                }
                for index in range(10)
            ]
            collector.collect = lambda limit: (items[:limit], {})
            git_calls: list[list[str]] = []

            def record_clean_git(cmd: list[str], **kwargs):
                git_calls.append(cmd)
                return subprocess.CompletedProcess(cmd, 0, "")

            collector.run = record_clean_git
            stderr = io.StringIO()

            with patch.object(sys, "argv", ["collect-tech-news-data.py"]):
                with patch.object(collector.os, "replace", side_effect=OSError("synthetic replace failure")):
                    with redirect_stderr(stderr):
                        result = collector.main()

            self.assertNotEqual(result, 0)
            self.assertEqual(output.read_bytes(), previous)
            self.assertEqual(git_calls, [])
            self.assertEqual(list(output.parent.glob(".data.json.*.tmp")), [])
            self.assertIn("write", stderr.getvalue().lower())


if __name__ == "__main__":
    unittest.main()
