# Detail.design Reference Library

[中文](README.md) · English

## Source, scope, and attribution

Source: [detail.design](https://detail.design). The archive covers the public English catalog, detail content returned by the site's API, and the Home, Resources, About Detail, and Support pages. It does not include website code, private content, or local copies of media files; media URLs are retained as provided by the source. Content and rights remain with their respective authors and rights holders. This project is intended for research, retrieval, and design assistance. Preserve attribution and follow the source site's terms and applicable licenses.

This is a periodically refreshed snapshot, not a live mirror. See [`capture-manifest.json`](detail-design-skill/references/capture-manifest.json) for capture date, item count, and integrity notes. Contributions and issue reports are welcome.

**A searchable, source-aware design practice library for AI agents.** This project organizes the public English catalog, article content, and selected site pages from [detail.design](https://detail.design) into structured data and packages them as a ready-to-use Agent Skill.

> This is a content archive and retrieval skill—not website source code or a mirror. Ask your agent to cite the relevant entry and source URL when making design recommendations.

## What can your agent do?

After downloading or installing [`detail-design-skill/`](detail-design-skill/), try prompts like:

- “Use the `detail-design-reference` Skill to audit this settings screen for design consistency and accessibility. Rank findings by severity.”
- “Use the `detail-design-reference` Skill to review this onboarding flow. Suggest improvements to interaction, copy, and feedback states, citing supporting references.”
- “Use the `detail-design-reference` Skill to improve this mobile form, focusing on error messages, input ergonomics, and keyboard behavior.”
- “Find practices about empty states, loading states, and motion. Compare when each applies, then recommend an approach for my product.”
- “Review these design screenshots for hierarchy, alignment, information density, and interaction states. Separate archive-backed guidance from your own inferences.”
- “Search the archive for accessibility, microcopy, and performance guidance and turn it into an actionable design review checklist.”

Replace “settings screen / onboarding / screenshots” with your own product context. Image understanding depends on the agent and environment you use.

## Install and use

The Skill lives in [`detail-design-skill/`](detail-design-skill/). Copy or install that directory into the Skills location supported by your agent, then mention `detail-design-reference` in your prompt.

You can also provide the `detail-design-skill/` directory to any tool that supports local Skills or agent instructions. Installation paths vary by tool; follow your agent's Skills documentation.

## Data layout

```text
.
├── README.md                        # Default Chinese README
├── README.en.md                     # English README
├── scripts/                         # Refresh and verification scripts
│   ├── update_archive.py
│   └── verify_archive.py
└── detail-design-skill/             # Install/provide this directory to your agent
    ├── SKILL.md
    ├── agents/openai.yaml
    └── references/
        ├── catalog.json
        ├── entries/<slug>.json
        ├── site-pages.json
        └── capture-manifest.json
```

Article bodies are split into per-slug files so agents can retrieve only what they need instead of loading the whole archive into context. Search `detail-design-skill/references/catalog.json` first, then read the matching `detail-design-skill/references/entries/<slug>.json`. If the source returns an empty body for an entry, the archive preserves that source state rather than presenting an excerpt as the full article.

## Refresh the archive

Requires Python 3; no third-party Python packages are needed. Run manually:

```bash
python3 scripts/update_archive.py
```

The updater traverses the public catalog, fetches every detail response and selected site page, validates the results, and only then publishes the snapshot. Incomplete responses abort the refresh and leave the old archive intact. No content change means no commit. When content changes, the script creates an automated Git commit and pushes the current branch to its configured upstream. Before the first run, configure a Git remote, upstream, and working push credentials. If those are missing, the script reports the issue and keeps the verified local update; it does not roll back the content.

After initialization, configure your remote as needed:

```bash
git remote add origin <your GitHub repository URL>
git push -u origin main
```

