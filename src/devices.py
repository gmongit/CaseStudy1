# src/devices.py
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from serializable import Serializable


class Device(Serializable):
    table_name = "devices"

    def __init__(
        self,
        id: str,
        name: str,
        responsible_user_id: str,
        is_active: bool = True,
        end_of_life: Optional[datetime] = None,
    ):
        super().__init__(id=id)
        self.name = name
        self.responsible_user_id = responsible_user_id
        self.is_active = is_active
        self.end_of_life = end_of_life

    def set_responsible_user_id(self, user_id: str) -> None:
        self.responsible_user_id = user_id

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": int(self.id) if str(self.id).isdigit() else self.id,
            "name": self.name,
            "responsible_user_id": self.responsible_user_id,
            "is_active": self.is_active,
            "end_of_life": self.end_of_life,
            "creation_date": self.creation_date,
            "last_update": self.last_update,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Device":
        obj = cls(
            id=str(data["id"]),
            name=data.get("name", ""),
            responsible_user_id=data.get("responsible_user_id", ""),
            is_active=data.get("is_active", True),
            end_of_life=data.get("end_of_life", None),
        )
        obj.creation_date = data.get("creation_date", datetime.now())
        obj.last_update = data.get("last_update", datetime.now())
        return obj
