# src/db.py
import os
from datetime import datetime, timezone

from tinydb import TinyDB
from tinydb.table import Table
from tinydb_serialization import SerializationMiddleware
from tinydb_serialization.serializers import DateTimeSerializer
from tinydb.storages import JSONStorage


DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.json")

# Serializer (datetime)

serializer = SerializationMiddleware(JSONStorage)
serializer.register_serializer(DateTimeSerializer(), "TinyDateTime")


_DB = TinyDB(DB_FILE, storage=serializer)


def get_db() -> TinyDB:
    """Return shared TinyDB instance."""
    return _DB


def now_utc() -> datetime:
    """Zeitstempel für creation_date/last_update (timezone-aware)."""
    return datetime.now(timezone.utc)



class DatabaseConnector:
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.path = DB_FILE
        return cls.__instance

    def get_table(self, table_name: str) -> Table:
        return TinyDB(self.path, storage=serializer).table(table_name)
