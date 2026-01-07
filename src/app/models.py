# app/models.py
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from app.db import dt_to_str, str_to_dt

@dataclass
class User:
    id: str     # email
    name: str

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "name": self.name}

    @staticmethod
    def from_dict(d: dict[str, Any]) -> "User":
        return User(id=d["id"], name=d["name"])


@dataclass
class Device:
    id: int
    name: str
    responsible_user_id: str
    creation_date: datetime
    last_update: datetime
    end_of_life: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "responsible_user_id": self.responsible_user_id,
            "creation_date": dt_to_str(self.creation_date),
            "last_update": dt_to_str(self.last_update),
            "end_of_life": dt_to_str(self.end_of_life),
        }

    @staticmethod
    def from_dict(d: dict[str, Any]) -> "Device":
        return Device(
            id=int(d["id"]),
            name=d["name"],
            responsible_user_id=d["responsible_user_id"],
            creation_date=str_to_dt(d["creation_date"]),
            last_update=str_to_dt(d["last_update"]),
            end_of_life=str_to_dt(d.get("end_of_life")),
        )
