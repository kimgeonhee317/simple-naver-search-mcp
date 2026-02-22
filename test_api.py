"""Quick script to verify Naver API credentials and print raw responses for all search types."""
import asyncio
import json
import os
from dotenv import load_dotenv
import httpx

load_dotenv()

CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

SEARCH_TYPES = ["news", "blog", "webkr", "image", "shop", "doc", "local", "kin", "book", "cafearticle"]


async def test_search(client: httpx.AsyncClient, search_type: str, query: str):
    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET,
    }
    url = f"https://openapi.naver.com/v1/search/{search_type}"
    response = await client.get(url, headers=headers, params={"query": query, "display": 2})

    print(f"{'='*60}")
    print(f"TYPE: {search_type} | status: {response.status_code}")
    print(f"{'='*60}")
    if response.status_code == 200:
        print(json.dumps(response.json(), ensure_ascii=False, indent=2))
    else:
        print(f"ERROR: {response.text}")
    print()


async def main():
    if not CLIENT_ID or not CLIENT_SECRET:
        print("ERROR: NAVER_CLIENT_ID or NAVER_CLIENT_SECRET not set in .env")
        return

    print(f"Client ID: {CLIENT_ID[:6]}... (loaded)\n")

    query = "래미안아름숲 부동산 전망"
    async with httpx.AsyncClient() as client:
        for search_type in SEARCH_TYPES:
            await test_search(client, search_type, query)


if __name__ == "__main__":
    asyncio.run(main())
