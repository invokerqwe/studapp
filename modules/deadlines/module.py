from datetime import datetime, timedelta

from core.config import DT_FORMAT
from core.errors import ValidationError
from core.registry import ModuleInfo
from data.repositories.deadline_repo import DeadlineRepo
from models.deadline import Deadline

NOTIFIED_KEY = "notified_deadlines"


class DeadlineService:
    def __init__(self, db):
        self.db = db
        self.repo = DeadlineRepo(db)

    def items(self, user) -> list[Deadline]:
        return self.repo.for_user(user.id)

    def save(self, user, values: dict, deadline: Deadline = None) -> Deadline:
        title = values["title"].strip()
        if not title:
            raise ValidationError("Введите название")
        try:
            due = datetime.strptime(values["due_at"].strip(), DT_FORMAT).strftime(DT_FORMAT)
        except ValueError:
            raise ValidationError("Срок: формат ГГГГ-ММ-ДД ЧЧ:ММ")
        subject = values.get("subject", "").strip()
        if deadline:
            deadline.title, deadline.due_at, deadline.subject = title, due, subject
            self.repo.update(deadline)
            return deadline
        return self.repo.add(Deadline(user.id, title, due, subject))

    def toggle(self, deadline: Deadline) -> None:
        deadline.done = 0 if deadline.done else 1
        self.repo.update(deadline)

    def delete(self, deadline: Deadline) -> None:
        self.repo.delete(deadline.id)

    @staticmethod
    def status(d: Deadline, now: datetime = None) -> str:
        if d.done:
            return "Выполнено"
        left = datetime.strptime(d.due_at, DT_FORMAT) - (now or datetime.now())
        if left.total_seconds() < 0:
            return "Просрочено"
        days, hours = left.days, left.seconds // 3600
        if days:
            return f"Осталось {days} дн. {hours} ч"
        return f"Осталось {hours} ч {left.seconds % 3600 // 60} мин"

    def due_reminders(self, user_id: int, now: datetime = None) -> list[tuple[Deadline, str]]:
        """Дедлайны, о которых пора напомнить (за 24 ч и за 1 ч). Каждое напоминание — один раз."""
        now = now or datetime.now()
        raw = self.db.get_setting(NOTIFIED_KEY, "")
        notified = {k for k in raw.split(",") if k}
        out = []
        for d in self.repo.for_user(user_id):
            if d.done:
                continue
            left = datetime.strptime(d.due_at, DT_FORMAT) - now
            if left <= timedelta(0) or left > timedelta(hours=24):
                continue
            stage = "1h" if left <= timedelta(hours=1) else "24h"
            key = f"{d.id}|{d.due_at}|{stage}"
            if key not in notified:
                notified.add(key)
                out.append((d, stage))
        ids = {str(d.id) for d in self.repo.list()}
        notified = {k for k in notified if k.split("|")[0] in ids}   # чистим удалённые
        new_raw = ",".join(sorted(notified))
        if new_raw != raw:
            self.db.set_setting(NOTIFIED_KEY, new_raw)
        return out


def check_reminders(app) -> None:
    user = app.auth.current_user
    if not user:
        return
    for d, stage in DeadlineService(app.db).due_reminders(user.id):
        msg = "Менее часа до срока!" if stage == "1h" else f"Срок: {d.due_at}"
        app.notifier.notify(f"Дедлайн: {d.title}", msg)


def register(registry):
    def factory():
        from kivymd.app import MDApp
        from ui.screens.deadlines import DeadlinesScreen
        app = MDApp.get_running_app()
        return DeadlinesScreen(name="deadlines", service=DeadlineService(app.db), auth=app.auth)

    registry.register(ModuleInfo("deadlines", "Дедлайны", "alarm", factory, order=30))
    registry.register_periodic(check_reminders, 60)
