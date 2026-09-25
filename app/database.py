"""
Datenbank-Setup. SQLite, weil's am einfachsten ist.
In den Tests wird eine In-Memory-DB benutzt, im Betrieb
eine Datei namens habits.db.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./habits.db")

# check_same_thread nur fuer SQLite noetig, nicht fuer Postgres.
# Hab das hier abgefragt, falls spaeter mal auf Postgres umgestellt wird.
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_db():
    """FastAPI/Flask-Helper: gibt eine Session und raeumt danach auf."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
