from app.db import connect
from app.lookup import lookup


def fake_search(query, topic="general", max_results=8, raw=False):
    return [{"title": "T", "content": f"about {topic}", "url": f"https://x.com/{topic}"}]


def test_lookup_stores_facts_and_dedupes():
    conn = connect(":memory:")
    assert lookup(conn, "Ann Lee", search=fake_search) == 2  # general url shared by two queries
    assert lookup(conn, "Ann Lee", search=fake_search) == 0
    kinds = {r["kind"] for r in conn.execute("SELECT kind FROM fact")}
    assert kinds == {"podcast_appearance", "news"}
