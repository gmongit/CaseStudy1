from __future__ import annotations
from datetime import datetime, timezone
from repositories import UserRepo, DeviceRepo, ReservationRepo
from reservations import Reservation


class ReservationError(Exception):
    pass

class ReservationService:
    def __init__(self) -> None:
        self.user_repo = UserRepo()
        self.device_repo = DeviceRepo()
        self.res_repo = ReservationRepo()

    @staticmethod
    def _overlaps(
        a_start: datetime,
        a_end: datetime,
        b_start: datetime,
        b_end: datetime,
    ) -> bool:
        # Overlap, wenn sich die Intervalle schneiden
        return a_start < b_end and a_end > b_start

    def create(
        self,
        user_id: str,
        device_id: int,
        start: datetime,
        end: datetime,
    ) -> Reservation:

        if start >= end:
            raise ReservationError("Start muss vor Ende liegen.")

        user = self.user_repo.get(user_id)
        if user is None:
            raise ReservationError("User existiert nicht.")

        device = self.device_repo.get(int(device_id))
        if device is None:
            raise ReservationError("Gerät existiert nicht.")
        if not device.is_active:
            raise ReservationError("Gerät ist nicht aktiv.")
        if (
            device.end_of_life is not None
            and device.end_of_life < datetime.now(timezone.utc)
        ):
            raise ReservationError("Gerät ist End-of-Life und nicht mehr reservierbar.")

        overlaps = self.res_repo.find_overlaps(int(device_id), start, end)
        if overlaps:
            r = overlaps[0]
            raise ReservationError(
                f"Überschneidung mit Reservierung {r.id}: {r.start_date} – {r.end_date}"
            )

        res = Reservation(
            user_id=user_id,
            device_id=int(device_id),
            start_date=start,
            end_date=end,
        )
        self.res_repo.create(res)
        return res

    def cancel(self, reservation_id: str) -> None:
        self.res_repo.delete(reservation_id)