"""Load fake demo data so the dashboard has something to show. Safe to re-run."""
from app.db import connect


def seed(conn):
    conn.executescript(
        """
        INSERT OR IGNORE INTO client(id, name) VALUES (1, 'Client Alpha'), (2, 'Client Beta');
        INSERT OR IGNORE INTO show(id, client_id, title, topics) VALUES
          (1, 1, 'The Founder Hour', 'startups, leadership'),
          (2, 2, 'Wellness Weekly', 'health, coaching');
        INSERT OR IGNORE INTO person(id, name, field, bio) VALUES
          (1, 'Demo Dana', 'Executive coach', 'DEMO DATA. Coach and author.'),
          (2, 'Demo Marcus', 'Venture investor', 'DEMO DATA. Early-stage investor.'),
          (3, 'Demo Priya', 'Wellness founder', 'DEMO DATA. Founded a wellness brand.');
        INSERT OR IGNORE INTO contact(person_id, email, role, role_note) VALUES
          (1, 'agent@example.com', 'agent', 'Handles all media bookings'),
          (1, 'dana@example.com', 'business', 'Speaking and coaching inquiries'),
          (2, 'press@example.com', 'publicist', 'Podcast and press requests');
        INSERT OR IGNORE INTO fact(person_id, kind, summary, url) VALUES
          (1, 'news', 'DEMO: Dana announces new book on leadership', 'https://example.com/1'),
          (1, 'event', 'DEMO: Dana keynoting a summit next month', 'https://example.com/2'),
          (2, 'podcast_appearance', 'DEMO: Marcus on a fundraising podcast', 'https://example.com/3');
        INSERT OR IGNORE INTO pitch(person_id, show_id, status, angle) VALUES
          (1, 1, 'booked', 'New book tie-in'), (2, 1, 'replied', 'Fundraising lessons'),
          (3, 2, 'sent', 'Brand founder story');
        INSERT OR IGNORE INTO connection(person_a, person_b, relation) VALUES
          (1, 2, 'co_guest'), (2, 3, 'collaborator');
        """
    )
    conn.commit()


if __name__ == "__main__":
    seed(connect())
    print("Demo data loaded.")
