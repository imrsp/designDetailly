#!/usr/bin/env python3
"""Refresh the structured public-content snapshot from detail.design."""
from __future__ import annotations

import json
import re
import os
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE = "https://detail.design"
REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "detail-design-skill"
REFS = ROOT / "references"
PAGES = {
    "home": "/",
    "resource": "/resource",
    "about-detail": "/resource/about-detail",
    "support": "/support",
}


def get(url: str) -> bytes:
    error = None
    for attempt in range(5):
        try:
            req = Request(url, headers={"User-Agent": "detail-design-content-archive/1.0"})
            with urlopen(req, timeout=40) as response:
                if response.status != 200:
                    raise RuntimeError(f"HTTP {response.status}: {url}")
                return response.read()
        except (HTTPError, URLError, TimeoutError, RuntimeError) as exc:
            error = exc
            if attempt < 4:
                time.sleep(min(2 ** attempt, 12))
    raise RuntimeError(f"Could not fetch {url}: {error}")


def get_json(url: str):
    return json.loads(get(url).decode("utf-8"))


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "noscript", "svg"}:
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript", "svg"} and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip:
            text = re.sub(r"\s+", " ", data).strip()
            if text:
                self.parts.append(text)


def write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")



def update_skill_references(content: str, captured_at: str, count: int) -> str:
    content = re.sub(r"captured on `[^`]+`", f"captured on `{captured_at}`", content)
    content = re.sub(r"(complete paginated catalog: )\d+( entries)", rf"\g<1>{count}\2", content)
    content = re.sub(r"(catalog has )\d+( unique slugs)", rf"\g<1>{count}\2", content)
    return re.sub(r"(its )\d+( English detail entries)", rf"\g<1>{count}\2", content)


def push_if_changed() -> None:
    repo = REPO
    if not (repo / ".git").exists():
        print("Archive updated locally; no Git repository found, so no commit or push was attempted.")
        return

    def git(*args, check=True):
        return subprocess.run(
            ["git", *args], cwd=repo, text=True, capture_output=True, check=check
        )

    changed = git("status", "--porcelain", "--", "detail-design-skill").stdout.strip()
    if not changed:
        print("No archive changes detected; nothing to commit or push.")
        return
    git("add", "-A", "--", "detail-design-skill")
    staged = git("diff", "--cached", "--quiet", check=False)
    if staged.returncode == 0:
        print("No staged archive changes; nothing to commit or push.")
        return
    git("-c", "user.name=detail-design-archive[bot]", "-c",
        "user.email=detail-design-archive[bot]@users.noreply.github.com",
        "commit", "-m", "chore: refresh detail.design archive")
    branch = git("symbolic-ref", "--quiet", "--short", "HEAD", check=False)
    if branch.returncode or not branch.stdout.strip():
        print("Archive commit created, but HEAD is detached; configure a branch and upstream to push.")
        return
    upstream = git("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}", check=False)
    if upstream.returncode:
        print("Archive commit created locally; no upstream is configured, so push was skipped.")
        return
    pushed = git("push", check=False)
    if pushed.returncode:
        raise RuntimeError(f"Archive updated and committed, but git push failed: {pushed.stderr.strip()}")
    print(f"Pushed archive update to {upstream.stdout.strip()}.")


