#!/usr/bin/env python3
"""Fail closed when public site output drifts outside reviewed boundaries."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Iterable


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://viggomeesters.com"


def slugify(value: str) -> str:
    value = value.lower().replace("/", "-")
    return re.sub(r"[^a-z0-9_-]+", "-", value).strip("-") or "skill"


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def public_html_files(root: Path) -> list[Path]:
    ignored = {".git", ".vercel", "node_modules"}
    return sorted(
        path
        for path in root.rglob("*.html")
        if not ignored.intersection(path.relative_to(root).parts)
    )


def public_text_files(root: Path, html_files: Iterable[Path]) -> list[Path]:
    files = set(html_files)
    for relative in (
        "skills/skills-data.json",
        "tech-news/data.json",
        "trendwatch/data.json",
        "sitemap.xml",
    ):
        path = root / relative
        if path.exists():
            files.add(path)
    reports = root / "reports"
    if reports.exists():
        for path in reports.rglob("*"):
            if path.is_file() and path.suffix.lower() in {".html", ".json", ".md", ".xml", ".txt"}:
                files.add(path)
    return sorted(files)


def normalized_words(text: str) -> list[str]:
    return re.findall(r"[^\W]+(?:['’-][^\W]+)*", text.casefold(), flags=re.UNICODE)


def ngram_hashes(words: list[str], width: int) -> set[str]:
    if width < 1:
        return set()
    return {
        hashlib.sha256(" ".join(words[index : index + width]).encode()).hexdigest()
        for index in range(0, len(words) - width + 1)
    }


def tree_bytes(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file()
    }


def load_skills_generator() -> object:
    generator_path = Path(__file__).with_name("generate-skills-pages.py")
    spec = importlib.util.spec_from_file_location("viggomeesters_skills_generator", generator_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load skills generator")
    generator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(generator)
    return generator


def expected_skills_tree(entries: list[dict[str, str]], generated_at: str) -> dict[str, bytes]:
    generator = load_skills_generator()
    generator.TODAY = generated_at
    with tempfile.TemporaryDirectory() as tmp:
        expected_root = Path(tmp) / "skills"
        generator.write_skills_tree(expected_root, entries)
        return tree_bytes(expected_root)


def check(root: Path, public_skills_path: Path, policy_path: Path) -> list[str]:
    errors: list[str] = []
    skill_policy = load_json(public_skills_path)
    boundary_policy = load_json(policy_path)
    if not isinstance(skill_policy, dict) or skill_policy.get("schema") != "viggomeesters.public-skills.v1":
        return ["public skills manifest has an invalid schema"]
    if not isinstance(boundary_policy, dict) or boundary_policy.get("schema") != "viggomeesters.public-boundary.v1":
        return ["public boundary policy has an invalid schema"]

    try:
        entries = load_skills_generator().load_public_allowlist(public_skills_path)
    except (OSError, ValueError, json.JSONDecodeError):
        return ["public skills manifest failed PII and proper-noun validation"]
    expected_entries = sorted(entries, key=lambda entry: (entry["category"], entry["name"]))
    allowed_names = {entry["name"] for entry in expected_entries}
    allowed_slugs = {slugify(name) for name in allowed_names}
    if "" in allowed_names or len(allowed_names) != len(entries) or len(allowed_slugs) != len(entries):
        errors.append("public skills manifest has empty, duplicate or slug-colliding names")

    sitemap_path = root / "sitemap.xml"
    sitemap = sitemap_path.read_text(encoding="utf-8") if sitemap_path.exists() else ""
    html_files = public_html_files(root)
    html_by_path = {path: path.read_text(errors="ignore") for path in html_files}
    text_files = public_text_files(root, html_files)
    auxiliary_text = {
        path: path.read_text(errors="ignore")
        for path in text_files
        if path not in html_by_path and path != sitemap_path
    }

    blocked_routes = boundary_policy.get("blocked_routes")
    if not isinstance(blocked_routes, list):
        errors.append("public boundary policy blocked_routes must be a list")
        blocked_routes = []
    for route in blocked_routes:
        if not isinstance(route, str) or not route.startswith("/") or not route.endswith("/"):
            errors.append("public boundary policy contains an invalid blocked route")
            continue
        route_index = root / route.strip("/") / "index.html"
        if route_index.exists():
            errors.append(f"blocked route is still published: {route}")
        if route_index.parent.exists():
            errors.append(f"blocked route directory still exists: {route}")
        if f"{BASE_URL}{route}" in sitemap:
            errors.append(f"blocked route remains in sitemap: {route}")
        href_pattern = re.compile(rf'href=["\']{re.escape(route)}(?:["\']|#)')
        for path, text in html_by_path.items():
            if href_pattern.search(text):
                errors.append(f"blocked route remains linked from {path.relative_to(root)}: {route}")
        for path, text in auxiliary_text.items():
            if route in text or f"{BASE_URL}{route}" in text:
                errors.append(f"blocked route remains in deployed text {path.relative_to(root)}: {route}")

    data_path = root / "skills" / "skills-data.json"
    registry_path = root / "skills" / "index.html"
    if not data_path.exists() or not registry_path.exists():
        errors.append("generated skills data or registry is missing")
    else:
        data = load_json(data_path)
        data_entries = data.get("skills", []) if isinstance(data, dict) else []
        data_names = {
            str(entry.get("name", "")) for entry in data_entries if isinstance(entry, dict)
        }
        if data_names != allowed_names:
            errors.append("skills-data names do not exactly match the public allowlist")
        generated_at = str(data.get("generated_at", "")) if isinstance(data, dict) else ""
        if (
            data_entries != expected_entries
            or not isinstance(data, dict)
            or data.get("count") != len(expected_entries)
            or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", generated_at)
        ):
            errors.append("skills-data metadata does not exactly match the reviewed manifest")
        detail_slugs = {
            child.name
            for child in (root / "skills").iterdir()
            if child.is_dir() and (child / "index.html").exists()
        }
        if detail_slugs != allowed_slugs:
            errors.append("skill detail directories do not exactly match the public allowlist")
        registry_slugs = set(
            re.findall(r'href="/skills/([^/]+)/"', registry_path.read_text(encoding="utf-8"))
        )
        if registry_slugs != allowed_slugs:
            errors.append("skills registry links do not exactly match the public allowlist")
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", generated_at):
            expected_tree = expected_skills_tree(expected_entries, generated_at)
            if tree_bytes(root / "skills") != expected_tree:
                errors.append("generated skill metadata and copy do not exactly match the reviewed manifest")

    hash_markers = boundary_policy.get("forbidden_text_hashes", [])
    if not isinstance(hash_markers, list):
        errors.append("public boundary policy forbidden_text_hashes must be a list")
        hash_markers = []
    for path in text_files:
        words = normalized_words(path.read_text(errors="ignore"))
        hashes_by_width: dict[int, set[str]] = {}
        for marker in hash_markers:
            if not isinstance(marker, dict):
                errors.append("public boundary policy contains an invalid hash marker")
                continue
            marker_id = str(marker.get("id", "invalid-marker"))
            try:
                width = int(marker.get("words", 0))
            except (TypeError, ValueError):
                width = 0
            expected = str(marker.get("sha256", ""))
            if width < 1 or not re.fullmatch(r"[a-f0-9]{64}", expected):
                errors.append(f"invalid forbidden text hash policy: {marker_id}")
                continue
            hashes = hashes_by_width.setdefault(width, ngram_hashes(words, width))
            if expected in hashes:
                errors.append(f"forbidden private marker {marker_id} found in {path.relative_to(root)}")
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--public-skills", type=Path)
    parser.add_argument("--policy", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    public_skills = args.public_skills or (root / "scripts" / "public-skills.json")
    policy = args.policy or (root / "scripts" / "public-boundary.json")
    try:
        errors = check(root, public_skills, policy)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Public boundary check could not run: {type(exc).__name__}", file=sys.stderr)
        return 2
    if errors:
        print(f"Public boundary check failed with {len(errors)} issue(s):", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Public boundary check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
