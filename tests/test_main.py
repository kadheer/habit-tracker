"""
Tests fuer den Habit Tracker.

Ich hab die Tests bewusst einfach gehalten - kein Mocking,
keine Fixtures-Akrobatik. In-Memory-SQLite, fertig.
"""

import os

# WICHTIG: Muss gesetzt sein, BEVOR app importiert wird.
# Sonst legt SQLAlchemy eine Datei namens habits.db an.
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest
from app.main import app
from app.database import Base, engine, SessionLocal
from app.models import Habit


@pytest.fixture
def client():
    """Frischer Test-Client mit sauberer DB."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_health(client):
    """Health-Endpoint muss immer 200 zurueckgeben."""
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"


def test_index_empty(client):
    """Startseite ohne Habits zeigt den Hinweis."""
    r = client.get("/")
    assert r.status_code == 200
    assert b"noch keine" in r.data.lower() or b"Habit" in r.data


def test_add_habit(client):
    """Neuen Habit anlegen, danach in der DB pruefen."""
    r = client.post("/habits", data={"name": "Lesen"}, follow_redirects=True)
    assert r.status_code == 200

    db = SessionLocal()
    try:
        habits = db.query(Habit).all()
        assert len(habits) == 1
        assert habits[0].name == "Lesen"
    finally:
        db.close()


def test_add_empty_habit_is_ignored(client):
    """Leerer Name darf keinen Habit anlegen."""
    client.post("/habits", data={"name": "   "}, follow_redirects=True)

    db = SessionLocal()
    try:
        assert db.query(Habit).count() == 0
    finally:
        db.close()


def test_mark_done_sets_streak(client):
    """Erstes Abhaken setzt den Streak auf 1."""
    client.post("/habits", data={"name": "Sport"}, follow_redirects=True)

    db = SessionLocal()
    try:
        habit_id = db.query(Habit).first().id
    finally:
        db.close()

    client.post(f"/habits/{habit_id}/done", follow_redirects=True)

    db = SessionLocal()
    try:
        habit = db.query(Habit).first()
        assert habit.streak == 1
    finally:
        db.close()


def test_mark_done_twice_does_nothing(client):
    """Zweimal am selben Tag abhaken erhoeht den Streak nicht."""
    client.post("/habits", data={"name": "Wasser trinken"}, follow_redirects=True)

    db = SessionLocal()
    try:
        habit_id = db.query(Habit).first().id
    finally:
        db.close()

    client.post(f"/habits/{habit_id}/done", follow_redirects=True)
    client.post(f"/habits/{habit_id}/done", follow_redirects=True)

    db = SessionLocal()
    try:
        habit = db.query(Habit).first()
        assert habit.streak == 1
    finally:
        db.close()
