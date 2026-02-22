# simple-naver-search-mcp

An MCP server that exposes Naver Search (뉴스, 블로그, 웹, 이미지, 쇼핑, 지식iN, 지역, 책, 카페) as tools for Claude and other MCP clients.

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- [Naver Open API](https://developers.naver.com) credentials

## Setup

```bash
# 1. Clone the repo
git clone https://github.com/your-username/simple-naver-search-mcp
cd simple-naver-search-mcp

# 2. Install dependencies
uv sync

# 3. Set credentials
cp .env.example .env
# Edit .env and fill in NAVER_CLIENT_ID and NAVER_CLIENT_SECRET
```

## Claude Desktop Configuration

Add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "naver-search": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/simple-naver-search-mcp",
        "run",
        "naver-search-mcp"
      ],
      "env": {
        "NAVER_CLIENT_ID": "your_client_id_here",
        "NAVER_CLIENT_SECRET": "your_client_secret_here"
      }
    }
  }
}
```

> Config file location:
> - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
> - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

## Available Tools

| Tool | Description |
|---|---|
| `naver_search_news` | Search Naver News articles |
| `naver_search_blog` | Search Naver Blog posts |
| `naver_search_web` | Search Naver Web pages |
| `naver_search_image` | Search Naver Images |
| `naver_search_shop` | Search Naver Shopping |
| `naver_search_doc` | Search Naver academic/office docs |
| `naver_search_local` | Search Naver Local places |
| `naver_search_kin` | Search Naver 지식iN (Q&A) |
| `naver_search_book` | Search Naver Books |
| `naver_search_cafe` | Search Naver Cafe articles |

All tools accept:
- `query` (required) — search keyword
- `display` (optional, 1–100, default 10) — number of results

## Testing

```bash
uv run python test_api.py
```

## Naver Search API — Type Reference

| Type | Key Fields | Notes |
|---|---|---|
| `news` | `title`, `originallink`, `link`, `description`, `pubDate` | Has both original & Naver link |
| `blog` | `title`, `link`, `description`, `bloggername`, `bloggerlink`, `postdate` | Good author info |
| `webkr` | `title`, `link`, `description` | General web, minimal metadata |
| `image` | `title`, `link`, `thumbnail`, `sizeheight`, `sizewidth` | No description |
| `shop` | — | Empty for non-product queries |
| `doc` | — | Empty for most queries |
| `local` | — | Needs place name query, not a sentence |
| `kin` | `title`, `link`, `description` | 지식iN Q&A |
| `book` | — | Empty for non-book queries |
| `cafearticle` | `title`, `link`, `description`, `cafename`, `cafeurl` | Has cafe name info |

**Notes:**
- `title` and `description` contain HTML `<b>` tags — strip before use
- `news` is richest for real estate queries (has `pubDate`)
- `shop`, `doc`, `book` irrelevant for real estate use case
- `local` requires a place name query format

## License

MIT
