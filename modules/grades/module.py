from datetime import datetime

from core.config import DATE_FORMAT, MAX_GRADE
from core.errors import ValidationError
from core.registry import ModuleInfo
from data.repositories.grades_repo import GradesRepo
from data.repositories.user_repo import UserRepo
from models.grade import Grade


class GradesService:
    """Студент видит свои оценки, преподаватель — все и может выставлять/менять."""

    def __init__(self, db):
        self.repo = GradesRepo(db)
        self.users = UserRepo(db)

    def entries(self, user):
        return self.repo.entries(user.id if user.role == "student" else None)

    @staticmethod
    def stats(grades: list[Grade]) -> dict:
        by: dict[str, list[float]] = {}
        for g in grades:
            by.setdefault(g.subject, []).append(g.value)
        count = len(grades)
        return {
            "count": count,
            "average": sum(g.value for g in grades) / count if count else None,
            "by_subject": {s: sum(v) / len(v) for s, v in sorted(by.items())},
        }

    def save(self, user, values: dict, grade: Grade = None) -> Grade:
        if user.role != "teacher":
            raise ValidationError("Оценки выставляет преподаватель")
        student = self.users.get_by_login(values["student_login"].strip().lower())
        if not student or student.role != "student":
            raise ValidationError("Студент с таким логином не найден")
        subject = values["subject"].strip()
        if not subject:
            raise ValidationError("Введите предмет")
        try:
            value = float(values["value"].replace(",", "."))
        except ValueError:
            raise ValidationError("Оценка должна быть числом")
        if not 0 <= value <= MAX_GRADE:
            raise ValidationError(f"Оценка: от 0 до {MAX_GRADE}")
        date = values.get("date", "").strip() or datetime.now().strftime(DATE_FORMAT)
        try:
            datetime.strptime(date, DATE_FORMAT)
        except ValueError:
            raise ValidationError("Дата: формат ГГГГ-ММ-ДД")
        comment = values.get("comment", "").strip()
        if grade:
            grade.student_id, grade.subject, grade.value = student.id, subject, value
            grade.date, grade.comment = date, comment
            self.repo.update(grade)
            return grade
        return self.repo.add(Grade(student.id, subject, value, date, comment))

    def delete(self, user, grade: Grade) -> None:
        if user.role != "teacher":
            raise ValidationError("Нет прав на удаление")
        self.repo.delete(grade.id)


def register(registry):
    def factory():
        from kivymd.app import MDApp
        from ui.screens.grades import GradesScreen
        app = MDApp.get_running_app()
        return GradesScreen(name="grades", service=GradesService(app.db), auth=app.auth)

    registry.register(ModuleInfo("grades", "Успеваемость", "school", factory, order=20))
