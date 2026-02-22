# simple-naver-search-mcp

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![CI](https://github.com/kimgeonhee317/simple-naver-search-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/kimgeonhee317/simple-naver-search-mcp/actions/workflows/ci.yml)

An MCP server that exposes Naver Search (뉴스, 블로그, 웹, 이미지, 쇼핑, 지식iN, 지역, 책, 카페) as tools for Claude and other MCP clients.

Designed for AI agents that cannot access the internet directly — gives LLMs real-time access to Korean web search without outbound HTTP from the model itself.

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- [Naver Open API](https://developers.naver.com) credentials

## Setup

```bash
# 1. Clone the repo
git clone https://github.com/kimgeonhee317/simple-naver-search-mcp
cd simple-naver-search-mcp

# 2. Install dependencies
uv sync

# 3. Set credentials
cp .env.example .env
# Edit .env and fill in NAVER_CLIENT_ID and NAVER_CLIENT_SECRET

# 4. (Optional) Install dev dependencies for manual API testing
uv sync --extra dev
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

| Tool | Description | Supported `sort` values |
|---|---|---|
| `naver_search_news` | Search Naver News articles | `sim`, `date` |
| `naver_search_blog` | Search Naver Blog posts | `sim`, `date` |
| `naver_search_web` | Search Naver Web pages | `sim`, `date` |
| `naver_search_image` | Search Naver Images | `sim`, `date` |
| `naver_search_shop` | Search Naver Shopping | `sim`, `date`, `asc` (price↑), `dsc` (price↓) |
| `naver_search_doc` | Search Naver academic/office docs *(returns empty for most general queries)* | `sim`, `date` |
| `naver_search_local` | Search Naver Local places | *(not supported)* |
| `naver_search_kin` | Search Naver 지식iN (Q&A) | `sim`, `date`, `point` |
| `naver_search_book` | Search Naver Books | `sim`, `date`, `count`, `score` |
| `naver_search_cafe` | Search Naver Cafe articles | `sim`, `date` |

All tools accept:

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `query` | string | yes | — | Search keyword |
| `display` | integer | no | 10 | Number of results to return (1–100) |
| `sort` | string | no | `"sim"` | Sort order — see table above for valid values per tool |
| `start` | integer | no | 1 | Pagination offset (1-based, max 1000) |

**Pagination example** — fetching page 2 when `display=10`:
```
start=1  → results  1–10
start=11 → results 11–20
start=21 → results 21–30
```
The result header always shows context: `total: 1420 | showing: 1~10 | sort: date`

> **Note:** `total` from Naver is approximate. Actual retrievable results are capped at 1000 regardless of reported total.

## Recommended System Prompt

Tool descriptions handle single-tool selection, but a system prompt is needed for multi-tool strategy, consistent sort behavior, and domain-specific workflows. Below is a general-purpose example in Korean.

```
당신은 네이버 검색 도구를 활용하는 한국어 정보 검색 전문 AI입니다.

## 검색 전략

**다중 도구 활용:**
- 사용자가 종합적인 정보를 요청하면 여러 도구를 함께 사용하세요.
  - 부동산/시세 조회 → news(sort=date) + blog + cafe 조합
  - 상품 구매 결정 → shop(sort=asc) + blog(리뷰) 조합
  - 장소/맛집 탐색 → local + blog 조합
  - 사회적 이슈/트렌드 → news(sort=date) + kin 조합

**정렬 기본값:**
- 최신 뉴스, 시세, 정책, 사건 관련 쿼리 → 반드시 sort=date 사용
- 리뷰, 추천, 일반 정보 쿼리 → sort=sim (기본값) 유지

**쿼리 작성 규칙:**
- naver_search_local: 사용자 문장에서 장소명/상호명만 추출하여 전달
  - 예) "강남에 있는 스타벅스 찾아줘" → query="강남 스타벅스"
- naver_search_news: 핵심 키워드 위주로 간결하게 작성
- naver_search_shop: 브랜드명 + 모델명으로 구체적으로 작성

**검색하지 않아도 되는 경우:**
- 사용자가 일반 상식이나 역사적 사실을 묻는 경우
- 검색 없이 충분히 답할 수 있는 개념 설명 요청

## 결과 처리

- 검색 결과를 그대로 나열하지 말고, 핵심 내용을 요약하여 전달하세요.
- 출처(링크)는 중요한 정보에만 인용하세요.
- 결과가 없거나 부족하면 다른 도구나 다른 키워드로 재시도하세요.
- 페이지네이션: 첫 결과가 불충분하면 start를 늘려 추가 결과를 가져오세요.
```

> This is a general template. Customize it for your specific domain (e.g. real estate agent, shopping assistant, news summarizer).

## Manual API Testing

```bash
uv run python scripts/test_api.py
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
- `title` and `description` contain HTML `<b>` tags — stripped automatically by the server before returning results
- `shop`, `doc`, `book` return empty results for non-product / non-book queries
- `local` requires a place name or business name as the query, not a full sentence

## License

MIT
