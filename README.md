# MCP Git History Analysis Server

A Model Context Protocol (MCP) server implementation in Python that provides Git History Analysis capabilities.

## Features

- 📊 **Commit Summaries**: Get recent commit activity summaries with statistics
- 📁 **File History Analysis**: Analyze commit history for specific files
- 👥 **Author Statistics**: Get contribution statistics by author
- 🔥 **Change Hotspots**: Identify files with the most changes
- 📅 **Time-based Queries**: Get commits within specific timeframes

## MCP tools exposed to the LLM

The server exposes the following tools via MCP. All tools accept JSON arguments and return a textual summary suitable for LLM consumption.

- get_commit_summary
	- Purpose: Summary of recent commit activity.
	- Arguments:
		- repo_path (string, optional): Path to the git repository. Defaults to current working directory of the server process.
		- limit (integer, optional, default 10): Number of recent commits to analyze.

- analyze_file_history
	- Purpose: Analyze commit history for a single file.
	- Arguments:
		- repo_path (string, optional): Path to the git repository.
		- file_path (string, required): Path to the file to analyze (relative to repo root or absolute).
		- limit (integer, optional, default 20): Number of commits to analyze.

- get_author_stats
	- Purpose: Contribution statistics by author.
	- Arguments:
		- repo_path (string, optional): Path to the git repository.
		- since (string, optional, format YYYY-MM-DD): Start date filter.
		- until (string, optional, format YYYY-MM-DD): End date filter.

- find_hotspots
	- Purpose: Identify files with the most changes.
	- Arguments:
		- repo_path (string, optional): Path to the git repository.
		- since (string, optional, format YYYY-MM-DD): Only consider commits since this date.
		- limit (integer, optional, default 10): Number of top files to return.

- get_commits_by_timeframe
	- Purpose: List commits within a timeframe, optionally filtered by author.
	- Arguments:
		- repo_path (string, optional): Path to the git repository.
		- since (string, optional, format YYYY-MM-DD): Start date filter.
		- until (string, optional, format YYYY-MM-DD): End date filter.
		- author (string, optional): Author name or email to filter by.

- get_churn_stats
	- Purpose: Compute code churn (additions/deletions) over an optional timeframe and path.
	- Arguments:
		- repo_path (string, optional): Path to the git repository.
		- since (string, optional, format YYYY-MM-DD): Start date filter.
		- until (string, optional, format YYYY-MM-DD): End date filter.
		- path (string, optional): File or directory to scope churn.
		- top_files (integer, optional, default 10): Top files by churn to list.

### Typical question types (what to ask the LLM)

- Recent activity and trends
	- "What happened in the last 20 commits?"
	- "Who authored most commits this week?"
- File-specific history
	- "Analyze the history of src/server.py."
	- "How many lines changed in path/to/file over the last 20 commits?"
- Author contributions
	- "Show author contribution stats from 2025-06-01 until 2025-06-30."
	- "What’s my activity period this quarter?"
- Hotspots
	- "Which files changed the most since 2025-07-01?"
	- "Top 20 hotspots over the last month."
- Time-bounded queries
	- "List commits between 2025-06-01 and 2025-06-30 by alice@example.com."
 - "Show churn (additions/deletions) since 2025-07-01 under src/."

### Example tool calls (MCP call_tool requests)

The exact wire format depends on your MCP client, but the tool names and argument shapes are:

- get_commit_summary
	- arguments: { "repo_path"?: string, "limit"?: number }

- analyze_file_history
	- arguments: { "repo_path"?: string, "file_path": string, "limit"?: number }

- get_author_stats
	- arguments: { "repo_path"?: string, "since"?: "YYYY-MM-DD", "until"?: "YYYY-MM-DD" }

- find_hotspots
	- arguments: { "repo_path"?: string, "since"?: "YYYY-MM-DD", "limit"?: number }

- get_commits_by_timeframe
	- arguments: { "repo_path"?: string, "since"?: "YYYY-MM-DD", "until"?: "YYYY-MM-DD", "author"?: string }

- get_churn_stats
	- arguments: { "repo_path"?: string, "since"?: "YYYY-MM-DD", "until"?: "YYYY-MM-DD", "path"?: string, "top_files"?: number }

Returned content: a single text payload that includes a human-readable summary plus recent commit snippets when relevant.

## Installation

```bash
# Clone and install with uv
git clone <repository-url>
cd mcp-git-history
uv sync
```

## Usage

Run the MCP server:

```bash
uv run mcp-git-history
```

### Integrating with your MCP client

Add this server to your MCP client configuration. Example (pseudocode config):

```json
{
	"mcpServers": {
		"git-history": {
			"command": "uv",
			"args": ["run", "mcp-git-history"],
			"cwd": "/path/to/mcp-git-history"
		}
	}
}
```

Once configured, your LLM can call tools like `get_commit_summary` or `analyze_file_history` directly.

### Example Requests

- "Which files had the most commits in the past month?"
- "List all commits touching main.cpp."
- "Show top 3 contributors by commit count."
- "Get commit summary for the last 20 commits"
- "Analyze the history of src/server.py"

### Notes on behavior and output

- The server shells out to the Git CLI (read-only operations). Output is summarized for LLMs and may include recent commit logs in fenced blocks.
- If a file has no history, `analyze_file_history` returns a clear message.
- Dates must be in YYYY-MM-DD format when provided.
- `repo_path` is optional; if omitted, commands run in the server’s current working directory.

## Technology Stack

- Python 3.10+
- MCP Python SDK
- Git command-line interface
- JSON-RPC 2.0 protocol

## Development

```bash
# Install dependencies
uv sync

# Run the server
uv run mcp-git-history

# Run tests (when available)
uv run pytest
```

## Requirements

- Git must be installed and available in PATH
- Python 3.10 or higher
- Access to git repositories

## Security Considerations

- Validates all git repository paths
- Sanitizes command-line arguments
- Implements proper error handling
- Restricts access to authorized repositories only

## Limitations

- This server does not modify repositories; it only reads history.
- Output is textual; if you need structured metrics, extend the server to emit JSON objects alongside text.
- Large repositories can make some queries slower; consider providing a `since` filter to scope analysis.