"""Shared helpers for adtech-crosswalk ingest scripts."""

import csv
import json
import re
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from bs4 import BeautifulSoup

REPO_ROOT = Path(__file__).parent.parent.parent


def fetch_url(url: str, retries: int = 3) -> str:
    headers = {"User-Agent": "adtech-crosswalk-ingest/1.0"}
    last_err = None
    for attempt in range(retries):
        try:
            request = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(request, timeout=30) as response:
                return response.read().decode("utf-8")
        except Exception as exc:
            last_err = exc
            if attempt < retries - 1:
                time.sleep(2**attempt)
    raise RuntimeError(f"Failed to fetch {url} after {retries} attempts: {last_err}")


def parse_tsv(content: str) -> list[dict]:
    lines = content.splitlines()
    header_index = next(
        (
            index
            for index, line in enumerate(lines)
            if "Unique ID" in line or "IAB Code" in line
        ),
        0,
    )
    reader = csv.DictReader(lines[header_index:], delimiter="\t")
    tier_cols = [col for col in reader.fieldnames or [] if col.startswith("Tier ")]
    entries = []
    seen: dict[str, int] = {}

    for row in reader:
        uid = _first_nonempty(row, ["Unique ID", "IAB Code", "ID"])
        parent_id = _first_nonempty(row, ["Parent ID", "Parent"]) or None
        if parent_id is None and row.get("IAB Code"):
            parent_id = _infer_iab_parent_id(uid)
        path_parts = [row.get(col, "").strip() for col in tier_cols if row.get(col, "").strip()]
        name = _first_nonempty(row, ["Name", "IAB Category", "Category"])
        if not name and path_parts:
            name = path_parts[-1]
        if not name:
            name = _first_nonempty(row, ["Condensed Name (1st, 2nd, Last Tier)"])
        if not uid or not name:
            continue

        if uid in seen:
            seen[uid] += 1
            uid = f"{uid}_{seen[uid]}"
        else:
            seen[uid] = 1

        entries.append(
            {
                "id": uid,
                "parent_id": parent_id,
                "name": name,
                "full_path": " > ".join(path_parts) if path_parts else name,
            }
        )

    return entries


def _first_nonempty(row: dict, keys: list[str]) -> str:
    for key in keys:
        value = row.get(key, "")
        if value and value.strip():
            return value.strip()
    return ""


def _infer_iab_parent_id(uid: str) -> str | None:
    if "-" not in uid:
        return None
    return uid.rsplit("-", 1)[0]


def parse_markdown_table(markdown: str) -> list[dict]:
    rows = []
    headers: list[str] | None = None

    for line in markdown.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue

        cells = [cell.strip() for cell in line.split("|")[1:-1]]
        if not cells:
            continue
        if all(re.match(r"^[-: ]+$", cell) for cell in cells if cell):
            continue

        if headers is None:
            headers = cells
        else:
            rows.append(dict(zip(headers, cells)))

    return rows


def parse_html_table(html: str, caption_pattern: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    target_table = None
    fallback_table = None
    pattern = caption_pattern.lower()

    for table in soup.find_all("table"):
        preceding = table.find_previous(["h1", "h2", "h3", "h4", "h5", "caption"])
        if not preceding:
            continue
        caption = preceding.get_text(strip=True).lower()
        if caption == pattern:
            target_table = table
            break
        if pattern in caption and fallback_table is None:
            fallback_table = table

    target_table = target_table or fallback_table
    if target_table is None:
        raise ValueError(f"No table found matching caption pattern '{caption_pattern}'")

    header_row = target_table.find("tr")
    if header_row is None:
        raise ValueError(f"Table matching '{caption_pattern}' has no rows")

    headers = [cell.get_text(strip=True) for cell in header_row.find_all(["th", "td"])]
    rows = []
    for table_row in target_table.find_all("tr")[1:]:
        cells = [cell.get_text(strip=True) for cell in table_row.find_all(["td", "th"])]
        if cells and any(cells):
            rows.append(dict(zip(headers, cells)))

    return rows


def detect_changes(new_data: dict, path: Path) -> bool:
    if not path.exists():
        return True

    with path.open() as file:
        existing = json.load(file)

    def strip_generated_values(value: object) -> object:
        if isinstance(value, dict):
            return {
                key: strip_generated_values(child)
                for key, child in value.items()
                if key not in ("fetched_at", "generated_at", "snapshot_date")
            }
        if isinstance(value, list):
            return [strip_generated_values(item) for item in value]
        return value

    return strip_generated_values(new_data) != strip_generated_values(existing)


def write_taxonomy(metadata: dict, entries: list[dict], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w") as file:
        json.dump({"metadata": metadata, "entries": entries}, file, indent=2)


def write_mapping(metadata: dict, entries: list[dict], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w") as file:
        json.dump({"metadata": metadata, "entries": entries}, file, indent=2)


def register_taxonomy(index_path: Path, entry: dict) -> None:
    with index_path.open() as file:
        index = json.load(file)

    key = (entry["provider"], entry["taxonomy_type"], entry["version"])
    changed = False
    for i, taxonomy in enumerate(index["taxonomies"]):
        if (taxonomy["provider"], taxonomy["taxonomy_type"], taxonomy["version"]) == key:
            if taxonomy == entry:
                return
            index["taxonomies"][i] = entry
            changed = True
            break
    else:
        index["taxonomies"].append(entry)
        changed = True

    if changed:
        index["generated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        with index_path.open("w") as file:
            json.dump(index, file, indent=2)


def register_mapping(index_path: Path, entry: dict) -> None:
    with index_path.open() as file:
        index = json.load(file)

    key = (
        entry["source_provider"],
        entry["source_version"],
        entry["target_provider"],
        entry["target_version"],
        entry["taxonomy_type"],
    )
    changed = False
    for i, mapping in enumerate(index["mappings"]):
        if (
            mapping["source_provider"],
            mapping["source_version"],
            mapping["target_provider"],
            mapping["target_version"],
            mapping["taxonomy_type"],
        ) == key:
            if mapping == entry:
                return
            index["mappings"][i] = entry
            changed = True
            break
    else:
        index["mappings"].append(entry)
        changed = True

    if changed:
        index["generated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        with index_path.open("w") as file:
            json.dump(index, file, indent=2)
