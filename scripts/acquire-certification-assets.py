#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "certifications"

MONTHS = {
    "jan.": "01", "feb.": "02", "mrt.": "03", "apr.": "04",
    "mei": "05", "jun.": "06", "jul.": "07", "aug.": "08",
    "sep.": "09", "okt.": "10", "nov.": "11", "dec.": "12",
}

SLUGS = {
    "Sales 2023 - SAP S/4HANA Cloud - Public Edition - SAP Certified Application Associate": "sap-s4hana-cloud-public-edition-sales-2023",
    "SAP Analytics Cloud - SAP Certified Application Associate": "sap-analytics-cloud",
    "Rapid Developer": "mendix-rapid-developer",
    "Excel Specialist 2013": "microsoft-excel-specialist-2013",
}

VAULT_ASSETS = {
    "data-transformation-in-alteryx": ("48e9aa0310535937f4ff2b457d67997e280622e5443c2b42f7c61db17aae5cc1", "pdf", "application/pdf"),
    "data-preparation-in-alteryx": ("26b425efdd2ee60d7c9152f3166ed4c8c0e43570838657cb206974fd86fedf78", "pdf", "application/pdf"),
    "introduction-to-alteryx": ("a951b0c6555878c49b516f3cc57e34ae775321b6c6ff79bc827cb07560741ed1", "pdf", "application/pdf"),
    "intermediate-python": ("e9f14214f50fb89e35b1e8281f8b06fb9e6807149e47c5c5dcd7ed0131df35ad", "pdf", "application/pdf"),
    "introduction-to-python": ("855af0e5dbc1959d007e93bc654fe0faf03646c003eeae06cff468ed798eafd0", "png", "image/png"),
    "okr-basics": ("a821e49ecb9bbaf9292fd844b73c215372996a34be1a21443ef96c4a2af23762", "pdf", "application/pdf"),
    "foundations-of-project-management": ("2acd7ac0e6d580683f3da6185746e0f46797ee70b24dbd96b4068a2289f02015", "pdf", "application/pdf"),
    "new-employee-business-partner-model-in-sap-s-4hana": ("2680660dcca98df4a755a95862161d1939fd0c224b6e44a7dff7e38c8ef40063", "pdf", "application/pdf"),
    "intermediate-sql": ("7e3c6005cabda8b1923cc5982e0a717d40e2172ca9d5a9b7ce56eb52eec1bb06", "pdf", "application/pdf"),
    "building-tomorrows-erp-with-sap-s-4hana": ("dd9febc8198b82e2276bac2ff4cec77975bd9c20682bfd4b3d264e4a98626daf", "pdf", "application/pdf"),
    "guide-your-sap-s-4hana-project-to-success": ("ee4cf6012a06f7e8bb7fe02f78308cb503a3c4501cfd7e9e185d6b7421c18a9b", "pdf", "application/pdf"),
    "information-security-management-in-a-nutshell": ("e6324247ebb471636f6aa963b68794411717b8eb7bea17216968e9e6b9233f48", "pdf", "application/pdf"),
    "introduction-to-sql": ("734a469f2448b17e5c3ff0ea62b8d4a5c138d8445effe55df1e001d28d59a1c8", "pdf", "application/pdf"),
    "introduction-to-statistics": ("d775c9338bcf36b87830fcb897d604b7324d48cd3bdc311344b1af78a6057237", "pdf", "application/pdf"),
    "understanding-data-visualization": ("f447ea9f35082e6dc247e7201bd4e63336b26bb7a00000e8c14f94b26e507522", "pdf", "application/pdf"),
    "understanding-data-topics": ("ae9a6f6e145431a05445e7a5771df9ac39ae656499e47511605cbcdbb0cebe8a", "pdf", "application/pdf"),
    "understanding-cloud-computing": ("e68de8053d3e624d22eb224f68ae83768003fd694341297bc69a1e048d1022cf", "pdf", "application/pdf"),
    "understanding-machine-learning": ("852171c14c9b814d6800adf7a68600d9bdf20bea967a37c4029454a931cf1a5f", "pdf", "application/pdf"),
    "understanding-data-engineering": ("1920a74a8304016565fa626d3ff0b8c55d4c454bc5e50f769370777228111096", "pdf", "application/pdf"),
    "understanding-data-science": ("e49e9419d857c1ce599fc9fbe774e46318171ff775b42102045628e132bdb8b5", "pdf", "application/pdf"),
    "innovation-award-2022": ("6d17d5e7f521119f0994cd5f56cf638bb29f5311931bdcc01b9eedc0d178ff6a", "pdf", "application/pdf"),
    "data-science-methodology": ("44e757f6e0bf7302e0c2b44a1ef52decee91facf60c09e7fb3e499ba80670a20", "png", "image/png"),
    "mendix-rapid-developer": ("4ebf98e1a964cfac4bf1a3788920e0051caa104064b9d57517ece0a3108d4760", "pdf", "application/pdf"),
    "nederlands-b2": ("4dfc29d2b769332a76a1e35a90be98cd65749b32631a56cc95588154ebdd0542", "pdf", "application/pdf"),
    "microsoft-excel-specialist-2013": ("e71cff5725486b315782e02ea7a96d480639c3e24e66392fc8f38867a24ba9da", "png", "image/png"),
}

