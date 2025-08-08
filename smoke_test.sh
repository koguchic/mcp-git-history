#!/usr/bin/env zsh
set -e

# Smoke test for mcp-git-history using uv only
# Ensures uv uses a working interpreter

SCRIPT_DIR=${0:a:h}
cd "$SCRIPT_DIR"

# Show uv info
echo "Using uv: $(uv --version 2>/dev/null || echo 'uv not found (please install uv)')"

# 1) Install the project and deps into a uv-managed environment
uv pip install -e .

# 2) Run smoke checks via a short Python harness with timing & summary
uv run python - << 'EOF'
import asyncio
import time
from mcp_git_history.server import GitHistoryServer

REPO = "/Users/koguchi/Coding/mcp/llama.cpp"

async def run_test(name, func, args):
    start = time.perf_counter()
    err = None
    text = None
    try:
        res = await func(args)
        text = res[0].text if res else "<no result>"
    except Exception as e:
        err = str(e)
    duration = time.perf_counter() - start
    return name, err is None, duration, text, err

async def main():
    server = GitHistoryServer()
    tests = [
        ("get_commit_summary", server._get_commit_summary, {"repo_path": REPO, "limit": 5}),
        ("analyze_file_history", server._analyze_file_history, {"repo_path": REPO, "file_path": "README.md", "limit": 5}),
        ("get_author_stats", server._get_author_stats, {"repo_path": REPO, "since": "2025-01-01"}),
        ("find_hotspots", server._find_hotspots, {"repo_path": REPO, "since": "2025-01-01", "limit": 5}),
        ("get_commits_by_timeframe", server._get_commits_by_timeframe, {"repo_path": REPO, "since": "2025-01-01", "until": "2025-08-07"}),
        ("get_churn_stats", server._get_churn_stats, {"repo_path": REPO, "since": "2025-01-01", "until": "2025-08-07", "path": "src", "top_files": 5}),
    ]

    results = []  # (name, ok, duration, err)

    for name, func, args in tests:
        print(f"=== {name} ===")
        n, ok, dur, text, err = await run_test(name, func, args)
        if ok:
            print(text[:800])
            print()
        else:
            print(f"Error in {name}: {err}\n")
        results.append((n, ok, dur, err))

    # Summary
    total = len(results)
    passed = sum(1 for _, ok, _, _ in results if ok)
    failed_names = [n for n, ok, _, _ in results if not ok]

    print("=== Summary ===")
    for n, ok, dur, _ in results:
        status = "PASS" if ok else "FAIL"
        print(f"- {n}: {status} in {dur:.2f}s")

    if results:
        slowest = max(results, key=lambda t: t[2])
        print(f"Slowest: {slowest[0]} ({slowest[2]:.2f}s)")

    if passed == total:
        print(f"All {total} functions passed correctly.")
    else:
        print(f"{passed}/{total} functions passed. Failed: {', '.join(failed_names)}")
        raise SystemExit(1)

asyncio.run(main())
EOF
