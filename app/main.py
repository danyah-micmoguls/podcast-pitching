from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.crossover import crossover_candidates, neighbors
from app.db import connect
from app.lookup import lookup

app = FastAPI(title="Podcast Pitching")
STATIC = Path(__file__).parent / "static"


def db():
    return connect()


class LookupBody(BaseModel):
    name: str


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/api/people")
def people():
    conn = db()
    rows = conn.execute(
        """SELECT p.id, p.name, p.field,
                  (SELECT COUNT(*) FROM fact f WHERE f.person_id = p.id) AS facts,
                  (SELECT COUNT(*) FROM contact c WHERE c.person_id = p.id) AS contacts
           FROM person p ORDER BY p.name"""
    ).fetchall()
    return [dict(r) for r in rows]


@app.post("/api/lookup")
def run_lookup(body: LookupBody):
    name = body.name.strip()
    if not name:
        raise HTTPException(400, "name required")
    conn = db()
    try:
        added = lookup(conn, name)
    except RuntimeError as e:
        raise HTTPException(503, str(e))
    pid = conn.execute("SELECT id FROM person WHERE name = ?", (name,)).fetchone()["id"]
    return {"id": pid, "added": added}


@app.get("/api/person/{person_id}")
def person(person_id: int):
    conn = db()
    p = conn.execute("SELECT * FROM person WHERE id = ?", (person_id,)).fetchone()
    if not p:
        raise HTTPException(404, "not found")
    q = lambda sql: [dict(r) for r in conn.execute(sql, (person_id,))]
    return {
        "person": dict(p),
        "contacts": q("SELECT email, role, role_note, source_url, verified FROM contact WHERE person_id = ?"),
        "facts": q("SELECT kind, summary, url, published_at FROM fact WHERE person_id = ? ORDER BY kind, published_at DESC"),
        "pitches": q(
            """SELECT c.name AS client, s.title AS show_title, pi.status, pi.angle
               FROM pitch pi JOIN show s ON s.id = pi.show_id JOIN client c ON c.id = s.client_id
               WHERE pi.person_id = ?"""
        ),
        "connections": [dict(r) for r in neighbors(conn, person_id)],
    }


@app.get("/api/graph")
def graph():
    conn = db()
    nodes = [{"id": f"p{r['id']}", "label": r["name"], "group": "person", "pid": r["id"]}
             for r in conn.execute("SELECT id, name FROM person")]
    nodes += [{"id": f"c{r['id']}", "label": r["name"], "group": "client"}
              for r in conn.execute("SELECT id, name FROM client")]
    edges = [{"from": f"p{r['person_a']}", "to": f"p{r['person_b']}", "label": r["relation"]}
             for r in conn.execute("SELECT person_a, person_b, relation FROM connection")]
    edges += [{"from": f"c{r['client_id']}", "to": f"p{r['person_id']}", "label": r["status"], "dashes": True}
              for r in conn.execute(
                  """SELECT DISTINCT s.client_id, pi.person_id, pi.status
                     FROM pitch pi JOIN show s ON s.id = pi.show_id""")]
    return {"nodes": nodes, "edges": edges}


@app.get("/api/crossover/{client_id}")
def crossover(client_id: int):
    return [dict(r) for r in crossover_candidates(db(), client_id)]
