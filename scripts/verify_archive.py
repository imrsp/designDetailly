#!/usr/bin/env python3
"""Verify that the catalog and full entry payloads are complete and aligned."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1] / "detail-design-skill"
catalog = json.loads((root / "references/catalog.json").read_text())
items = catalog["items"]
slugs = [item["slug"] for item in items]
entry_dir = root / "references/entries"
missing = []
empty = []
for slug in slugs:
    path = entry_dir / f"{slug}.json"
    if not path.exists():
        missing.append(slug)
        continue
    payload = json.loads(path.read_text())
    if payload.get("mdxSource") is None or payload.get("mdxSource") == "":
        empty.append(slug)
duplicates = sorted({slug for slug in slugs if slugs.count(slug) > 1})
unexpected = sorted(path.stem for path in entry_dir.glob("*.json") if path.stem not in set(slugs))
result = {
    "catalog_count": len(items),
    "unique_slug_count": len(set(slugs)),
    "entry_file_count": len(list(entry_dir.glob("*.json"))),
    "missing_entries": missing,
    "empty_mdx_source": empty,
    "duplicate_slugs": duplicates,
    "unexpected_entry_files": unexpected,
        "empty_mdx_source_is_source_state": True,
    "complete": not (missing or duplicates or unexpected) and len(items) == len(set(slugs)),
}
print(json.dumps(result, ensure_ascii=False, indent=2))
if not result["complete"]:
    raise SystemExit(1)
