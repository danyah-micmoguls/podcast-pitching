import os

import httpx

TAVILY_URL = "https://api.tavily.com/search"


def tavily_search(query: str, topic: str = "general", max_results: int = 8, raw: bool = False) -> list[dict]:
    key = os.environ.get("TAVILY_API_KEY")
    if not key:
        raise RuntimeError("Set TAVILY_API_KEY (free key at tavily.com)")
    resp = httpx.post(
        TAVILY_URL,
        headers={"Authorization": f"Bearer {key}"},
        json={"query": query, "topic": topic, "max_results": max_results,
              "include_raw_content": "text" if raw else False},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json().get("results", [])
