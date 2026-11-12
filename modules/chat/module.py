from datetime import datetime

from core.errors import ValidationError
from core.registry import ModuleInfo
from data.repositories.chat_repo import ChatRepo
from data.repositories.user_repo import UserRepo
from models.message import Message


class ChatService:
    """Чат только студент ↔ преподаватель."""

    def __init__(self, db):
        self.repo = ChatRepo(db)
        self.users = UserRepo(db)

    def contacts(self, user):
        return self.users.list_by_role("teacher" if user.role == "student" else "student")

    def unread(self, user) -> dict:
        return self.repo.unread_counts(user.id)

    def conversation(self, user, partner_id: int) -> list[Message]:
        msgs = self.repo.conversation(user.id, partner_id)
        self.repo.mark_read(user.id, partner_id)
        return msgs

    def send(self, user, partner_id: int, text: str) -> Message:
        text = text.strip()
        if not text:
            raise ValidationError("Пустое сообщение")
        partner = self.users.get(partner_id)
        if not partner or partner.role == user.role:
            raise ValidationError("Писать можно только студенту ↔ преподавателю")
        return self.repo.add(Message(user.id, partner_id, text, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))


def register(registry):
    def factory():
        from kivymd.app import MDApp
        from ui.screens.chat import ChatListScreen
        app = MDApp.get_running_app()
        return ChatListScreen(name="chat", service=ChatService(app.db), auth=app.auth)

    registry.register(ModuleInfo("chat", "Чат", "message-text", factory, order=40))