def main():
    today = datetime.now(timezone.utc).date().isoformat()
    pages = []
    catalog = None
    for number in range(1000):
        payload = get_json(f"{BASE}/api/details?{urlencode({'locale': 'en', 'page': number})}")
        if not isinstance(payload, dict) or not isinstance(payload.get("items"), list):
            raise RuntimeError(f"Unexpected catalog response on page {number}")
        if catalog is None:
            catalog = dict(payload)
            catalog["items"] = []
        pages.append(number)
        catalog["items"].extend(payload["items"])
        if not payload.get("hasMore"):
            break
        if not payload["items"]:
            raise RuntimeError(f"Catalog page {number} is empty but hasMore is true")
    else:
        raise RuntimeError("Catalog pagination exceeded safety limit")

    slugs = [item.get("slug") for item in catalog["items"]]
    if not slugs or any(not isinstance(s, str) or not s for s in slugs):
        raise RuntimeError("Catalog contains missing/invalid slugs")
    if len(slugs) != len(set(slugs)):
        raise RuntimeError("Catalog contains duplicate slugs; refusing to publish partial data")
    if isinstance(catalog.get("total"), int) and catalog["total"] != len(slugs):
        raise RuntimeError(f"Catalog says total={catalog['total']} but returned {len(slugs)}")

    with tempfile.TemporaryDirectory(prefix="detail-design-update-", dir=REFS) as tmp:
        staging = Path(tmp) / "entries"
        staging.mkdir()
        empty_bodies = []
        for i, slug in enumerate(slugs, 1):
            url = f"{BASE}/api/detail-content?{urlencode({'slug': slug, 'locale': 'en'})}"
            detail = get_json(url)
            if not isinstance(detail, dict) or detail.get("slug") != slug:
                raise RuntimeError(f"Detail response mismatch for {slug}")
            if "mdxSource" not in detail or detail["mdxSource"] is not None and not isinstance(detail["mdxSource"], str):
                raise RuntimeError(f"Detail body missing or malformed for {slug}")
            if detail["mdxSource"] is None:
                # Preserve an explicit source null; normalize it to empty text so
                # consumers and the verifier can consistently recognize no body.
                detail["mdxSource"] = ""
            if not detail["mdxSource"]:
                empty_bodies.append(slug)
            write_json(staging / f"{slug}.json", detail)
            if i % 20 == 0:
                print(f"Fetched {i}/{len(slugs)} detail payloads", flush=True)

        site_pages = {}
        for name, path in PAGES.items():
            html = get(f"{BASE}{path}").decode("utf-8", errors="replace")
            parser = TextExtractor()
            parser.feed(html)
            text = "\n".join(parser.parts)
            if not text:
                raise RuntimeError(f"Page had no extractable text: {path}")
            site_pages[name] = {"url": f"{BASE}{path}", "text": text}

        # Compare canonical data before publishing so unchanged refreshes stay clean.
        catalog_path = REFS / "catalog.json"
        pages_path = REFS / "site-pages.json"
        old_catalog = json.loads(catalog_path.read_text(encoding="utf-8")) if catalog_path.exists() else None
        old_pages = json.loads(pages_path.read_text(encoding="utf-8")) if pages_path.exists() else None
        old_entries = REFS / "entries"
        same_entries = old_entries.exists() and all(
            (old_entries / f"{slug}.json").exists()
            and json.loads((old_entries / f"{slug}.json").read_text(encoding="utf-8"))
            == json.loads((staging / f"{slug}.json").read_text(encoding="utf-8"))
            for slug in slugs
        ) and len(list(old_entries.glob("*.json"))) == len(slugs)
        unchanged = old_catalog == catalog and old_pages == site_pages and same_entries
        manifest_path = REFS / "capture-manifest.json"
        old_manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
        if unchanged:
            # Refresh every human-readable snapshot-date reference even when the
            # source content did not change; update metadata date only if stale.
            skill_path = ROOT / "SKILL.md"
            skill_text = skill_path.read_text(encoding="utf-8")
            skill_text = update_skill_references(skill_text, today, old_manifest.get("catalog_entries", len(slugs)))
            skill_path.write_text(skill_text, encoding="utf-8")
            if old_manifest.get("captured_at") != today:
                old_manifest["captured_at"] = today
                write_json(manifest_path, old_manifest)
            print("Source content is unchanged; archive data was preserved and freshness dates updated.")
            result = subprocess.run([sys.executable, str(ROOT / "scripts/verify_archive.py")], check=False)
            if result.returncode:
                raise RuntimeError("Archive verification failed after date refresh")
            push_if_changed()
            return

        # Publish only after every API response and page has passed validation.
        entries = REFS / "entries"
        backup = Path(tmp) / "entries-previous"
        if entries.exists():
            entries.rename(backup)
        try:
            staging.rename(entries)
        except Exception:
            if backup.exists() and not entries.exists():
                backup.rename(entries)
            raise
        write_json(REFS / "catalog.json", catalog)
        write_json(REFS / "site-pages.json", site_pages)
        write_json(REFS / "capture-manifest.json", {
            "source": BASE,
            "locale": "en",
            "captured_at": today,
            "catalog_endpoint": "/api/details?locale=en&page=N",
            "detail_endpoint": "/api/detail-content?slug={slug}&locale=en",
            "catalog_pages_fetched": pages,
            "catalog_entries": len(slugs),
            "full_detail_payloads": len(slugs),
            "empty_mdx_source": empty_bodies,
            "site_pages": list(site_pages),
            "completeness_note": "Every catalog page was traversed through hasMore=false; each unique slug has a validated full detail-content response. Empty mdxSource values reflect the source response.",
        })

    skill = ROOT / "SKILL.md"
    content = skill.read_text(encoding="utf-8")
    content = update_skill_references(content, today, len(slugs))
    skill.write_text(content, encoding="utf-8")

    result = subprocess.run([sys.executable, str(ROOT / "scripts/verify_archive.py")], check=False)
    if result.returncode:
        raise RuntimeError("Archive verification failed after refresh")
    print(f"Updated {len(slugs)} entries and {len(site_pages)} pages ({today}); empty source bodies: {len(empty_bodies)}")
    push_if_changed()


if __name__ == "__main__":
    main()
