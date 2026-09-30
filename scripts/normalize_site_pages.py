#!/usr/bin/env python3
import json
import re
from html.parser import HTMLParser
from pathlib import Path

class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "noscript"}:
            self.skip += 1
    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript"} and self.skip:
            self.skip -= 1
    def handle_data(self, data):
        if not self.skip:
            value = re.sub(r"\s+", " ", data).strip()
            if value:
                self.parts.append(value)

root = Path(__file__).resolve().parents[1]
pages = {}
for html in sorted((root / "references/site-pages").glob("*.html")):
    parser = Text()
    parser.feed(html.read_text(errors="ignore"))
    pages[html.stem] = {
        "url": "https://detail.design/" if html.stem == "home" else {
            "resource": "https://detail.design/resource",
            "about-detail": "https://detail.design/resource/about-detail",
            "support": "https://detail.design/support",
        }.get(html.stem, "https://detail.design/" + html.stem),
        "text": "\n".join(parser.parts),
    }
(root / "references/site-pages.json").write_text(json.dumps(pages, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"pages": len(pages), "names": sorted(pages)}, ensure_ascii=False))
