from typing import Optional

from data.repositories.base import SqliteRepo
from models.grade import Grade


class GradesRepo(SqliteRepo[Grade]):
    table = "grades"
    model = Grade

    def entries(self, student_id: Optional[int] = None) -> list[tuple[Grade, str, str]]:
        """[(оценка, ФИО студента, логин студента)] — новые сверху."""
        sql = ("SELECT g.*, u.full_name AS student_name, u.login AS student_login "
               "FROM grades g JOIN users u ON u.id = g.student_id")
        params: tuple = ()
        if student_id is not None:
            sql += " WHERE g.student_id = ?"
            params = (student_id,)
        sql += " ORDER BY g.date DESC, g.id DESC"
        keys = ["id"] + self._cols
        return [(Grade(**{k: r[k] for k in keys}), r["student_name"], r["student_login"])
                for r in self.db.query(sql, params)]
