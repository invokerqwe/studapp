from data.repositories.base import SqliteRepo
from models.schedule import Lesson


class ScheduleRepo(SqliteRepo[Lesson]):
    table = "schedule"
    model = Lesson

    def by_weekday(self, weekday: int) -> list[Lesson]:
        rows = self.db.query("SELECT * FROM schedule WHERE weekday = ? ORDER BY start_time, id", (weekday,))
        return [self._make(r) for r in rows]
