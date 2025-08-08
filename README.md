# MCP Git History Analysis Server

A Model Context Protocol (MCP) server implementation in Python that provides Git History Analysis capabilities.

## Features

- 📊 **Commit Summaries**: Get recent commit activity summaries with statistics
- 📁 **File History Analysis**: Analyze commit history for specific files
- 👥 **Author Statistics**: Get contribution statistics by author
- 🔥 **Change Hotspots**: Identify files with the most changes
- 📅 **Time-based Queries**: Get commits within specific timeframes

## MCP Tools Provided

- `get_commit_summary`: Get recent commit activity summary
- `analyze_file_history`: Analyze commit history for specific files
- `get_author_stats`: Get contribution statistics by author
- `find_hotspots`: Identify files with most changes
- `get_commits_by_timeframe`: Get commits within date range

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

### Example Requests

- "Which files had the most commits in the past month?"
- "List all commits touching main.cpp."
- "Show top 3 contributors by commit count."
- "Get commit summary for the last 20 commits"
- "Analyze the history of src/server.py"

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

## License

MIT License - see LICENSE file for details.
