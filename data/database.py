import sqlite3
from typing import Any, Iterable, Optional

# Миграции: индекс + 1 = версия схемы (PRAGMA user_version). Новые — только в конец.
MIGRATIONS: list[str] = [
    """
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        login TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        role TEXT NOT NULL CHECK (role IN ('student','teacher'))
    );
    CREATE TABLE schedule (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject TEXT NOT NULL,
        weekday INTEGER NOT NULL,          -- 0=пн .. 6=вс
        start_time TEXT NOT NULL,          -- HH:MM
        end_time TEXT NOT NULL,
        room TEXT DEFAULT '',
        teacher_id INTEGER REFERENCES users(id),
        group_name TEXT DEFAULT ''
    );
    CREATE TABLE grades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL REFERENCES users(id),
        subject TEXT NOT NULL,
        value REAL NOT NULL,
        date TEXT NOT NULL,                -- YYYY-MM-DD
        comment TEXT DEFAULT ''
    );
    CREATE TABLE deadlines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL REFERENCES users(id),
        title TEXT NOT NULL,
        subject TEXT DEFAULT '',
        due_at TEXT NOT NULL,              -- YYYY-MM-DD HH:MM
        done INTEGER NOT NULL DEFAULT 0
    );
    CREATE TABLE messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL REFERENCES users(id),
        recipient_id INTEGER NOT NULL REFERENCES users(id),
        text TEXT NOT NULL,
        sent_at TEXT NOT NULL,
        is_read INTEGER NOT NULL DEFAULT 0
    );
    CREATE TABLE settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    );
    """,
]


class Database:
    def __init__(self, path: str):
        self.path = path
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")

    def migrate(self) -> None:
        current = self.conn.execute("PRAGMA user_version").fetchone()[0]
        for version in range(current, len(MIGRATIONS)):
            self.conn.executescript(MIGRATIONS[version])
            self.conn.execute(f"PRAGMA user_version = {version + 1}")
        self.conn.commit()

    def execute(self, sql: str, params: Iterable[Any] = ()) -> sqlite3.Cursor:
        cur = self.conn.execute(sql, tuple(params))
        self.conn.commit()
        return cur

    def query(self, sql: str, params: Iterable[Any] = ()) -> list[sqlite3.Row]:
        return self.conn.execute(sql, tuple(params)).fetchall()

    def query_one(self, sql: str, params: Iterable[Any] = ()) -> Optional[sqlite3.Row]:
        return self.conn.execute(sql, tuple(params)).fetchone()

    def get_setting(self, key: str, default: str = "") -> str:
        row = self.query_one("SELECT value FROM settings WHERE key = ?", (key,))
        return row["value"] if row else default

    def set_setting(self, key: str, value: str) -> None:
        self.execute(
            "INSERT INTO settings(key, value) VALUES(?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )

    def close(self) -> None:
        self.conn.close()
