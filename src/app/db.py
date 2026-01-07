# app/db.py
from __future__ import annotations
from dataclasses import dataclass
from tinydb import TinyDB
from pathlib import Path
from datetime import datetime, timezone

DB_FILE = Path(__file__).resolve().parents[2] / "database.json"

def get_db() -> TinyDB:
    return TinyDB(DB_FILE)


def now_utc() -> datetime:
    return datetime.now(timezone.utc)

def dt_to_str(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    return dt.astimezone(timezone.utc).isoformat()

def str_to_dt(s: str | None) -> datetime | None:
    if not s:
        return None
    # isoformat mit timezone wird sauber geparst
    return datetime.fromisoformat(s)

@dataclass
class _DBHolder:
    db: TinyDB

_db_holder: _DBHolder | None = None

def get_db() -> TinyDB:
    """Simple Singleton für TinyDB."""
    global _db_holder
    if _db_holder is None:
        _db_holder = _DBHolder(db=TinyDB(DB_FILE))
    return _db_holder.db
