"""
Datenbank-Modell. Nur eine Tabelle, weil das Projekt klein ist.
"""

from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Date
from app.database import Base


class Habit(Base):
    __tablename__ = "habits"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    created_at = Column(Date, default=date.today)

    # Datum, an dem das letzte Mal abgehakt wurde.
    # Null bedeutet: noch nie abgehakt.
    last_done = Column(Date, nullable=True)

    # Streak in Tagen. Wird beim Abhaken hochgezaehlt.
    streak = Column(Integer, default=0)
