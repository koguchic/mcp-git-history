# mcp-git-history – Roadmap & Ideas

This document lists enhancements that would make this MCP server more insightful and useful in day-to-day engineering.

## Near-term improvements

- Code churn tool (done): compute additions/deletions with optional timeframe and path filtering; list top files by churn.
- Output formats: add an option to return structured JSON alongside text (e.g., stats fields and arrays) for programmatic use.
- Performance: cache recent `git log` results by (repo_path, since, until, path) key to reduce repeated shell-outs.
- Robust path handling: resolve `repo_path` safely, support tilde (`~`) expansion, and normalize relative paths.
- Better binary handling: show counts for binary changes where possible or mark them explicitly.

## Analysis tools to add

- Blame summary: summarize `git blame` by author for a file or directory.
- PR/merge analysis: highlight merge commits, average time between merges, and frequency of merges.
- Tag/release intervals: commits and contributors between tags or releases, top changed files per release.
- Streaks & activity rhythm: author activity streaks, weekdays with highest commit volume.
- Ownership signals: approximate file/directory ownership based on contributions and recency.
- Refactor detector: find files with high churn and many authors (possible refactoring candidates).
- Outlier detection: unusually large commits or bursts of changes; detect risk areas.
- Bus factor signals: concentration of knowledge by file/directory.

## Tooling & UX

- Error surfaces: include suggested fixes in tool errors (e.g., missing git, invalid repo_path).
- Paging support: allow clients to request paginated commit lists for very large ranges.
- Configuration: allow per-user defaults (e.g., default `since` for timeframe queries).

## Long-term ideas

- Git providers integration: optional enrichment using GitHub/GitLab APIs for PRs and reviews (non-stdio tools).
- Language-aware diffs: summarize types of changes (tests/docs/code) by diff path patterns.
- Visualization hooks: emit lightweight JSON that downstream UIs can graph (churn over time, hotspots, authorship).

---

Contributions and suggestions are welcome. Open an issue with the idea and expected inputs/outputs so we can design the tool contract first.
