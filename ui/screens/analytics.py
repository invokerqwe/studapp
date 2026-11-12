from kivymd.uix.list import OneLineListItem

from core.config import MAX_GRADE
from ui.screens.base import ModuleScreen
from ui.widgets.cards import list_item
from ui.widgets.charts import BarChart, LineChart, fmt


class AnalyticsScreen(ModuleScreen):
    screen_title = "Аналитика и отчёты"

    def __init__(self, service, auth, **kw):
        super().__init__(**kw)
        self.service, self.auth = service, auth

    def _title(self, text):
        self.list.add_widget(OneLineListItem(text=text, disabled=True))

    def _summary(self, rep, extra=""):
        avg = fmt(rep["average"]) if rep["average"] is not None else "—"
        self.list.add_widget(list_item(f"Средний балл: {avg}", f"Всего оценок: {rep['count']}{extra}"))

    def load(self):
        user = self.auth.current_user
        if user.role == "student":
            r = self.service.student_report(user.id)
            self._summary(r, f" · дедлайнов: {r['deadlines_total']}")
            self._title("Средний балл по предметам")
            self.list.add_widget(BarChart(data=r["by_subject"], max_value=MAX_GRADE))
            self._title("Динамика оценок (последние 20)")
            self.list.add_widget(LineChart(data=r["trend"], max_value=MAX_GRADE))
            self._title("Дедлайны")
            self.list.add_widget(BarChart(data=r["deadlines"]))
        else:
            r = self.service.teacher_report()
            self._summary(r)
            self._title("Средний балл по предметам")
            self.list.add_widget(BarChart(data=r["by_subject"], max_value=MAX_GRADE))
            self._title("Рейтинг студентов (первые 10)")
            self.list.add_widget(BarChart(data=r["by_student"], max_value=MAX_GRADE))
            self._title("Нагрузка по дням (занятий)")
            self.list.add_widget(BarChart(data=r["workload"]))
