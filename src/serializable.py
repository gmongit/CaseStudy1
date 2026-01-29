# src/serializable.py
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, ClassVar, Dict, List, Optional, Type, TypeVar

from tinydb import Query
from db import DatabaseConnector  # <-- wichtig: ohne src.

T = TypeVar("T", bound="Serializable")


class Serializable(ABC):
    table_name: ClassVar[str] = ""

    def __init__(self, id: str):
        self.id = id
        self.creation_date = datetime.now()
        self.last_update = datetime.now()

    @classmethod
    def _table(cls):
        if not cls.table_name:
            raise ValueError(f"{cls.__name__}.table_name ist nicht gesetzt.")
        return DatabaseConnector().get_table(cls.table_name)

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        ...

    @classmethod
    @abstractmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        ...

    def store_data(self) -> None:
        self.last_update = datetime.now()
        table = self._table()
        q = Query()
        existing = table.search(q.id == self.id)

        payload = self.to_dict()

        if existing:
            table.update(payload, doc_ids=[existing[0].doc_id])
        else:
            table.insert(payload)

    def delete(self) -> None:
        table = self._table()
        q = Query()
        table.remove(q.id == self.id)

    @classmethod
    def find_by_attribute(cls: Type[T], attribute: str, value: Any) -> Optional[T]:
        table = cls._table()
        q = Query()
        result = table.search(getattr(q, attribute) == value)
        if not result:
            return None
        return cls.from_dict(result[0])

    @classmethod
    def find_all(cls: Type[T]) -> List[T]:
        table = cls._table()
        return [cls.from_dict(row) for row in table.all()]
