---
name: detail-design-reference
description: Use the bundled, point-in-time content archive of detail.design as a structured reference for interface craft, accessibility, motion, copywriting, optimization, and design decisions. Trigger when answering questions about Detail, its 126 English detail entries, its resources/about/support pages, or when applying those references to product/interface work.
---

# Detail.design reference

This skill contains a structured snapshot of the public English content of `https://detail.design`, captured on 2026-09-30.

## Source of truth

- `references/catalog.json` is the complete paginated catalog: 126 entries, including title, slug, categories, summary/excerpt, media, dates, SEO keywords, and source links.
- `references/entries/<slug>.json` is the complete public detail-content response for each catalog entry. Its `mdxSource` field is the authoritative article body; do not infer missing prose from the catalog excerpt.
- `references/site-pages.json` contains the normalized text and URL metadata for the home, resources, about, and support pages.
- `references/capture-manifest.json` records counts and the capture date for integrity checks.

## How to use the archive

1. Identify the user's intent: retrieve an exact entry, search by category/keyword, compare patterns, or apply a principle to a new interface.
2. Search `references/catalog.json` first by `slug`, `title`, `type`, `seo.keywords`, and `summary`.
3. When a result is relevant, open the matching `references/entries/<slug>.json` and use `mdxSource` for the complete body, plus `media` for visual/video evidence and `seo` for retrieval terms.
4. For site-level questions, use `references/site-pages.json`; do not treat external links listed there as part of Detail's own authored content.
5. Preserve attribution: distinguish Detail's editorial text from the credited original product, author, or external resource.
6. If the user asks for recommendations or implementation, synthesize the cited entries and clearly mark any new recommendation as an inference rather than quoting it as site content.

## Completeness guardrails

- The catalog is paginated through the public endpoint `/api/details?locale=en&page=N`; page zero is the homepage's first page. The captured catalog has 126 unique slugs.
- Every catalog slug must have a matching entry JSON. An empty `mdxSource` is valid when the live entry has no editor's note/body; use the catalog metadata and `references/capture-manifest.json` to distinguish that state from a missing response.
- The archive is a snapshot, not a live mirror. If freshness matters, re-check the live site and record the new capture date.
- Do not reproduce site code or bundled JavaScript. The archive stores public content data and media URLs only.

## Retrieval hints

For large files, use targeted search rather than loading the entire archive. Useful patterns include:

- `"slug":"..."`
- `"type":["accessibility"]`
- `"seo":{"keywords"`
- `"mdxSource"`

## 中文使用提示

本 Skill 的归档原文为英文。用中文提问时，先用 `catalog.json` 按标题、类别、关键词和摘要定位，再读取匹配条目的完整 `mdxSource`；中文总结应保留英文来源链接，并区分原文依据与 Agent 的推断。不要只凭摘要声称读过完整文章。
