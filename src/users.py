# src/users.py
from __future__ import annotations
from typing import Any, Dict
from datetime import datetime

from serializable import Serializable  # <-- ohne src.

class User(Serializable):
    table_name = "users"

    def __init__(self, id: str, name: str):
        super().__init__(id=id)
        self.name = name

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "creation_date": self.creation_date,
            "last_update": self.last_update,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        obj = cls(id=data["id"], name=data["name"])
        obj.creation_date = data.get("creation_date", datetime.now())
        obj.last_update = data.get("last_update", datetime.now())
        return obj
