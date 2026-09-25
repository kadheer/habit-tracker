"""
Habit Tracker - Hauptanwendung.

Drei Endpunkte:
  GET  /               -> HTML-Seite
  POST /habits         -> neuen Habit anlegen
  POST /habits/<id>/done -> Habit fuer heute abhaken
"""

import os
from datetime import date, timedelta

from flask import Flask, render_template, request, redirect, url_for, jsonify

from app.database import Base, engine, SessionLocal
from app.models import Habit


# Flask sucht standardmaessig im Verzeichnis von main.py nach
# templates/ und static/. Da unsere Ordner aber im Projekt-Root
# liegen (eine Ebene hoeher), muessen wir den Pfad explizit setzen.
# Sonst gibt's "TemplateNotFound: index.html".
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
)

# Beim Start die Tabellen anlegen, falls sie noch nicht existieren.
Base.metadata.create_all(bind=engine)


@app.route("/")
def index():
    """Startseite mit Liste aller Habits."""
    db = SessionLocal()
    try:
        habits = db.query(Habit).order_by(Habit.created_at.desc()).all()
        # today wird im Template gebraucht, um den Done-Status anzuzeigen.
        return render_template("index.html", habits=habits, today=date.today())
    finally:
        db.close()


@app.route("/health")
def health():
    """Health-Endpoint fuer Docker/Kubernetes."""
    return jsonify(status="ok")


@app.route("/habits", methods=["POST"])
def add_habit():
    """Neuen Habit anlegen. Der Name kommt aus dem Formular."""
    name = request.form.get("name", "").strip()

    if not name:
        return redirect(url_for("index"))

    db = SessionLocal()
    try:
        habit = Habit(name=name, created_at=date.today())
        db.add(habit)
        db.commit()
    finally:
        db.close()

    return redirect(url_for("index"))


@app.route("/habits/<int:habit_id>/done", methods=["POST"])
def mark_done(habit_id):
    """
    Habit fuer heute abhaken.
    Wenn schon heute abgehakt: nichts aendern.
    Wenn gestern abgehakt: Streak erhoehen.
    Sonst: Streak auf 1 setzen.
    """
    db = SessionLocal()
    try:
        habit = db.query(Habit).filter(Habit.id == habit_id).first()
        if not habit:
            return redirect(url_for("index"))

        today = date.today()

        # Schon heute abgehakt? Nichts tun.
        if habit.last_done == today:
            return redirect(url_for("index"))

        # Gestern abgehakt? Streak erhoehen.
        if habit.last_done == today - timedelta(days=1):
            habit.streak += 1
        else:
            habit.streak = 1

        habit.last_done = today
        db.commit()
    finally:
        db.close()

    return redirect(url_for("index"))


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
