import sqlite3


def crossover_candidates(conn: sqlite3.Connection, client_id: int) -> list[sqlite3.Row]:
    """People already pitched or booked for other clients' shows, not yet pitched to this client."""
    return conn.execute(
        """
        SELECT DISTINCT p.id, p.name, c.name AS from_client, pi.status
        FROM pitch pi
        JOIN show s ON s.id = pi.show_id
        JOIN client c ON c.id = s.client_id
        JOIN person p ON p.id = pi.person_id
        WHERE s.client_id <> ?
          AND pi.status IN ('replied', 'booked')
          AND p.id NOT IN (
              SELECT pi2.person_id FROM pitch pi2
              JOIN show s2 ON s2.id = pi2.show_id
              WHERE s2.client_id = ?
          )
        ORDER BY p.name
        """,
        (client_id, client_id),
    ).fetchall()


def neighbors(conn: sqlite3.Connection, person_id: int) -> list[sqlite3.Row]:
    """People directly connected to this person, regardless of edge direction."""
    return conn.execute(
        """
        SELECT p.id, p.name, cn.relation, cn.evidence_url
        FROM connection cn
        JOIN person p ON p.id = CASE WHEN cn.person_a = :id THEN cn.person_b ELSE cn.person_a END
        WHERE cn.person_a = :id OR cn.person_b = :id
        ORDER BY p.name
        """,
        {"id": person_id},
    ).fetchall()
