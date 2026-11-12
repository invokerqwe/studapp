"""Интерфейс репозитория. SQLite-реализация ниже; позже можно подставить серверную (API)."""
from abc import ABC, abstractmethod
from dataclasses import asdict, fields
from typing import Generic, Optional, TypeVar

T = TypeVar("T")


class BaseRepo(ABC, Generic[T]):
    @abstractmethod
    def add(self, obj: T) -> T: ...
    @abstractmethod
    def get(self, id: int) -> Optional[T]: ...
    @abstractmethod
    def list(self, **filters) -> list[T]: ...
    @abstractmethod
    def update(self, obj: T) -> None: ...
    @abstractmethod
    def delete(self, id: int) -> None: ...


class SqliteRepo(BaseRepo[T]):
    """Универсальный CRUD поверх dataclass-модели. Наследники добавляют специальные запросы."""
    table: str
    model: type

    def __init__(self, db):
        self.db = db
        self._cols = [f.name for f in fields(self.model) if f.name != "id"]

    def _make(self, row) -> T:
        return self.model(**dict(row))

    def add(self, obj: T) -> T:
        data = asdict(obj)
        vals = [data[c] for c in self._cols]
        cur = self.db.execute(
            f"INSERT INTO {self.table} ({','.join(self._cols)}) "
            f"VALUES ({','.join('?' * len(self._cols))})", vals)
        obj.id = cur.lastrowid
        return obj

    def get(self, id: int) -> Optional[T]:
        row = self.db.query_one(f"SELECT * FROM {self.table} WHERE id = ?", (id,))
        return self._make(row) if row else None

    def list(self, **filters) -> list[T]:
        bad = set(filters) - set(self._cols)
        if bad:
            raise ValueError(f"Unknown filter fields: {bad}")
        where = " AND ".join(f"{k} = ?" for k in filters)
        sql = f"SELECT * FROM {self.table}" + (f" WHERE {where}" if where else "")
        return [self._make(r) for r in self.db.query(sql, list(filters.values()))]

    def update(self, obj: T) -> None:
        data = asdict(obj)
        sets = ",".join(f"{c} = ?" for c in self._cols)
        self.db.execute(f"UPDATE {self.table} SET {sets} WHERE id = ?",
                        [data[c] for c in self._cols] + [obj.id])

    def delete(self, id: int) -> None:
        self.db.execute(f"DELETE FROM {self.table} WHERE id = ?", (id,))
