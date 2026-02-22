import os
import re
import logging

from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("naver-search-mcp")

NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID", "")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET", "")
NAVER_API_BASE = "https://openapi.naver.com/v1/search"

mcp = FastMCP("naver-search-mcp")

# ---------------------------------------------------------------------------
# Helpers (stdlib only — no genos_import needed)
# ---------------------------------------------------------------------------

def strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text or "")


def _fmt_result(items: list, start: int, total: int, sort: str, fmt_fn) -> str:
    if not items:
        return f"No results found. (total reported: {total})"
    header = f"total: {total} | showing: {start}~{start + len(items) - 1} | sort: {sort}"
    return header + "\n\n" + fmt_fn(items)


def fmt_news(items):
    lines = []
    for i, item in enumerate(items, 1):
        lines.append(f"[{i}] {strip_html(item.get('title', ''))}")
        lines.append(f"    {item.get('pubDate', '')}")
        lines.append(f"    {strip_html(item.get('description', ''))}")
        lines.append(f"    {item.get('originallink') or item.get('link', '')}")
    return "\n".join(lines)


def fmt_blog(items):
    lines = []
    for i, item in enumerate(items, 1):
        lines.append(f"[{i}] {strip_html(item.get('title', ''))}")
        lines.append(f"    by {item.get('bloggername', '')} ({item.get('postdate', '')})")
        lines.append(f"    {strip_html(item.get('description', ''))}")
        lines.append(f"    {item.get('link', '')}")
    return "\n".join(lines)


def fmt_webkr(items):
    lines = []
    for i, item in enumerate(items, 1):
        lines.append(f"[{i}] {strip_html(item.get('title', ''))}")
        lines.append(f"    {strip_html(item.get('description', ''))}")
        lines.append(f"    {item.get('link', '')}")
    return "\n".join(lines)


def fmt_image(items):
    lines = []
    for i, item in enumerate(items, 1):
        lines.append(f"[{i}] {strip_html(item.get('title', ''))}")
        lines.append(f"    {item.get('sizewidth', '')}x{item.get('sizeheight', '')}px")
        lines.append(f"    image: {item.get('link', '')}")
        lines.append(f"    thumb: {item.get('thumbnail', '')}")
    return "\n".join(lines)


def fmt_shop(items):
    lines = []
    for i, item in enumerate(items, 1):
        lines.append(f"[{i}] {strip_html(item.get('title', ''))}")
        lines.append(f"    {item.get('lprice', '')}원 ~ {item.get('hprice', '')}원")
        lines.append(f"    {item.get('mallName', '')} | {item.get('maker', '')}")
        lines.append(f"    {item.get('link', '')}")
    return "\n".join(lines)


def fmt_doc(items):
    lines = []
    for i, item in enumerate(items, 1):
        lines.append(f"[{i}] {strip_html(item.get('title', ''))}")
        lines.append(f"    {strip_html(item.get('description', ''))}")
        lines.append(f"    {item.get('link', '')}")
    return "\n".join(lines)


def fmt_local(items):
    lines = []
    for i, item in enumerate(items, 1):
        lines.append(f"[{i}] {strip_html(item.get('title', ''))}")
        lines.append(f"    {item.get('category', '')} | {item.get('telephone', '')}")
        lines.append(f"    {item.get('address', '')}")
        lines.append(f"    {item.get('link', '')}")
    return "\n".join(lines)


def fmt_kin(items):
    lines = []
    for i, item in enumerate(items, 1):
        lines.append(f"[{i}] {strip_html(item.get('title', ''))}")
        lines.append(f"    {strip_html(item.get('description', ''))}")
        lines.append(f"    {item.get('link', '')}")
    return "\n".join(lines)


def fmt_book(items):
    lines = []
    for i, item in enumerate(items, 1):
        lines.append(f"[{i}] {strip_html(item.get('title', ''))}")
        lines.append(f"    {item.get('author', '')} | {item.get('publisher', '')} | {item.get('pubdate', '')}")
        lines.append(f"    {item.get('discount', '') or item.get('price', '')}원")
        lines.append(f"    {strip_html(item.get('description', ''))}")
        lines.append(f"    {item.get('link', '')}")
    return "\n".join(lines)


