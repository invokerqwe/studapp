from datetime import datetime

from core.config import DT_FORMAT
from core.registry import ModuleInfo

WEEKDAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]


class AnalyticsService:
    def __init__(self, db):
        self.db = db

    def student_report(self, user_id: int) -> dict:
        rows = self.db.query("SELECT subject, value FROM grades WHERE student_id = ? ORDER BY date, id", (user_id,))
        by = self.db.query("SELECT subject, AVG(value) AS a FROM grades WHERE student_id = ? "
                           "GROUP BY subject ORDER BY subject", (user_id,))
        values = [r["value"] for r in rows]
        dls = self.db.query("SELECT due_at, done FROM deadlines WHERE user_id = ?", (user_id,))
        now = datetime.now().strftime(DT_FORMAT)
        done = sum(1 for d in dls if d["done"])
        overdue = sum(1 for d in dls if not d["done"] and d["due_at"] < now)
        return {
            "count": len(values),
            "average": sum(values) / len(values) if values else None,
            "by_subject": [(r["subject"], r["a"]) for r in by],
            "trend": values[-20:],
            "deadlines": [("Выполнено", done), ("Активные", len(dls) - done - overdue), ("Просрочено", overdue)],
            "deadlines_total": len(dls),
        }

    def teacher_report(self) -> dict:
        total = self.db.query_one("SELECT COUNT(*) AS c, AVG(value) AS a FROM grades")
        by_subject = self.db.query("SELECT subject, AVG(value) AS a FROM grades GROUP BY subject ORDER BY subject")
        by_student = self.db.query(
            "SELECT u.full_name AS n, AVG(g.value) AS a FROM grades g JOIN users u ON u.id = g.student_id "
            "GROUP BY g.student_id ORDER BY a DESC")
        load = {r["weekday"]: r["c"] for r in
                self.db.query("SELECT weekday, COUNT(*) AS c FROM schedule GROUP BY weekday")}
        return {
            "count": total["c"], "average": total["a"],
            "by_subject": [(r["subject"], r["a"]) for r in by_subject],
            "by_student": [(r["n"].split()[0], r["a"]) for r in by_student],
            "workload": [(d, load.get(i, 0)) for i, d in enumerate(WEEKDAYS)],
        }


def register(registry):
    def factory():
        from kivymd.app import MDApp
        from ui.screens.analytics import AnalyticsScreen
        app = MDApp.get_running_app()
        return AnalyticsScreen(name="analytics", service=AnalyticsService(app.db), auth=app.auth)

    registry.register(ModuleInfo("analytics", "Аналитика и отчёты", "chart-bar", factory, order=50))
