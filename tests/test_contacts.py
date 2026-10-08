from app.contacts import extract_contacts


def test_extracts_and_labels_roles():
    text = "For press inquiries email jo@pr-firm.com. Booking agent: agent@talent.com. Questions: hi@site.org. Junk: noreply@x.com logo@2x.png"
    got = {e: r for e, r, _ in extract_contacts(text)}
    assert got["jo@pr-firm.com"] == "publicist"
    assert got["agent@talent.com"] == "agent"
    assert "noreply@x.com" not in got and "logo@2x.png" not in got
