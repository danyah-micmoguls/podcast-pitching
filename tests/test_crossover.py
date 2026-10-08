from app.crossover import crossover_candidates, neighbors
from app.db import connect


def seed(conn):
    conn.execute("INSERT INTO client(name) VALUES ('A'), ('B')")
    conn.execute("INSERT INTO show(client_id, title) VALUES (1, 'Show A'), (2, 'Show B')")
    conn.execute("INSERT INTO person(name) VALUES ('Ann'), ('Bo'), ('Cy')")
    conn.execute("INSERT INTO pitch(person_id, show_id, status) VALUES (1, 1, 'booked'), (2, 1, 'draft'), (3, 1, 'replied'), (3, 2, 'sent')")
    conn.execute("INSERT INTO connection(person_a, person_b, relation) VALUES (1, 2, 'co_guest')")


def test_crossover_excludes_drafts_and_already_pitched():
    conn = connect(":memory:")
    seed(conn)
    names = [r["name"] for r in crossover_candidates(conn, client_id=2)]
    assert names == ["Ann"]


def test_neighbors_work_in_both_directions():
    conn = connect(":memory:")
    seed(conn)
    assert [r["name"] for r in neighbors(conn, 1)] == ["Bo"]
    assert [r["name"] for r in neighbors(conn, 2)] == ["Ann"]
