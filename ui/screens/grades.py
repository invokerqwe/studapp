from datetime import datetime

from kivy.metrics import dp
from kivymd.uix.label import MDLabel

from core.config import DATE_FORMAT
from ui.screens.base import ModuleScreen
from ui.widgets.cards import list_item
from ui.widgets.dialogs import FormDialog


def fmt(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


class GradesScreen(ModuleScreen):
    screen_title = "Успеваемость"

    def __init__(self, service, auth, **kw):
        super().__init__(with_fab=auth.current_user.role == "teacher", **kw)
        self.service, self.auth = service, auth
        self.is_teacher = auth.current_user.role == "teacher"
        self.summary = MDLabel(text="", adaptive_height=True, padding=(dp(16), dp(8)))
        self.header.add_widget(self.summary)

    def load(self):
        entries = self.service.entries(self.auth.current_user)
        st = self.service.stats([e[0] for e in entries])
        if not st["count"]:
            self.summary.text = ""
            return self.empty("Оценок пока нет")
        lines = [f"Средний балл: {fmt(st['average'])} · оценок: {st['count']}"]
        lines += [" · ".join(f"{s} {fmt(a)}" for s, a in st["by_subject"].items())]
        self.summary.text = "\n".join(lines)
        for g, name, login in entries:
            title = f"{g.subject}: {fmt(g.value)}" + (f"  —  {name}" if self.is_teacher else "")
            self.list.add_widget(list_item(title, f"{g.date}" + (f" · {g.comment}" if g.comment else ""),
                                           on_release=lambda g=g, login=login: self.open_form(g, login)))

    def on_add(self):
        self.open_form(None, "")

    def open_form(self, grade, login):
        if not self.is_teacher:
            return
        user = self.auth.current_user
        fields = [("student_login", "Логин студента", login), ("subject", "Предмет", grade.subject if grade else ""),
                  ("value", "Оценка", grade.value if grade else ""),
                  ("date", "Дата (ГГГГ-ММ-ДД)", grade.date if grade else datetime.now().strftime(DATE_FORMAT)),
                  ("comment", "Комментарий", grade.comment if grade else "")]

        def save(values):
            self.service.save(user, values, grade)
            self.refresh()

        def delete():
            self.service.delete(user, grade)
            self.refresh()

        FormDialog("Изменить оценку" if grade else "Новая оценка", fields, save, delete if grade else None)
