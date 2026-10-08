import sqlite3
import sys

from app.contacts import find_contacts
from app.db import connect
from app.search import tavily_search

# (query template, tavily topic, fact kind)
QUERIES = [
    ('"{name}" interview OR podcast', "general", "podcast_appearance"),
    ('"{name}" news', "news", "news"),
    ('"{name}" upcoming event OR speaking OR book launch', "general", "event"),
]


def lookup(conn: sqlite3.Connection, name: str, search=tavily_search) -> int:
    """Search public sources for a name and store results as facts. Returns new fact count."""
    conn.execute("INSERT OR IGNORE INTO person(name) VALUES (?)", (name,))
    person_id = conn.execute("SELECT id FROM person WHERE name = ?", (name,)).fetchone()["id"]
    added = 0
    for template, topic, kind in QUERIES:
        for r in search(template.format(name=name), topic=topic):
            cur = conn.execute(
                "INSERT OR IGNORE INTO fact(person_id, kind, summary, url, published_at) VALUES (?,?,?,?,?)",
                (person_id, kind, f"{r.get('title', '')}: {r.get('content', '')}"[:1000],
                 r.get("url"), r.get("published_date")),
            )
            added += cur.rowcount
    conn.commit()
    find_contacts(conn, person_id, name, search=search)
    return added


def main() -> None:
    name = " ".join(sys.argv[1:]).strip()
    if not name:
        sys.exit("usage: python -m app.lookup <name>")
    conn = connect()
    added = lookup(conn, name)
    print(f"{name}: {added} new facts")
    print("Contacts:")
    for c in conn.execute("SELECT email, role, role_note, source_url FROM contact WHERE person_id = (SELECT id FROM person WHERE name = ?)", (name,)):
        print(f"  [{c['role']}] {c['email']}  ({c['role_note']})  {c['source_url']}")
    for row in conn.execute(
        "SELECT kind, summary, url FROM fact WHERE person_id = (SELECT id FROM person WHERE name = ?) ORDER BY kind",
        (name,),
    ):
        print(f"[{row['kind']}] {row['summary'][:120]}\n    {row['url']}")


if __name__ == "__main__":
    main()
