#!/usr/bin/env python3
"""
Git History Analysis MCP Server

This server provides tools for analyzing git repository history, including:
- Commit summaries and statistics
- File change analysis and hotspots
- Author contribution statistics
- Time-based commit queries
"""

import asyncio
import subprocess
from typing import List, Optional

from mcp.server import InitializationOptions, NotificationOptions, Server
from mcp.types import Tool
from mcp import stdio_server
import mcp.types as types


class GitHistoryServer:
    """MCP Server for Git History Analysis"""
    
    def __init__(self):
        self.server = Server("git-history-analysis")
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Set up all the MCP handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            """List available tools"""
            return [
                Tool(
                    name="get_commit_summary",
                    description="Get a summary of recent commit activity in a git repository",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "repo_path": {
                                "type": "string",
                                "description": "Path to the git repository (defaults to current directory)"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Number of recent commits to analyze (default: 10)",
                                "default": 10
                            }
                        }
                    }
                ),
                Tool(
                    name="analyze_file_history",
                    description="Analyze commit history for specific files",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "repo_path": {
                                "type": "string",
                                "description": "Path to the git repository"
                            },
                            "file_path": {
                                "type": "string",
                                "description": "Path to the file to analyze"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Number of commits to analyze (default: 20)",
                                "default": 20
                            }
                        },
                        "required": ["file_path"]
                    }
                ),
                Tool(
                    name="get_author_stats",
                    description="Get contribution statistics by author",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "repo_path": {
                                "type": "string",
                                "description": "Path to the git repository"
                            },
                            "since": {
                                "type": "string",
                                "description": "Start date for analysis (YYYY-MM-DD format)"
                            },
                            "until": {
                                "type": "string",
                                "description": "End date for analysis (YYYY-MM-DD format)"
                            }
                        }
                    }
                ),
                Tool(
                    name="find_hotspots",
                    description="Identify files with the most changes (hotspots)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "repo_path": {
                                "type": "string",
                                "description": "Path to the git repository"
                            },
                            "since": {
                                "type": "string",
                                "description": "Start date for analysis (YYYY-MM-DD format)"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Number of top files to return (default: 10)",
                                "default": 10
                            }
                        }
                    }
                ),
                Tool(
                    name="get_commits_by_timeframe",
                    description="Get commits within a specific timeframe",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "repo_path": {
                                "type": "string",
                                "description": "Path to the git repository"
                            },
                            "since": {
                                "type": "string",
                                "description": "Start date (YYYY-MM-DD format)"
                            },
                            "until": {
                                "type": "string",
                                "description": "End date (YYYY-MM-DD format)"
                            },
                            "author": {
                                "type": "string",
                                "description": "Filter by author email or name"
                            }
                        }
                    }
                )
                ,
                Tool(
                    name="get_churn_stats",
                    description="Compute code churn (additions/deletions) over an optional timeframe and path",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "repo_path": {
                                "type": "string",
                                "description": "Path to the git repository"
                            },
                            "since": {
                                "type": "string",
                                "description": "Start date (YYYY-MM-DD format)"
                            },
                            "until": {
                                "type": "string",
                                "description": "End date (YYYY-MM-DD format)"
                            },
                            "path": {
                                "type": "string",
                                "description": "Optional file or directory path to scope churn"
                            },
                            "top_files": {
                                "type": "integer",
                                "description": "Number of top files by churn to include (default: 10)",
                                "default": 10
                            }
                        }
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
            """Handle tool calls"""
            
            if name == "get_commit_summary":
                return await self._get_commit_summary(arguments)
            elif name == "analyze_file_history":
                return await self._analyze_file_history(arguments)
            elif name == "get_author_stats":
                return await self._get_author_stats(arguments)
            elif name == "find_hotspots":
                return await self._find_hotspots(arguments)
            elif name == "get_commits_by_timeframe":
                return await self._get_commits_by_timeframe(arguments)
            elif name == "get_churn_stats":
                return await self._get_churn_stats(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")
    
    def _run_git_command(self, cmd: List[str], repo_path: Optional[str] = None) -> str:
        """Run a git command and return the output"""
        try:
            if repo_path:
                cmd = ["git", "-C", repo_path] + cmd[1:]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Git command failed: {e.stderr}")
        except FileNotFoundError:
            raise RuntimeError("Git is not installed or not in PATH")
    
    async def _get_commit_summary(self, arguments: dict) -> list[types.TextContent]:
        """Get recent commit summary"""
        repo_path = arguments.get("repo_path")
        limit = arguments.get("limit", 10)
        
        try:
            # Get recent commits
            cmd = ["git", "log", f"--max-count={limit}", "--oneline", "--decorate"]
            output = self._run_git_command(cmd, repo_path)
            
            # Get basic stats
            stats_cmd = ["git", "log", f"--max-count={limit}", "--pretty=format:%an|%ad", "--date=short"]
            stats_output = self._run_git_command(stats_cmd, repo_path)
            
            # Parse authors and dates
            authors = {}
            dates = set()
            for line in stats_output.strip().split('\n'):
                if '|' in line:
                    author, date = line.split('|', 1)
                    authors[author] = authors.get(author, 0) + 1
                    dates.add(date)
            
            summary = f"## Recent Commit Summary (Last {limit} commits)\n\n"
            summary += f"**Total commits analyzed:** {limit}\n"
            summary += f"**Date range:** {min(dates) if dates else 'N/A'} to {max(dates) if dates else 'N/A'}\n"
            summary += f"**Active authors:** {len(authors)}\n\n"
            
            if authors:
                summary += "**Top contributors:**\n"
                for author, count in sorted(authors.items(), key=lambda x: x[1], reverse=True)[:5]:
                    summary += f"- {author}: {count} commits\n"
                summary += "\n"
            
            summary += "**Recent commits:**\n```\n"
            summary += output
            summary += "```\n"
            
            return [types.TextContent(type="text", text=summary)]
            
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error getting commit summary: {str(e)}")]
    
    async def _analyze_file_history(self, arguments: dict) -> list[types.TextContent]:
        """Analyze commit history for a specific file"""
        repo_path = arguments.get("repo_path")
        file_path = arguments["file_path"]
        limit = arguments.get("limit", 20)
        
        try:
            # Get file commit history
            cmd = ["git", "log", f"--max-count={limit}", "--oneline", "--", file_path]
            commits_output = self._run_git_command(cmd, repo_path)
            
            if not commits_output.strip():
                return [types.TextContent(type="text", text=f"No commits found for file: {file_path}")]
            
            # Get detailed stats
            stats_cmd = ["git", "log", f"--max-count={limit}", "--pretty=format:%an|%ad|%s", "--date=short", "--", file_path]
            stats_output = self._run_git_command(stats_cmd, repo_path)
            
            # Get number of lines changed
            changes_cmd = ["git", "log", f"--max-count={limit}", "--numstat", "--pretty=format:", "--", file_path]
            changes_output = self._run_git_command(changes_cmd, repo_path)
            
            # Parse data
            commits = commits_output.strip().split('\n')
            total_commits = len([c for c in commits if c.strip()])
            
            authors = {}
            dates = set()
            total_additions = 0
            total_deletions = 0
            
            for line in stats_output.strip().split('\n'):
                if '|' in line:
                    parts = line.split('|', 2)
                    if len(parts) >= 2:
                        author, date = parts[0], parts[1]
                        authors[author] = authors.get(author, 0) + 1
                        dates.add(date)
            
            # Parse line changes
            for line in changes_output.strip().split('\n'):
                if line.strip() and '\t' in line:
                    parts = line.split('\t')
                    if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
                        total_additions += int(parts[0])
                        total_deletions += int(parts[1])
            
            result = f"## File History Analysis: {file_path}\n\n"
            result += f"**Total commits:** {total_commits}\n"
            if dates:
                result += f"**First commit:** {min(dates)}\n"
                result += f"**Last commit:** {max(dates)}\n"
            result += f"**Total lines added:** {total_additions}\n"
            result += f"**Total lines deleted:** {total_deletions}\n"
            result += f"**Net lines changed:** {total_additions - total_deletions}\n\n"
            
            if authors:
                result += "**Contributors:**\n"
                for author, count in sorted(authors.items(), key=lambda x: x[1], reverse=True):
                    result += f"- {author}: {count} commits\n"
                result += "\n"
            
            result += f"**Recent commits (last {min(limit, total_commits)}):**\n```\n"
            result += commits_output
            result += "```\n"
            
            return [types.TextContent(type="text", text=result)]
            
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error analyzing file history: {str(e)}")]
    
    async def _get_author_stats(self, arguments: dict) -> list[types.TextContent]:
        """Get author contribution statistics"""
        repo_path = arguments.get("repo_path")
        since = arguments.get("since")
        until = arguments.get("until")
        
        try:
            # Build git command
            cmd = ["git", "shortlog", "-sn"]
            if since:
                cmd.extend(["--since", since])
            if until:
                cmd.extend(["--until", until])
            
            output = self._run_git_command(cmd, repo_path)
            
            # Also get detailed stats
            detail_cmd = ["git", "log", "--pretty=format:%an|%ad", "--date=short"]
            if since:
                detail_cmd.extend(["--since", since])
            if until:
                detail_cmd.extend(["--until", until])
            
            detail_output = self._run_git_command(detail_cmd, repo_path)
            
            # Parse detailed data
            author_dates = {}
            for line in detail_output.strip().split('\n'):
                if '|' in line:
                    author, date = line.split('|', 1)
                    if author not in author_dates:
                        author_dates[author] = []
                    author_dates[author].append(date)
            
            result = "## Author Contribution Statistics\n\n"
            if since or until:
                date_range = []
                if since:
                    date_range.append(f"from {since}")
                if until:
                    date_range.append(f"until {until}")
                result += f"**Period:** {' '.join(date_range)}\n\n"
            
            result += "**Commit counts by author:**\n"
            result += "```\n" + output + "```\n\n"
            
            # Add activity period for each author
            if author_dates:
                result += "**Activity periods:**\n"
                for author, dates in author_dates.items():
                    if dates:
                        first_date = min(dates)
                        last_date = max(dates)
                        active_days = len(set(dates))
                        result += f"- **{author}**: {first_date} to {last_date} ({active_days} active days)\n"
            
            return [types.TextContent(type="text", text=result)]
            
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error getting author stats: {str(e)}")]
    
    async def _find_hotspots(self, arguments: dict) -> list[types.TextContent]:
        """Find files with the most changes (hotspots)"""
        repo_path = arguments.get("repo_path")
        since = arguments.get("since")
        limit = arguments.get("limit", 10)
        
        try:
            # Get file change statistics
            cmd = ["git", "log", "--name-only", "--pretty=format:"]
            if since:
                cmd.extend(["--since", since])
            
            output = self._run_git_command(cmd, repo_path)
            
            # Count file changes
            file_changes = {}
            for line in output.strip().split('\n'):
                line = line.strip()
                if line and not line.startswith('commit'):
                    file_changes[line] = file_changes.get(line, 0) + 1
            
            # Sort by change count
            sorted_files = sorted(file_changes.items(), key=lambda x: x[1], reverse=True)[:limit]
            
            result = f"## File Change Hotspots (Top {limit})\n\n"
            if since:
                result += f"**Period:** since {since}\n\n"
            
            if sorted_files:
                result += "**Files with most changes:**\n"
                for i, (file_path, count) in enumerate(sorted_files, 1):
                    result += f"{i}. **{file_path}**: {count} changes\n"
                
                # Get more detailed stats for top files
                result += "\n**Detailed analysis for top 3 files:**\n"
                for file_path, count in sorted_files[:3]:
                    try:
                        # Get recent commits for this file
                        file_cmd = ["git", "log", "--max-count=5", "--oneline", "--", file_path]
                        if since:
                            file_cmd.insert(2, "--since")
                            file_cmd.insert(3, since)
                        
                        file_commits = self._run_git_command(file_cmd, repo_path)
                        result += f"\n**{file_path}** ({count} changes):\n"
                        result += "Recent commits:\n```\n"
                        result += file_commits
                        result += "```\n"
                    except Exception:
                        pass
            else:
                result += "No file changes found in the specified period.\n"
            
            return [types.TextContent(type="text", text=result)]
            
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error finding hotspots: {str(e)}")]
    
    async def _get_commits_by_timeframe(self, arguments: dict) -> list[types.TextContent]:
        """Get commits within a specific timeframe"""
        repo_path = arguments.get("repo_path")
        since = arguments.get("since")
        until = arguments.get("until")
        author = arguments.get("author")
        
        try:
            # Build git command
            cmd = ["git", "log", "--oneline", "--decorate"]
            if since:
                cmd.extend(["--since", since])
            if until:
                cmd.extend(["--until", until])
            if author:
                cmd.extend(["--author", author])
            
            output = self._run_git_command(cmd, repo_path)
            
            # Get summary stats
            stats_cmd = ["git", "log", "--pretty=format:%an|%ad|%s", "--date=short"]
            if since:
                stats_cmd.extend(["--since", since])
            if until:
                stats_cmd.extend(["--until", until])
            if author:
                stats_cmd.extend(["--author", author])
            
            stats_output = self._run_git_command(stats_cmd, repo_path)
            
            # Parse stats
            commits = output.strip().split('\n') if output.strip() else []
            total_commits = len([c for c in commits if c.strip()])
            
            authors = {}
            dates = set()
            for line in stats_output.strip().split('\n'):
                if '|' in line:
                    parts = line.split('|', 2)
                    if len(parts) >= 2:
                        author_name, date = parts[0], parts[1]
                        authors[author_name] = authors.get(author_name, 0) + 1
                        dates.add(date)
            
            result = "## Commits by Timeframe\n\n"
            
            # Build filter description
            filters = []
            if since:
                filters.append(f"since {since}")
            if until:
                filters.append(f"until {until}")
            if author:
                filters.append(f"by author '{author}'")
            
            if filters:
                result += f"**Filters:** {', '.join(filters)}\n"
            
            result += f"**Total commits:** {total_commits}\n"
            if dates:
                result += f"**Date range:** {min(dates)} to {max(dates)}\n"
            result += f"**Authors involved:** {len(authors)}\n\n"
            
            if authors:
                result += "**Commits by author:**\n"
                for author_name, count in sorted(authors.items(), key=lambda x: x[1], reverse=True):
                    result += f"- {author_name}: {count} commits\n"
                result += "\n"
            
            if total_commits > 0:
                result += "**Commits:**\n```\n"
                result += output
                result += "```\n"
            else:
                result += "No commits found matching the specified criteria.\n"
            
            return [types.TextContent(type="text", text=result)]
            
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error getting commits by timeframe: {str(e)}")]

    async def _get_churn_stats(self, arguments: dict) -> list[types.TextContent]:
        """Compute code churn (additions/deletions) over an optional timeframe and path"""
        repo_path = arguments.get("repo_path")
        since = arguments.get("since")
        until = arguments.get("until")
        scope_path = arguments.get("path")
        top_files = int(arguments.get("top_files", 10))

        try:
            # Build base git log with numstat to get per-file additions/deletions
            cmd = ["git", "log", "--numstat", "--pretty=format:"]
            if since:
                cmd.extend(["--since", since])
            if until:
                cmd.extend(["--until", until])
            if scope_path:
                cmd.extend(["--", scope_path])

            output = self._run_git_command(cmd, repo_path)

            total_add = 0
            total_del = 0
            per_file: dict[str, tuple[int, int]] = {}

            for line in output.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("\t")
                if len(parts) < 3:
                    continue
                add_s, del_s, file_path = parts[0], parts[1], parts[2]
                # Handle binary files marked as '-'
                try:
                    adds = int(add_s) if add_s.isdigit() else 0
                    dels = int(del_s) if del_s.isdigit() else 0
                except ValueError:
                    adds = 0
                    dels = 0
                total_add += adds
                total_del += dels
                a, d = per_file.get(file_path, (0, 0))
                per_file[file_path] = (a + adds, d + dels)

            # Get commit count and date range for the same filters
            dates_cmd = ["git", "log", "--pretty=format:%ad", "--date=short"]
            if since:
                dates_cmd.extend(["--since", since])
            if until:
                dates_cmd.extend(["--until", until])
            if scope_path:
                dates_cmd.extend(["--", scope_path])

            dates_out = self._run_git_command(dates_cmd, repo_path)
            dates = [d for d in dates_out.strip().split("\n") if d.strip()]
            commit_count = len(dates)

            result = "## Code Churn Statistics\n\n"
            filters = []
            if since:
                filters.append(f"since {since}")
            if until:
                filters.append(f"until {until}")
            if scope_path:
                filters.append(f"path '{scope_path}'")
            if filters:
                result += f"**Filters:** {', '.join(filters)}\n"
            result += f"**Total commits considered:** {commit_count}\n"
            if dates:
                result += f"**Date range:** {min(dates)} to {max(dates)}\n"
            result += f"**Total additions:** {total_add}\n"
            result += f"**Total deletions:** {total_del}\n"
            result += f"**Net change:** {total_add - total_del}\n\n"

            if per_file:
                # rank by churn (adds + dels)
                ranked = sorted(per_file.items(), key=lambda kv: (kv[1][0] + kv[1][1]), reverse=True)
                top = ranked[: max(0, top_files)]
                result += f"**Top files by churn (additions+deletions) — Top {len(top)}:**\n"
                for idx, (fp, (a, d)) in enumerate(top, 1):
                    result += f"{idx}. {fp}: +{a} / -{d} (total {a + d})\n"
            else:
                result += "No churn found for the specified filters.\n"

            return [types.TextContent(type="text", text=result)]

        except Exception as e:
            return [types.TextContent(type="text", text=f"Error computing churn stats: {str(e)}")]
    
    async def run(self):
        """Run the MCP server"""
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="git-history-analysis",
                    server_version="0.1.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )


def main():
    """Main entry point"""
    async def run_server():
        server = GitHistoryServer()
        await server.run()
    
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
