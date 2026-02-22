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

## Example Output

<details>
<summary><code>naver_search_news</code></summary>

```
total: 48200 | showing: 1~3 | sort: date

[1] 한국은행, 기준금리 0.25%p 인하 결정
    Mon, 16 Feb 2026 14:32:00 +0900
    한국은행 금융통화위원회가 기준금리를 연 2.75%로 0.25%포인트 인하했다...
    https://www.yna.co.kr/view/AKR20260216XXXXXX

[2] 금리 인하에 부동산 시장 반응은?
    Mon, 16 Feb 2026 15:10:00 +0900
    전문가들은 이번 금리 인하가 침체된 부동산 시장에 온기를 불어넣을 것으로...
    https://www.chosun.com/economy/2026/02/16/XXXXXX
```

</details>

<details>
<summary><code>naver_search_blog</code></summary>

```
total: 125000 | showing: 1~2 | sort: sim

[1] 제주도 3박4일 혼자 여행 완벽 후기
    by 여행하는곰 (20260110)
    제주도를 혼자 여행하고 왔어요. 숙소는 애월 게스트하우스를 선택했는데...
    https://blog.naver.com/travelbear/XXXXXX

[2] 제주 맛집 총정리 - 현지인 추천 TOP 10
    by 제주토박이 (20260205)
    제주에서 20년 살면서 알게 된 진짜 맛집만 모았습니다. 관광객 맛집 말고...
    https://blog.naver.com/jejunative/XXXXXX
```

</details>

<details>
<summary><code>naver_search_web</code></summary>

```
total: 980000 | showing: 1~2 | sort: sim

[1] 파이썬 가상환경 설정 방법 - venv, conda 비교
    파이썬 프로젝트를 시작할 때 가상환경을 설정하는 방법과 venv와 conda의 차이점을 설명합니다...
    https://wikidocs.net/XXXXX

[2] Python 가상환경(venv) 완전 정복
    venv 모듈을 사용해 가상환경을 생성하고 활성화하는 방법, 패키지 관리까지 정리했습니다...
    https://dojang.io/mod/page/view.php?id=XXXXX
```

</details>

<details>
<summary><code>naver_search_image</code></summary>

```
total: 53000 | showing: 1~2 | sort: sim

[1] 골든 리트리버 강아지
    1200x800px
    image: https://shopping-phinf.pstatic.net/XXXXXX.jpg
    thumb: https://thumb.pstatic.net/XXXXXX.jpg

[2] 귀여운 골든 리트리버
    800x600px
    image: https://blogfiles.pstatic.net/XXXXXX.jpg
    thumb: https://thumb.pstatic.net/XXXXXX.jpg
```

</details>

<details>
<summary><code>naver_search_shop</code></summary>

```
total: 8420 | showing: 1~2 | sort: asc

[1] 나이키 에어맥스 90 화이트 (270mm)
    89000원 ~ 89000원
    나이키공식온라인스토어 | Nike
    https://smartstore.naver.com/XXXXXX

[2] 나이키 에어맥스 90 블랙 (270mm)
    92000원 ~ 95000원
    스포츠용품몰 | Nike
    https://smartstore.naver.com/XXXXXX
```

</details>

<details>
<summary><code>naver_search_local</code></summary>

```
total: 38 | showing: 1~2 | sort: n/a

[1] 스타벅스 강남점
    카페,음료 | 02-XXX-XXXX
    서울특별시 강남구 테헤란로 XXX
    https://map.naver.com/v5/entry/place/XXXXXX

[2] 스타벅스 강남역점
    카페,음료 | 02-XXX-XXXX
    서울특별시 강남구 강남대로 XXX
    https://map.naver.com/v5/entry/place/XXXXXX
```

</details>

<details>
<summary><code>naver_search_kin</code></summary>

```
total: 32400 | showing: 1~2 | sort: point

[1] 강아지가 갑자기 밥을 안 먹어요, 이유가 뭔가요?
    강아지가 갑자기 밥을 거부할 때는 여러 가지 원인이 있을 수 있습니다. 스트레스, 환경 변화...
    https://kin.naver.com/qna/detail.naver?d1id=XXXXXX

[2] 강아지 밥 안 먹을 때 해결 방법
    저도 같은 문제로 고민했는데, 사료 브랜드를 바꾸거나 습식 사료를 섞어주면 잘 먹더라고요...
    https://kin.naver.com/qna/detail.naver?d1id=XXXXXX
```

</details>

<details>
<summary><code>naver_search_book</code></summary>

```
total: 240 | showing: 1~2 | sort: score

[1] 클린 코드
    로버트 C. 마틴 | 인사이트 | 20131231
    22000원
    나쁜 코드도 돌아간다. 하지만 코드가 나쁘면 개발 속도가 크게 떨어진다...
    https://search.shopping.naver.com/book/XXXXXX

[2] 리팩터링 2판
    마틴 파울러 | 한빛미디어 | 20200101
    36000원
    코드 구조를 체계적으로 개선하여 효율적인 리팩터링 구현하기...
    https://search.shopping.naver.com/book/XXXXXX
```

</details>

<details>
<summary><code>naver_search_cafe</code></summary>

```
total: 15800 | showing: 1~2 | sort: date

[1] 2월 탁구 횡회전 서브 연습 후기
    탁구사랑 (https://cafe.naver.com/tabletennis)
    오늘 드디어 횡회전 서브를 제대로 익혔습니다. 핵심은 라켓 각도보다 손목 스냅이더라고요...
    https://cafe.naver.com/tabletennis/XXXXXX

[2] 횡회전 서브 교정 받고 나서 달라진 점
    탁구동호회 (https://cafe.naver.com/pingpong)
    코치님께 자세 교정 받은 후 서브 성공률이 확 올라갔어요. 팔꿈치 위치가 핵심...
    https://cafe.naver.com/pingpong/XXXXXX
```

</details>

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
