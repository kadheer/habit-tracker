# Habit Tracker

Ein einfacher Habit-Tracker mit Flask, SQLite und einem
schlanken HTML/CSS-Frontend.

![CI](https://github.com/kadheer/habit-tracker/actions/workflows/ci.yaml/badge.svg)

## Features

- Habits anlegen
- Habits fuer heute abhaken
- Streak pro Habit
- Health-Endpoint fuer Docker

## Stack

- Python 3.11
- Flask
- SQLAlchemy + SQLite
- HTML/CSS (kein Framework)
- Docker

## Lokal starten

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
python -m app.main
