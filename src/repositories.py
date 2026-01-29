# app/repositories.py
from __future__ import annotations

from tinydb import Query
from db import get_db, now_utc
from users import User
from devices import Device



class UserRepo:
    def __init__(self) -> None:
        self.table = get_db().table("users")

    def upsert(self, user: User) -> None:
        q = Query()
        self.table.upsert(user.to_dict(), q.id == user.id)

    def get(self, user_id: str) -> User | None:
        q = Query()
        d = self.table.get(q.id == user_id)
        return User.from_dict(d) if d else None

    def list_all(self) -> list[User]:
        return [User.from_dict(d) for d in self.table.all()]

    def delete(self, user_id: str) -> None:
        q = Query()
        self.table.remove(q.id == user_id)


class DeviceRepo:
    """
    Geräte-Repo auf TinyDB-Basis.

    Business-Rule:
      - Inventarnummern sind auf 1..20 beschränkt.
      - create() darf keine bereits vergebene ID anlegen.
      - update() erhält creation_date, aktualisiert last_update.
    """
    MAX_IDS = 20

    def __init__(self) -> None:
        self.table = get_db().table("devices")
        self.user_repo = UserRepo()

    # ---------- helpers ----------
    @classmethod
    def _validate_id(cls, device_id: int) -> None:
        if not (1 <= int(device_id) <= cls.MAX_IDS):
            raise ValueError(f"Inventarnummer muss zwischen 1 und {cls.MAX_IDS} liegen.")

    def existing_ids(self) -> set[int]:
        return {int(d["id"]) for d in self.table.all() if d.get("id") is not None}

    def free_ids(self) -> list[int]:
        existing = self.existing_ids()
        return [i for i in range(1, self.MAX_IDS + 1) if i not in existing]

    # ---------- CRUD ----------
    def create(self, device: Device) -> None:
        device.id = int(device.id)
        self._validate_id(device.id)

        # Verantwortliche Person muss existieren
        if self.user_repo.get(device.responsible_user_id) is None:
            raise ValueError("Verantwortliche Person existiert nicht (User zuerst anlegen).")

        q = Query()
        if self.table.get(q.id == int(device.id)) is not None:
            raise ValueError("Inventarnummer bereits vergeben.")

        device.creation_date = now_utc()
        device.last_update = now_utc()
        self.table.insert(device.to_dict())

    def update(self, device: Device) -> None:
        device.id = int(device.id)
        self._validate_id(device.id)

        if self.user_repo.get(device.responsible_user_id) is None:
            raise ValueError("Verantwortliche Person existiert nicht (User zuerst anlegen).")

        q = Query()
        existing = self.table.get(q.id == int(device.id))
        if existing is None:
            raise ValueError("Gerät existiert nicht (kann nicht aktualisiert werden).")

        old = Device.from_dict(existing)
        device.creation_date = old.creation_date
        device.last_update = now_utc()
        self.table.update(device.to_dict(), q.id == int(device.id))

    def upsert(self, device: Device) -> None:
        if self.get(int(device.id)) is None:
            self.create(device)
        else:
            self.update(device)

    def get(self, device_id: int) -> Device | None:
        self._validate_id(int(device_id))
        q = Query()
        d = self.table.get(q.id == int(device_id))
        return Device.from_dict(d) if d else None

    def list_all(self) -> list[Device]:
        # Absichtlich ohne validate_id, damit alte Daten (falls es mal größer war)
        # noch angezeigt werden können.
        return [Device.from_dict(d) for d in self.table.all()]

    def delete(self, device_id: int) -> None:
        self._validate_id(int(device_id))
        q = Query()
        self.table.remove(q.id == int(device_id))

class ReservationRepo:
    def __init__(self) -> None:
        self.table = get_db().table("reservations")

    def create(self, r: Reservation) -> None:
        r.creation_date = now_utc()
        r.last_update = now_utc()
        self.table.insert(r.to_dict())

    def delete(self, reservation_id: str) -> None:
        q = Query()
        self.table.remove(q.id == reservation_id)

    def list_for_device(self, device_id: int) -> list[Reservation]:
        q = Query()
        rows = self.table.search(q.device_id == int(device_id))
        return [Reservation.from_dict(d) for d in rows]

    def find_overlaps(self, device_id: int, start: datetime, end: datetime) -> list[Reservation]:
        # TinyDB kann nicht super SQL-mäßig interval overlap -> wir filtern in Python
        reservations = self.list_for_device(device_id)
        return [r for r in reservations if (start < r.end_date and end > r.start_date)]
