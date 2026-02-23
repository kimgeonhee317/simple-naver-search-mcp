# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
uv sync

# Install dev dependencies (needed for scripts/test_api.py)
uv sync --extra dev

# Run the MCP server (requires NAVER_CLIENT_ID and NAVER_CLIENT_SECRET in env)
uv run naver-search-mcp

# Verify import (used by CI)
uv run python -c "from naver_search.server import app; print('OK')"

# Test all Naver API endpoints manually (requires .env with real credentials)
uv run python scripts/test_api.py
```

There is no test suite. CI only checks that the package installs and imports cleanly.

## Architecture

This is an MCP server that wraps the Naver Search Open API, exposing 10 search tools to MCP clients (Claude Desktop, etc.). The server communicates over stdio using the MCP protocol.

### Two implementations

- **`src/naver_search/server.py`** — The canonical implementation. Uses the low-level `mcp.Server` class with `httpx` (async). This is what `uv run naver-search-mcp` launches (entrypoint: `naver_search.server:main`).
- **`genos/server-genos.py`** — An alternate implementation using `FastMCP` + a `genos_import` runtime helper. This variant is for use in the Genos environment and is not installed as a package entrypoint.

### How the main server works

All 10 tools are declared in the `TOOLS` list (`server.py:171`), a flat list of tuples `(tool_name, api_type, description, fmt_fn)`. From this single source of truth:

- `TOOL_MAP` (`server.py:285`) maps `tool_name → (api_type, fmt_fn)` for dispatch in `call_tool`.
- `list_tools()` (`server.py:288`) generates MCP tool schemas dynamically, adding a `sort` enum only for types that support it (controlled by `SORT_OPTIONS`).
- `call_tool()` (`server.py:313`) handles all tools uniformly: look up `api_type` and `fmt_fn`, call `naver_search()`, then call `fmt_fn(items)`.

### Adding a new search type

1. Add a `fmt_<type>` formatter function.
2. Add the valid sort values to `SORT_OPTIONS`.
3. Add a tuple to the `TOOLS` list — the rest is automatic.

### Formatter pattern

Each `fmt_*` function takes `items: list` and returns a plain-text string. HTML `<b>` tags in Naver API responses are stripped by `strip_html()` before formatting. The header line `total: N | showing: X~Y | sort: Z` is prepended in `call_tool()`.

### Credentials

`NAVER_CLIENT_ID` and `NAVER_CLIENT_SECRET` are read from the environment (or `.env` via `python-dotenv`). The server raises `RuntimeError` at startup if either is missing.
