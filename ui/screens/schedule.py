from datetime import datetime

from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView
from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton

from modules.schedule.module import WEEKDAYS
from ui.screens.base import ModuleScreen
from ui.widgets.cards import list_item
from ui.widgets.dialogs import FormDialog


class ScheduleScreen(ModuleScreen):
    screen_title = "Расписание"

    def __init__(self, service, auth, **kw):
        super().__init__(with_fab=True, **kw)
        self.service, self.auth = service, auth
        self.day = datetime.now().weekday()
        tabs = ScrollView(do_scroll_y=False, size_hint_y=None, height=dp(48), bar_width=0)
        row = MDBoxLayout(adaptive_width=True, spacing=dp(4), padding=dp(4))
        self.tab_buttons = []
        for i, name in enumerate(WEEKDAYS):
            b = MDFlatButton(text=name, on_release=lambda _, d=i: self.select_day(d))
            self.tab_buttons.append(b)
            row.add_widget(b)
        tabs.add_widget(row)
        self.header.add_widget(tabs)

    def select_day(self, day):
        self.day = day
        self.refresh()

    def load(self):
        t = MDApp.get_running_app().theme_cls
        for i, b in enumerate(self.tab_buttons):
            b.text_color = t.primary_color if i == self.day else t.disabled_hint_text_color
        lessons = self.service.day(self.day)
        if not lessons:
            return self.empty("На этот день занятий нет")
        for l in lessons:
            details = " · ".join(x for x in (f"ауд. {l.room}" if l.room else "", l.group_name) if x)
            self.list.add_widget(list_item(f"{l.start_time}–{l.end_time}   {l.subject}", details,
                                           on_release=lambda l=l: self.open_form(l)))

    def on_add(self):
        self.open_form(None)

    def open_form(self, lesson):
        user = self.auth.current_user
        if lesson and not self.service.can_edit(user, lesson):
            return toast("Это занятие может менять только преподаватель или автор")
        g = lambda a, d="": getattr(lesson, a) if lesson else d
        fields = [("subject", "Предмет", g("subject")), ("start_time", "Начало (ЧЧ:ММ)", g("start_time", "09:00")),
                  ("end_time", "Конец (ЧЧ:ММ)", g("end_time", "10:30")), ("room", "Аудитория", g("room")),
                  ("group_name", "Группа", g("group_name"))]

        def save(values):
            self.service.save(user, self.day, values, lesson)
            self.refresh()

        def delete():
            self.service.delete(user, lesson)
            self.refresh()

        FormDialog(f"{'Изменить' if lesson else 'Новое'} занятие ({WEEKDAYS[self.day]})", fields, save,
                   delete if lesson else None)
