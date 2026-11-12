from data.repositories.base import SqliteRepo
from models.message import Message


class ChatRepo(SqliteRepo[Message]):
    table = "messages"
    model = Message

    def conversation(self, a: int, b: int) -> list[Message]:
        rows = self.db.query(
            "SELECT * FROM messages WHERE (sender_id = ? AND recipient_id = ?) "
            "OR (sender_id = ? AND recipient_id = ?) ORDER BY id", (a, b, b, a))
        return [self._make(r) for r in rows]

    def unread_counts(self, user_id: int) -> dict[int, int]:
        rows = self.db.query("SELECT sender_id, COUNT(*) AS c FROM messages "
                             "WHERE recipient_id = ? AND is_read = 0 GROUP BY sender_id", (user_id,))
        return {r["sender_id"]: r["c"] for r in rows}

    def mark_read(self, reader_id: int, partner_id: int) -> None:
        self.db.execute("UPDATE messages SET is_read = 1 WHERE recipient_id = ? AND sender_id = ?",
                        (reader_id, partner_id))
