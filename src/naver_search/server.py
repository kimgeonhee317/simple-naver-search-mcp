import logging
import os
import re
from dotenv import load_dotenv
import httpx
import mcp.server.stdio
import mcp.types as types
from mcp.server import Server

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("naver-search-mcp")

NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
NAVER_API_BASE = "https://openapi.naver.com/v1/search"

if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
    raise RuntimeError("NAVER_CLIENT_ID and NAVER_CLIENT_SECRET must be set in environment")

app = Server("naver-search-mcp")


def strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text or "")


async def naver_search(search_type: str, query: str, display: int = 10) -> dict:
    display = max(1, min(display, 100))
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
    }
    logger.info("naver_search type=%s query=%r display=%d", search_type, query, display)
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{NAVER_API_BASE}/{search_type}",
            headers=headers,
            params={"query": query, "display": display},
        )
        if response.status_code == 401:
            raise ValueError("Invalid Naver API credentials. Check NAVER_CLIENT_ID and NAVER_CLIENT_SECRET.")
        if response.status_code == 429:
            raise ValueError("Naver API rate limit exceeded. Please try again later.")
        response.raise_for_status()
        return response.json()


def fmt_news(items: list) -> str:
    lines = []
    for i, item in enumerate(items, 1):
        lines.append(f"[{i}] {strip_html(item.get('title', ''))}")
        lines.append(f"    {item.get('pubDate', '')}")
        lines.append(f"    {strip_html(item.get('description', ''))}")
        lines.append(f"    {item.get('originallink') or item.get('link', '')}")
    return "\n".join(lines)


def fmt_blog(items: list) -> str:
    lines = []
    for i, item in enumerate(items, 1):
        lines.append(f"[{i}] {strip_html(item.get('title', ''))}")
        lines.append(f"    by {item.get('bloggername', '')} ({item.get('postdate', '')})")
        lines.append(f"    {strip_html(item.get('description', ''))}")
        lines.append(f"    {item.get('link', '')}")
    return "\n".join(lines)


def fmt_webkr(items: list) -> str:
    lines = []
    for i, item in enumerate(items, 1):
        lines.append(f"[{i}] {strip_html(item.get('title', ''))}")
        lines.append(f"    {strip_html(item.get('description', ''))}")
        lines.append(f"    {item.get('link', '')}")
    return "\n".join(lines)


def fmt_image(items: list) -> str:
    lines = []
    for i, item in enumerate(items, 1):
        lines.append(f"[{i}] {strip_html(item.get('title', ''))}")
        lines.append(f"    {item.get('sizewidth', '')}x{item.get('sizeheight', '')}px")
        lines.append(f"    image: {item.get('link', '')}")
        lines.append(f"    thumb: {item.get('thumbnail', '')}")
    return "\n".join(lines)


def fmt_shop(items: list) -> str:
    lines = []
    for i, item in enumerate(items, 1):
        lines.append(f"[{i}] {strip_html(item.get('title', ''))}")
        lines.append(f"    {item.get('lprice', '')}원 ~ {item.get('hprice', '')}원")
        lines.append(f"    {item.get('mallName', '')} | {item.get('maker', '')}")
        lines.append(f"    {item.get('link', '')}")
    return "\n".join(lines)


def fmt_doc(items: list) -> str:
    lines = []
    for i, item in enumerate(items, 1):
        lines.append(f"[{i}] {strip_html(item.get('title', ''))}")
        lines.append(f"    {strip_html(item.get('description', ''))}")
        lines.append(f"    {item.get('link', '')}")
    return "\n".join(lines)


def fmt_local(items: list) -> str:
    lines = []
    for i, item in enumerate(items, 1):
        lines.append(f"[{i}] {strip_html(item.get('title', ''))}")
        lines.append(f"    {item.get('category', '')} | {item.get('telephone', '')}")
        lines.append(f"    {item.get('address', '')}")
        lines.append(f"    {item.get('link', '')}")
    return "\n".join(lines)


def fmt_kin(items: list) -> str:
    lines = []
    for i, item in enumerate(items, 1):
        lines.append(f"[{i}] {strip_html(item.get('title', ''))}")
        lines.append(f"    {strip_html(item.get('description', ''))}")
        lines.append(f"    {item.get('link', '')}")
    return "\n".join(lines)


def fmt_book(items: list) -> str:
    lines = []
    for i, item in enumerate(items, 1):
        lines.append(f"[{i}] {strip_html(item.get('title', ''))}")
        lines.append(f"    {item.get('author', '')} | {item.get('publisher', '')} | {item.get('pubdate', '')}")
        lines.append(f"    {item.get('discount', '') or item.get('price', '')}원")
        lines.append(f"    {strip_html(item.get('description', ''))}")
        lines.append(f"    {item.get('link', '')}")
    return "\n".join(lines)


def fmt_cafearticle(items: list) -> str:
    lines = []
    for i, item in enumerate(items, 1):
        lines.append(f"[{i}] {strip_html(item.get('title', ''))}")
        lines.append(f"    {item.get('cafename', '')} ({item.get('cafeurl', '')})")
        lines.append(f"    {strip_html(item.get('description', ''))}")
        lines.append(f"    {item.get('link', '')}")
    return "\n".join(lines)


TOOLS = [
    ("naver_search_news",        "news",         "Search Naver News articles",           fmt_news),
    ("naver_search_blog",        "blog",         "Search Naver Blog posts",              fmt_blog),
    ("naver_search_web",         "webkr",        "Search Naver Web pages",               fmt_webkr),
    ("naver_search_image",       "image",        "Search Naver Images",                  fmt_image),
    ("naver_search_shop",        "shop",         "Search Naver Shopping",                fmt_shop),
    ("naver_search_doc",         "doc",          "Search Naver academic/office docs",    fmt_doc),
    ("naver_search_local",       "local",        "Search Naver Local places",            fmt_local),
    ("naver_search_kin",         "kin",          "Search Naver 지식iN (Q&A)",             fmt_kin),
    ("naver_search_book",        "book",         "Search Naver Books",                   fmt_book),
    ("naver_search_cafe",        "cafearticle",  "Search Naver Cafe articles",           fmt_cafearticle),
]

TOOL_MAP = {name: (api_type, fmt) for name, api_type, _, fmt in TOOLS}


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name=name,
            description=desc,
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "display": {"type": "integer", "description": "Number of results (1-100)", "default": 10},
                },
                "required": ["query"],
            },
        )
        for name, _, desc, _ in TOOLS
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name not in TOOL_MAP:
        raise ValueError(f"Unknown tool: {name}")

    query = (arguments.get("query") or "").strip()
    if not query:
        return [types.TextContent(type="text", text="Error: query must not be empty.")]

    api_type, fmt = TOOL_MAP[name]
    display = arguments.get("display", 10)

    try:
        data = await naver_search(api_type, query, display)
    except ValueError as e:
        return [types.TextContent(type="text", text=f"Error: {e}")]
    except httpx.HTTPStatusError as e:
        return [types.TextContent(type="text", text=f"API error {e.response.status_code}: {e.response.text}")]
    except httpx.RequestError as e:
        return [types.TextContent(type="text", text=f"Network error: {e}")]

    items = data.get("items", [])
    total = data.get("total", 0)

    if not items:
        result = f"No results found. (total reported: {total})"
    else:
        result = f"total: {total}\n\n" + fmt(items)

    return [types.TextContent(type="text", text=result)]


def main():
    import asyncio
    asyncio.run(mcp.server.stdio.run(app))


if __name__ == "__main__":
    main()
