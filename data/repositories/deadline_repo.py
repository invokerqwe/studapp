from data.repositories.base import SqliteRepo
from models.deadline import Deadline


class DeadlineRepo(SqliteRepo[Deadline]):
    table = "deadlines"
    model = Deadline

    def for_user(self, user_id: int) -> list[Deadline]:
        rows = self.db.query("SELECT * FROM deadlines WHERE user_id = ? ORDER BY done, due_at, id", (user_id,))
        return [self._make(r) for r in rows]