def fmt_cafearticle(items):
    lines = []
    for i, item in enumerate(items, 1):
        lines.append(f"[{i}] {strip_html(item.get('title', ''))}")
        lines.append(f"    {item.get('cafename', '')} ({item.get('cafeurl', '')})")
        lines.append(f"    {strip_html(item.get('description', ''))}")
        lines.append(f"    {item.get('link', '')}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@mcp.tool()
async def naver_search_news(query: str, display: int = 10, start: int = 1, sort: str = "sim") -> str:
    """
    Search Naver News for recent Korean news articles.
    Use this when the user asks about current events, breaking news, or recent developments on a topic.
    Returns title, publication date, source link, and a short excerpt.
    Best for time-sensitive queries like market trends, policy changes, or recent incidents.

    Args:
        query (str): Search keyword
        display (int): Number of results to return (1-100, default 10)
        start (int): Pagination offset, 1-based (default 1). Use start=11 for page 2 when display=10.
        sort (str): Sort order — "sim" (relevance) or "date" (latest first)

    Returns:
        str: Formatted list of news articles
    """
    try:
        from util.genos_utils import genos_import
        requests = genos_import('requests', install_name='requests')
    except Exception as e:
        return f"Error: failed to import requests — {e}"
    display = max(1, min(display, 100))
    start = max(1, min(start, 1000))
    sort = sort if sort in ("sim", "date") else "sim"
    headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
    params = {"query": query.strip(), "display": display, "start": start, "sort": sort}
    logger.info("naver_search_news query=%r display=%d start=%d sort=%s", query, display, start, sort)
    resp = requests.get(f"{NAVER_API_BASE}/news", headers=headers, params=params)
    if resp.status_code == 401:
        return "Error: Invalid Naver API credentials."
    if resp.status_code == 429:
        return "Error: Naver API rate limit exceeded. Try again later."
    resp.raise_for_status()
    data = resp.json()
    return _fmt_result(data.get("items", []), start, data.get("total", 0), sort, fmt_news)


@mcp.tool()
async def naver_search_blog(query: str, display: int = 10, start: int = 1, sort: str = "sim") -> str:
    """
    Search Naver Blog for personal blog posts written in Korean.
    Use this when the user wants detailed personal experiences, reviews, tips, or how-to guides.
    Returns title, author, post date, excerpt, and link.
    Best for queries like product reviews, travel experiences, recipes, or local tips.

    Args:
        query (str): Search keyword
        display (int): Number of results to return (1-100, default 10)
        start (int): Pagination offset, 1-based (default 1)
        sort (str): Sort order — "sim" (relevance) or "date" (latest first)

    Returns:
        str: Formatted list of blog posts
    """
    try:
        from util.genos_utils import genos_import
        requests = genos_import('requests', install_name='requests')
    except Exception as e:
        return f"Error: failed to import requests — {e}"
    display = max(1, min(display, 100))
    start = max(1, min(start, 1000))
    sort = sort if sort in ("sim", "date") else "sim"
    headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
    params = {"query": query.strip(), "display": display, "start": start, "sort": sort}
    logger.info("naver_search_blog query=%r display=%d start=%d sort=%s", query, display, start, sort)
    resp = requests.get(f"{NAVER_API_BASE}/blog", headers=headers, params=params)
    if resp.status_code == 401:
        return "Error: Invalid Naver API credentials."
    if resp.status_code == 429:
        return "Error: Naver API rate limit exceeded. Try again later."
    resp.raise_for_status()
    data = resp.json()
    return _fmt_result(data.get("items", []), start, data.get("total", 0), sort, fmt_blog)


@mcp.tool()
async def naver_search_web(query: str, display: int = 10, start: int = 1, sort: str = "sim") -> str:
    """
    Search Naver Web for general Korean web pages.
    Use this as a broad fallback when no other specialized tool fits,
    or when the user needs general information from any type of Korean website.
    Returns title, description, and link.

    Args:
        query (str): Search keyword
        display (int): Number of results to return (1-100, default 10)
        start (int): Pagination offset, 1-based (default 1)
        sort (str): Sort order — "sim" (relevance) or "date" (latest first)

    Returns:
        str: Formatted list of web pages
    """
    try:
        from util.genos_utils import genos_import
        requests = genos_import('requests', install_name='requests')
    except Exception as e:
        return f"Error: failed to import requests — {e}"
    display = max(1, min(display, 100))
    start = max(1, min(start, 1000))
    sort = sort if sort in ("sim", "date") else "sim"
    headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
    params = {"query": query.strip(), "display": display, "start": start, "sort": sort}
    logger.info("naver_search_web query=%r display=%d start=%d sort=%s", query, display, start, sort)
    resp = requests.get(f"{NAVER_API_BASE}/webkr", headers=headers, params=params)
    if resp.status_code == 401:
        return "Error: Invalid Naver API credentials."
    if resp.status_code == 429:
        return "Error: Naver API rate limit exceeded. Try again later."
    resp.raise_for_status()
    data = resp.json()
    return _fmt_result(data.get("items", []), start, data.get("total", 0), sort, fmt_webkr)


@mcp.tool()
async def naver_search_image(query: str, display: int = 10, start: int = 1, sort: str = "sim") -> str:
    """
    Search Naver Images.
    Use this when the user explicitly asks for images or visual references.
    Returns image title, direct image URL, thumbnail URL, and dimensions.

    Args:
        query (str): Search keyword
        display (int): Number of results to return (1-100, default 10)
        start (int): Pagination offset, 1-based (default 1)
        sort (str): Sort order — "sim" (relevance) or "date" (latest first)

    Returns:
        str: Formatted list of images with URLs and dimensions
    """
    try:
        from util.genos_utils import genos_import
        requests = genos_import('requests', install_name='requests')
    except Exception as e:
        return f"Error: failed to import requests — {e}"
    display = max(1, min(display, 100))
    start = max(1, min(start, 1000))
    sort = sort if sort in ("sim", "date") else "sim"
    headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
    params = {"query": query.strip(), "display": display, "start": start, "sort": sort}
    logger.info("naver_search_image query=%r display=%d start=%d sort=%s", query, display, start, sort)
    resp = requests.get(f"{NAVER_API_BASE}/image", headers=headers, params=params)
    if resp.status_code == 401:
        return "Error: Invalid Naver API credentials."
    if resp.status_code == 429:
        return "Error: Naver API rate limit exceeded. Try again later."
    resp.raise_for_status()
    data = resp.json()
    return _fmt_result(data.get("items", []), start, data.get("total", 0), sort, fmt_image)


@mcp.tool()
async def naver_search_shop(query: str, display: int = 10, start: int = 1, sort: str = "sim") -> str:
    """
    Search Naver Shopping for products and prices.
    Use this when the user asks about product prices, purchasing options, or shopping comparisons.
    Returns product name, price range, seller, and link.
    Best for queries like '아이패드 가격', '운동화 추천'.

    Args:
        query (str): Search keyword (be specific: brand + model name works best)
        display (int): Number of results to return (1-100, default 10)
        start (int): Pagination offset, 1-based (default 1)
        sort (str): Sort order — "sim" (relevance), "date" (latest), "asc" (price low→high), "dsc" (price high→low)

    Returns:
        str: Formatted list of products with prices
    """
    try:
        from util.genos_utils import genos_import
        requests = genos_import('requests', install_name='requests')
    except Exception as e:
        return f"Error: failed to import requests — {e}"
    display = max(1, min(display, 100))
    start = max(1, min(start, 1000))
    sort = sort if sort in ("sim", "date", "asc", "dsc") else "sim"
    headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
    params = {"query": query.strip(), "display": display, "start": start, "sort": sort}
    logger.info("naver_search_shop query=%r display=%d start=%d sort=%s", query, display, start, sort)
    resp = requests.get(f"{NAVER_API_BASE}/shop", headers=headers, params=params)
    if resp.status_code == 401:
        return "Error: Invalid Naver API credentials."
    if resp.status_code == 429:
        return "Error: Naver API rate limit exceeded. Try again later."
    resp.raise_for_status()
    data = resp.json()
    return _fmt_result(data.get("items", []), start, data.get("total", 0), sort, fmt_shop)


@mcp.tool()
async def naver_search_doc(query: str, display: int = 10, start: int = 1, sort: str = "sim") -> str:
    """
    Search Naver for academic papers and office documents (Korean).
    Use this when the user needs formal documents, research papers, or official reports.
    Note: returns empty results for most general queries — use only for document-specific searches.
    Returns document title, excerpt, and link.

    Args:
        query (str): Search keyword
        display (int): Number of results to return (1-100, default 10)
        start (int): Pagination offset, 1-based (default 1)
        sort (str): Sort order — "sim" (relevance) or "date" (latest first)

    Returns:
        str: Formatted list of documents
    """
    try:
        from util.genos_utils import genos_import
        requests = genos_import('requests', install_name='requests')
    except Exception as e:
        return f"Error: failed to import requests — {e}"
    display = max(1, min(display, 100))
    start = max(1, min(start, 1000))
    sort = sort if sort in ("sim", "date") else "sim"
    headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
    params = {"query": query.strip(), "display": display, "start": start, "sort": sort}
    logger.info("naver_search_doc query=%r display=%d start=%d sort=%s", query, display, start, sort)
    resp = requests.get(f"{NAVER_API_BASE}/doc", headers=headers, params=params)
    if resp.status_code == 401:
        return "Error: Invalid Naver API credentials."
    if resp.status_code == 429:
        return "Error: Naver API rate limit exceeded. Try again later."
    resp.raise_for_status()
    data = resp.json()
    return _fmt_result(data.get("items", []), start, data.get("total", 0), sort, fmt_doc)


@mcp.tool()
async def naver_search_local(query: str, display: int = 10, start: int = 1) -> str:
    """
    Search Naver Local for places, businesses, and restaurants in Korea.
    Use this when the user asks about a specific place, store, restaurant, or address.
    Query must be a place name or business name — NOT a full sentence.
    Example: query="강남 스타벅스" (not "강남에 있는 스타벅스 찾아줘").
    Returns place name, category, phone number, and address.
    Note: sort is not supported for this search type.

    Args:
        query (str): Place name or business name (short, not a sentence)
        display (int): Number of results to return (1-100, default 10)
        start (int): Pagination offset, 1-based (default 1)

    Returns:
        str: Formatted list of local places
    """
    try:
        from util.genos_utils import genos_import
        requests = genos_import('requests', install_name='requests')
    except Exception as e:
        return f"Error: failed to import requests — {e}"
    display = max(1, min(display, 100))
    start = max(1, min(start, 1000))
    headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
    params = {"query": query.strip(), "display": display, "start": start}
    logger.info("naver_search_local query=%r display=%d start=%d", query, display, start)
    resp = requests.get(f"{NAVER_API_BASE}/local", headers=headers, params=params)
    if resp.status_code == 401:
        return "Error: Invalid Naver API credentials."
    if resp.status_code == 429:
        return "Error: Naver API rate limit exceeded. Try again later."
    resp.raise_for_status()
    data = resp.json()
    return _fmt_result(data.get("items", []), start, data.get("total", 0), "n/a", fmt_local)


@mcp.tool()
async def naver_search_kin(query: str, display: int = 10, start: int = 1, sort: str = "sim") -> str:
    """
    Search Naver 지식iN (Knowledge IN) for community Q&A.
    Use this when the user wants community opinions, practical advice, or answers to specific questions.
    Returns question title, excerpt, and link.
    Best for queries seeking real user experiences or common questions.

    Args:
        query (str): Search keyword
        display (int): Number of results to return (1-100, default 10)
        start (int): Pagination offset, 1-based (default 1)
        sort (str): Sort order — "sim" (relevance), "date" (latest), "point" (most answered)

    Returns:
        str: Formatted list of Q&A results
    """
    try:
        from util.genos_utils import genos_import
        requests = genos_import('requests', install_name='requests')
    except Exception as e:
        return f"Error: failed to import requests — {e}"
    display = max(1, min(display, 100))
    start = max(1, min(start, 1000))
    sort = sort if sort in ("sim", "date", "point") else "sim"
    headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
    params = {"query": query.strip(), "display": display, "start": start, "sort": sort}
    logger.info("naver_search_kin query=%r display=%d start=%d sort=%s", query, display, start, sort)
    resp = requests.get(f"{NAVER_API_BASE}/kin", headers=headers, params=params)
    if resp.status_code == 401:
        return "Error: Invalid Naver API credentials."
    if resp.status_code == 429:
        return "Error: Naver API rate limit exceeded. Try again later."
    resp.raise_for_status()
    data = resp.json()
    return _fmt_result(data.get("items", []), start, data.get("total", 0), sort, fmt_kin)


@mcp.tool()
async def naver_search_book(query: str, display: int = 10, start: int = 1, sort: str = "sim") -> str:
    """
    Search Naver Books for Korean and international books.
    Use this when the user asks about books, authors, publishers, or ISBN.
    Returns title, author, publisher, publish date, price, and description.

    Args:
        query (str): Search keyword (book title, author name, or ISBN)
        display (int): Number of results to return (1-100, default 10)
        start (int): Pagination offset, 1-based (default 1)
        sort (str): Sort order — "sim" (relevance), "date" (latest), "count" (sales), "score" (rating)

    Returns:
        str: Formatted list of books
    """
    try:
        from util.genos_utils import genos_import
        requests = genos_import('requests', install_name='requests')
    except Exception as e:
        return f"Error: failed to import requests — {e}"
    display = max(1, min(display, 100))
    start = max(1, min(start, 1000))
    sort = sort if sort in ("sim", "date", "count", "score") else "sim"
    headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
    params = {"query": query.strip(), "display": display, "start": start, "sort": sort}
    logger.info("naver_search_book query=%r display=%d start=%d sort=%s", query, display, start, sort)
    resp = requests.get(f"{NAVER_API_BASE}/book", headers=headers, params=params)
    if resp.status_code == 401:
        return "Error: Invalid Naver API credentials."
    if resp.status_code == 429:
        return "Error: Naver API rate limit exceeded. Try again later."
    resp.raise_for_status()
    data = resp.json()
    return _fmt_result(data.get("items", []), start, data.get("total", 0), sort, fmt_book)


@mcp.tool()
async def naver_search_cafe(query: str, display: int = 10, start: int = 1, sort: str = "sim") -> str:
    """
    Search Naver Cafe for community forum posts.
    Use this when the user wants niche community discussions, enthusiast forums, or group-specific posts.
    Returns post title, cafe name, excerpt, and link.
    Best for hobbyist, investment, or fan community topics.

    Args:
        query (str): Search keyword
        display (int): Number of results to return (1-100, default 10)
        start (int): Pagination offset, 1-based (default 1)
        sort (str): Sort order — "sim" (relevance) or "date" (latest first)

    Returns:
        str: Formatted list of cafe posts
    """
    try:
        from util.genos_utils import genos_import
        requests = genos_import('requests', install_name='requests')
    except Exception as e:
        return f"Error: failed to import requests — {e}"
    display = max(1, min(display, 100))
    start = max(1, min(start, 1000))
    sort = sort if sort in ("sim", "date") else "sim"
    headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
    params = {"query": query.strip(), "display": display, "start": start, "sort": sort}
    logger.info("naver_search_cafe query=%r display=%d start=%d sort=%s", query, display, start, sort)
    resp = requests.get(f"{NAVER_API_BASE}/cafearticle", headers=headers, params=params)
    if resp.status_code == 401:
        return "Error: Invalid Naver API credentials."
    if resp.status_code == 429:
        return "Error: Naver API rate limit exceeded. Try again later."
    resp.raise_for_status()
    data = resp.json()
    return _fmt_result(data.get("items", []), start, data.get("total", 0), sort, fmt_cafearticle)
