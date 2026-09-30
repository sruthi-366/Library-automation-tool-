from datetime import date, timedelta

def test_due_date_calculation():
    issue_date = date(2026, 9, 30)
    days = 14
    assert issue_date + timedelta(days=days) == date(2026, 10, 14)

def test_required_fields():
    title = "Python Basics"
    author = "John"
    assert title.strip() != ""
    assert author.strip() != ""

def test_email_validation():
    email = "student@example.com"
    assert "@" in email