REMOTE_ASSETS = {
    "sap-s4hana-cloud-public-edition-sales-2023": ("https://images.credly.com/images/16c321da-79bc-4fd4-b932-e2c7f174bf66/linkedin_thumb_image.png", "png", "image/png"),
    "sap-analytics-cloud": ("https://images.credly.com/images/e576bed5-1c89-41a0-88d1-cd21d6df479b/linkedin_thumb_image.png", "png", "image/png"),
    "python-for-data-science-ai-and-development": ("https://s3.amazonaws.com/coursera_assets/meta_images/generated/CERTIFICATE_LANDING_PAGE/CERTIFICATE_LANDING_PAGE~3EC8T69C5PUE/CERTIFICATE_LANDING_PAGE~3EC8T69C5PUE.jpeg", "jpg", "image/jpeg"),
    "data-science-orientation": ("https://s3.amazonaws.com/coursera_assets/meta_images/generated/CERTIFICATE_LANDING_PAGE/CERTIFICATE_LANDING_PAGE~C5YED6T8KH5F/CERTIFICATE_LANDING_PAGE~C5YED6T8KH5F.jpeg", "jpg", "image/jpeg"),
    "technical-support-fundamentals": ("https://s3.amazonaws.com/coursera_assets/meta_images/generated/CERTIFICATE_LANDING_PAGE/CERTIFICATE_LANDING_PAGE~ZCRJR53HXCWN/CERTIFICATE_LANDING_PAGE~ZCRJR53HXCWN.jpeg", "jpg", "image/jpeg"),
}


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    value = value.replace("&", " and ").replace("S/4HANA", "S 4HANA")
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def parse_note(path: Path) -> list[dict[str, str]]:
    content = path.read_text(encoding="utf-8")
    section = content.split("### Certificaten", 1)[1].split("```", 1)[1].split("```", 1)[0]
    credentials = []
    for block in re.split(r"\n---\n", section):
        if "Afgegeven op " not in block:
            continue
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        issue_index = next(i for i, line in enumerate(lines) if line.startswith("Afgegeven op "))
        labels = []
        for line in lines[:issue_index]:
            if line in {"[", "]", "Licenties en certificaten"} or line.startswith(("![", "](", "[](", "[http", "http")):
                continue
            labels.append(line)
        title, issuer = labels[-2:]
        month, year = lines[issue_index].removeprefix("Afgegeven op ").split()
        credential_id = ""
        for line in lines[issue_index + 1:]:
            if line.startswith("Referentienummer "):
                credential_id = line.removeprefix("Referentienummer ").strip()
        link_match = re.search(r"\[Referentie weergeven\]\(([^)]+)\)", block)
        verification_url = ""
        if link_match:
            outer = link_match.group(1)
            verification_url = urllib.parse.unquote(urllib.parse.parse_qs(urllib.parse.urlparse(outer).query).get("url", [outer])[0])
        credentials.append({
            "slug": SLUGS.get(title, slugify(title)),
            "title": title,
            "issuer": issuer,
            "issued": f"{year}-{MONTHS[month]}",
            "credential_id": credential_id,
            "verification_url": verification_url,
            "category": "SAP" if issuer == "SAP" else "Data and automation" if issuer in {"DataCamp", "IBM"} else "Professional practice" if issuer in {"Aiden Academy", "Workpath", "Google Career Certificates"} else "Foundations",
        })
    return sorted(credentials, key=lambda item: item["issued"], reverse=True)


def assert_signature(path: Path, mime_type: str) -> None:
    prefix = path.read_bytes()[:8]
    expected = {
        "application/pdf": b"%PDF-",
        "image/png": b"\x89PNG\r\n\x1a\n",
        "image/jpeg": b"\xff\xd8\xff",
    }[mime_type]
    if not prefix.startswith(expected):
        raise ValueError(f"Unexpected bytes for {path.name}: expected {mime_type}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--note", type=Path, required=True)
    parser.add_argument("--vault-runtime", type=Path, required=True)
    args = parser.parse_args()

    credentials = parse_note(args.note)
    if len(credentials) != 36:
        raise ValueError(f"Expected 36 credentials, found {len(credentials)}")

    assets_dir = OUTPUT / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    for item in credentials:
        slug = item["slug"]
        if slug in VAULT_ASSETS:
            source_sha, extension, mime_type = VAULT_ASSETS[slug]
            source = args.vault_runtime / "blobs" / "sha256" / source_sha[:2] / source_sha
            if not source.is_file() or hashlib.sha256(source.read_bytes()).hexdigest() != source_sha:
                raise ValueError(f"Vault CAS verification failed for {slug}")
            target = assets_dir / f"{slug}.{extension}"
            shutil.copyfile(source, target)
            provenance = "vault_cas"
            provenance_ref = f"blob://sha256/{source_sha}"
        elif slug in REMOTE_ASSETS:
            source_url, extension, mime_type = REMOTE_ASSETS[slug]
            target = assets_dir / f"{slug}.{extension}"
            request = urllib.request.Request(source_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(request, timeout=30) as response, target.open("wb") as output:
                shutil.copyfileobj(response, output)
            provenance = "official_verification_page"
            provenance_ref = source_url
        else:
            item["artifact"] = {
                "status": "source_unavailable",
                "reason": "The former StudyTube verification URL now requires authentication; no original file is present in the active vault.",
            }
            continue

        assert_signature(target, mime_type)
        item["artifact"] = {
            "status": "hosted",
            "path": f"/certifications/assets/{target.name}",
            "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
            "mime_type": mime_type,
            "provenance": provenance,
            "provenance_ref": provenance_ref,
        }

    OUTPUT.mkdir(exist_ok=True)
    (OUTPUT / "data.json").write_text(json.dumps(credentials, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    hosted = sum(item["artifact"]["status"] == "hosted" for item in credentials)
    print(f"Catalogued {len(credentials)} credentials with {hosted} hosted proofs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
