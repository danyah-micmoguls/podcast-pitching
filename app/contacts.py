import re
import sqlite3

from app.search import tavily_search

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")
JUNK_DOMAINS = {"example.com", "domain.com", "email.com", "sentry.io", "wixpress.com"}
JUNK_PREFIX = ("noreply", "no-reply", "donotreply", "unsubscribe", "privacy", "abuse", "webmaster")
JUNK_SUFFIX = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".css", ".js")

# keyword found near the email -> (role, plain-English note)
ROLES = [
    (("publicist", "pr ", "press", "media inquir"), "publicist", "Handles press and media requests"),
    (("agent", "agency", "represent", "booking", "speaking"), "agent", "Handles bookings and speaking requests"),
    (("manage", "management"), "manager", "Manages their business and schedule"),
    (("assistant", "scheduling"), "assistant", "Handles scheduling"),
]

QUERIES = [
    '"{name}" booking agent OR publicist OR management contact email',
    '"{name}" official website contact media inquiries',
]


def classify(context: str) -> tuple[str, str]:
    c = context.lower()
    for keys, role, note in ROLES:
        if any(k in c for k in keys):
            return role, note
    return "unlabeled", "Found publicly, purpose unclear. Check source."


def extract_contacts(text: str, window: int = 45) -> list[tuple[str, str, str]]:
    found = []
    for m in EMAIL.finditer(text):
        email = m.group(0).lower().rstrip(".")
        domain = email.split("@")[1]
        if domain in JUNK_DOMAINS or email.startswith(JUNK_PREFIX) or email.endswith(JUNK_SUFFIX):
            continue
        ctx = text[max(0, m.start() - window): m.end() + 15]
        role, note = classify(ctx)
        found.append((email, role, note))
    return found


def find_contacts(conn: sqlite3.Connection, person_id: int, name: str, search=tavily_search) -> int:
    """Pull publicly listed emails from search results. Never guesses addresses."""
    added = 0
    for template in QUERIES:
        for r in search(template.format(name=name), raw=True):
            text = (r.get("raw_content") or "") + " " + (r.get("content") or "")
            for email, role, note in extract_contacts(text):
                cur = conn.execute(
                    "INSERT OR IGNORE INTO contact(person_id, email, role, role_note, source_url) VALUES (?,?,?,?,?)",
                    (person_id, email, role, note, r.get("url")),
                )
                added += cur.rowcount
    conn.commit()
    return added
