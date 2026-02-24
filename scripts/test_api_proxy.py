"""Quick script to verify Naver API credentials + proxy/NTLM config for all search types."""
import json
import os
import warnings

import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

PROXY_DEV = os.getenv("PROXY_DEV", "")
PROXY_NTLM_DOMAIN = os.getenv("PROXY_NTLM_DOMAIN", "")
PROXY_NTLM_USER = os.getenv("PROXY_NTLM_USER", "")
PROXY_NTLM_PASS = os.getenv("PROXY_NTLM_PASS", "")

NAVER_API_BASE = "https://openapi.naver.com/v1/search"
SEARCH_TYPES = ["news", "blog", "webkr", "image", "shop", "doc", "local", "kin", "book", "cafearticle"]

def build_session() -> requests.Session:
    session = requests.Session()
    session.verify = False
    # warnings.filterwarnings("ignore", message="Unverified HTTPS request")
    # try:
    #     import urllib3
    #     urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    # except ImportError:
    #     pass

    if PROXY_DEV:
        session.proxies = {"http": PROXY_DEV, "https": PROXY_DEV}
        print(f"[proxy]  {PROXY_DEV}")
    else:
        print("[proxy]  None (system default)")

    if PROXY_NTLM_DOMAIN and PROXY_NTLM_USER:
        try:
            from requests_ntlm import HttpNtlmAuth
            session.auth = HttpNtlmAuth(
                f"{PROXY_NTLM_DOMAIN}\\{PROXY_NTLM_USER}",
                PROXY_NTLM_PASS or "",
            )
            print(f"[auth]   NTLM — {PROXY_NTLM_DOMAIN}\\{PROXY_NTLM_USER}")
        except ImportError:
            print("[auth]   NTLM requested but requests_ntlm not installed — skipping")
    else:
        print("[auth]   None")

    return session


def test_search(session: requests.Session, search_type: str, query: str):
    url = f"{NAVER_API_BASE}/{search_type}"
    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET,
    }
    params = {"query": query, "display": 2}

    print(f"\n{'='*60}")
    print(f"TYPE: {search_type} | url: {url}")
    print(f"{'='*60}")

    try:
        resp = session.get(url, headers=headers, params=params, timeout=60)
        print(f"status: {resp.status_code}")
        if resp.status_code == 200:
            print(json.dumps(resp.json(), ensure_ascii=False, indent=2))
        else:
            print(f"ERROR: {resp.text}")
    except Exception as e:
        print(f"EXCEPTION: {e}")


def main():
    if not CLIENT_ID or not CLIENT_SECRET:
        print("ERROR: NAVER_CLIENT_ID or NAVER_CLIENT_SECRET not set in .env")
        return

    print(f"[creds]  Client ID: {CLIENT_ID[:6]}... (loaded)")
    session = build_session()

    query = "탁구 횡회전 서브 주는법"
    for search_type in SEARCH_TYPES:
        test_search(session, search_type, query)


if __name__ == "__main__":
    main()
