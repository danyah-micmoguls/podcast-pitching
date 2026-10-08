import app.main as m
from app.db import connect
from app.seed_demo import seed
from fastapi.testclient import TestClient


def test_graph_and_person(tmp_path, monkeypatch):
    path = tmp_path / "t.db"
    seed(connect(path))
    monkeypatch.setattr(m, "db", lambda: connect(path))
    c = TestClient(m.app)
    g = c.get("/api/graph").json()
    assert len(g["nodes"]) == 5 and len(g["edges"]) >= 5
    d = c.get("/api/person/1").json()
    assert {x["role"] for x in d["contacts"]} == {"agent", "business"}
    assert c.get("/api/person/99").status_code == 404
    assert c.get("/").status_code == 200
