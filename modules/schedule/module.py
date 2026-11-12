from datetime import datetime

from core.errors import ValidationError
from core.registry import ModuleInfo
from data.repositories.schedule_repo import ScheduleRepo
from models.schedule import Lesson

WEEKDAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]


def _norm_time(value: str, label: str) -> str:
    try:
        return datetime.strptime(value.strip(), "%H:%M").strftime("%H:%M")
    except ValueError:
        raise ValidationError(f"{label}: формат ЧЧ:ММ")


class ScheduleService:
    """Занятия видны всем. Правит преподаватель или автор занятия (teacher_id = автор)."""

    def __init__(self, db):
        self.repo = ScheduleRepo(db)

    def day(self, weekday: int) -> list[Lesson]:
        return self.repo.by_weekday(weekday)

    @staticmethod
    def can_edit(user, lesson: Lesson) -> bool:
        return user.role == "teacher" or lesson.teacher_id == user.id

    def save(self, user, weekday: int, values: dict, lesson: Lesson = None) -> Lesson:
        subject = values["subject"].strip()
        if not subject:
            raise ValidationError("Введите предмет")
        start = _norm_time(values["start_time"], "Начало")
        end = _norm_time(values["end_time"], "Конец")
        if start >= end:
            raise ValidationError("Конец должен быть позже начала")
        room, group = values.get("room", "").strip(), values.get("group_name", "").strip()
        if lesson:
            if not self.can_edit(user, lesson):
                raise ValidationError("Нет прав на изменение")
            lesson.subject, lesson.start_time, lesson.end_time = subject, start, end
            lesson.room, lesson.group_name = room, group
            self.repo.update(lesson)
            return lesson
        return self.repo.add(Lesson(subject, weekday, start, end, room, user.id, group))

    def delete(self, user, lesson: Lesson) -> None:
        if not self.can_edit(user, lesson):
            raise ValidationError("Нет прав на удаление")
        self.repo.delete(lesson.id)


def register(registry):
    def factory():
        from kivymd.app import MDApp
        from ui.screens.schedule import ScheduleScreen
        app = MDApp.get_running_app()
        return ScheduleScreen(name="schedule", service=ScheduleService(app.db), auth=app.auth)

    registry.register(ModuleInfo("schedule", "Расписание", "calendar-clock", factory, order=10))
