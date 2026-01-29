from __future__ import annotations
from datetime import datetime
from typing import Any, Dict
from uuid import uuid4
from serializable import Serializable


class Reservation(Serializable):
    table_name = "reservations"

    def __init__(
        self,
        user_id: str,
        device_id: int,
        start_date: datetime,
        end_date: datetime,
        id: str | None = None,
    ):
        super().__init__(id=id or str(uuid4()))
        self.user_id = user_id
        self.device_id = int(device_id)
        self.start_date = start_date
        self.end_date = end_date

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "device_id": self.device_id,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "creation_date": self.creation_date,
            "last_update": self.last_update,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Reservation":
        obj = cls(
            id=data.get("id"),
            user_id=data["user_id"],
            device_id=int(data["device_id"]),
            start_date=data["start_date"],
            end_date=data["end_date"],
        )
        obj.creation_date = data.get("creation_date", datetime.now())
        obj.last_update = data.get("last_update", datetime.now())
        return obj