from datetime import datetime, timedelta

from core.config import DT_FORMAT
from ui.screens.base import ModuleScreen
from ui.widgets.cards import list_item
from ui.widgets.dialogs import FormDialog, choice_dialog


class DeadlinesScreen(ModuleScreen):
    screen_title = "Дедлайны"

    def __init__(self, service, auth, **kw):
        super().__init__(with_fab=True, **kw)
        self.service, self.auth = service, auth

    def load(self):
        items = self.service.items(self.auth.current_user)
        if not items:
            return self.empty("Дедлайнов нет. Нажмите «+», чтобы добавить")
        for d in items:
            mark = "✓ " if d.done else ""
            sec = f"{d.subject} · до {d.due_at}" if d.subject else f"до {d.due_at}"
            self.list.add_widget(list_item(mark + d.title, sec, self.service.status(d),
                                           on_release=lambda d=d: self.actions(d)))

    def actions(self, d):
        choice_dialog(d.title, [
            ("Вернуть в работу" if d.done else "Отметить выполненным", lambda: self._toggle(d)),
            ("Изменить", lambda: self.open_form(d)),
            ("Удалить", lambda: self._delete(d)),
        ])

    def _toggle(self, d):
        self.service.toggle(d)
        self.refresh()

    def _delete(self, d):
        self.service.delete(d)
        self.refresh()

    def on_add(self):
        self.open_form(None)

    def open_form(self, d):
        user = self.auth.current_user
        default = (datetime.now() + timedelta(days=1)).replace(hour=23, minute=59).strftime(DT_FORMAT)
        fields = [("title", "Название", d.title if d else ""), ("subject", "Предмет", d.subject if d else ""),
                  ("due_at", "Срок (ГГГГ-ММ-ДД ЧЧ:ММ)", d.due_at if d else default)]

        def save(values):
            self.service.save(user, values, d)
            self.refresh()

        FormDialog("Изменить дедлайн" if d else "Новый дедлайн", fields, save)
