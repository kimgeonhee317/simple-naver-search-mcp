Convert a standard MCP server file (`server.py`) to a genos-compatible version and save it as `genos/server-genos.py` in the same directory.

## What genos is

Genos is an air-gapped MCP framework. Third-party packages cannot be imported at the top level — they must be loaded via `genos_import` inside each tool function. The server uses FastMCP's `@mcp.tool()` decorator instead of the low-level `Server` + `@app.list_tools()` / `@app.call_tool()` pattern.

## Conversion steps

Read the source `server.py` (or the file the user points to), then produce `genos/server-genos.py` following these rules:

### 1. Replace server setup
- Remove: `from mcp.server import Server`, `app = Server(...)`, `load_dotenv()`
- Add: `from mcp.server.fastmcp import FastMCP` and `mcp = FastMCP("server-name")`
- Keep: `import os`, `import re`, `import logging`, and all `os.getenv(...)` calls (no dotenv)

### 2. Keep helper/formatter functions unchanged
Pure-stdlib helpers (e.g. `strip_html`, `fmt_*`) don't need changes — do NOT add genos_import to them.

### 3. Remove the dispatch table
Delete `TOOLS`, `TOOL_MAP`, `@app.list_tools()`, and `@app.call_tool()` entirely.

### 4. Create one `@mcp.tool()` function per tool
For each entry that was in the TOOLS list, create:

```python
@mcp.tool()
async def tool_name(param: str, ...) -> str:
    """
    [Tool description here — copied from the original TOOLS tuple]

    Args:
        param (str): description

    Returns:
        str: description
    """
    try:
        from util.genos_utils import genos_import
        requests = genos_import('requests', install_name='requests')
    except Exception as e:
        return f"Error: failed to import requests — {e}"
    # ... tool logic using requests (sync) instead of httpx (async)
```

**Order within each function must be:**
1. Docstring (first statement — required for FastMCP schema generation)
2. `try/except` block for `genos_import`
3. Logic

### 5. Replace httpx with requests
- Remove all `httpx.AsyncClient` / `await client.get(...)` usage
- Use `requests.get(...)` (sync) instead
- Error handling: check `resp.status_code` directly and return error strings; call `resp.raise_for_status()` for other errors

### 6. Remove the main() entrypoint
Delete the `main()` function and `if __name__ == "__main__"` block — genos handles process lifecycle.

### 7. Output location
Save the result to `genos/server-genos.py` inside the same directory as the source file.

## Example — single tool before/after

**Before (server.py):**
```python
@app.call_tool()
async def call_tool(name, arguments):
    # dispatches to naver_search() via TOOL_MAP
```

**After (server-genos.py):**
```python
@mcp.tool()
async def naver_search_news(query: str, display: int = 10, start: int = 1, sort: str = "sim") -> str:
    """
    Search Naver News for recent Korean news articles.
    ...
    """
    try:
        from util.genos_utils import genos_import
        requests = genos_import('requests', install_name='requests')
    except Exception as e:
        return f"Error: failed to import requests — {e}"
    display = max(1, min(display, 100))
    sort = sort if sort in ("sim", "date") else "sim"
    resp = requests.get(url, headers=headers, params=params)
    if resp.status_code == 401:
        return "Error: Invalid API credentials."
    resp.raise_for_status()
    return fmt_result(resp.json())
```

Now perform this conversion on the file specified by the user (default: `src/naver_search/server.py`).
