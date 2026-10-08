import os
import sqlite3
from pathlib import Path


def load_env(path: str | Path = ".env") -> None:
    f = Path(path)
    if not f.exists():
        return
    for line in f.read_text().splitlines():
        k, sep, v = line.partition("=")
        if sep and not line.lstrip().startswith("#"):
            os.environ.setdefault(k.strip(), v.strip())


load_env()

SCHEMA = """
CREATE TABLE IF NOT EXISTS person (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    field TEXT,
    bio TEXT,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Every contact path, labeled by what that contact does for the person.
CREATE TABLE IF NOT EXISTS contact (
    id INTEGER PRIMARY KEY,
    person_id INTEGER NOT NULL REFERENCES person(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    role TEXT NOT NULL,            -- personal | business | agent | publicist | manager | assistant
    role_note TEXT,                -- what this contact handles for them
    source_url TEXT,
    verified INTEGER DEFAULT 0,
    UNIQUE (person_id, email)
);

-- Raw public facts, each tied to a source so pitches can cite them.
CREATE TABLE IF NOT EXISTS fact (
    id INTEGER PRIMARY KEY,
    person_id INTEGER NOT NULL REFERENCES person(id) ON DELETE CASCADE,
    kind TEXT NOT NULL,            -- social | news | event | press | podcast_appearance | other
    summary TEXT NOT NULL,
    url TEXT,
    published_at TEXT,
    fetched_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (person_id, url)
);

CREATE TABLE IF NOT EXISTS client (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    clickup_id TEXT
);

CREATE TABLE IF NOT EXISTS show (
    id INTEGER PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES client(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    topics TEXT,
    audience TEXT,
    UNIQUE (client_id, title)
);

-- Tracks who was pitched for which show, powering cross-client reuse.
CREATE TABLE IF NOT EXISTS pitch (
    id INTEGER PRIMARY KEY,
    person_id INTEGER NOT NULL REFERENCES person(id),
    show_id INTEGER NOT NULL REFERENCES show(id),
    status TEXT NOT NULL DEFAULT 'draft',  -- draft | sent | replied | booked | declined
    angle TEXT,
    clickup_task_id TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (person_id, show_id)
);

-- Who knows who. Directional edge, stored once per pair in either direction.
CREATE TABLE IF NOT EXISTS connection (
    id INTEGER PRIMARY KEY,
    person_a INTEGER NOT NULL REFERENCES person(id) ON DELETE CASCADE,
    person_b INTEGER NOT NULL REFERENCES person(id) ON DELETE CASCADE,
    relation TEXT NOT NULL,        -- co_guest | host_guest | business_partner | collaborator | other
    evidence_url TEXT,
    UNIQUE (person_a, person_b, relation),
    CHECK (person_a <> person_b)
);
"""


def connect(path: str | Path = "pitching.db") -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    return conn
