from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.textfield import MDTextField

from core.errors import ValidationError
from ui.screens.base import ModuleScreen
from ui.widgets.cards import bubble, list_item


class ChatListScreen(ModuleScreen):
    screen_title = "Чат"

    def __init__(self, service, auth, **kw):
        super().__init__(**kw)
        self.service, self.auth = service, auth

    def load(self):
        user = self.auth.current_user
        contacts = self.service.contacts(user)
        if not contacts:
            who = "преподавателей" if user.role == "student" else "студентов"
            return self.empty(f"Пока нет зарегистрированных {who}")
        unread = self.service.unread(user)
        for c in contacts:
            n = unread.get(c.id, 0)
            self.list.add_widget(list_item(c.full_name, f"Новых сообщений: {n}" if n else "Нет новых сообщений",
                                           on_release=lambda c=c: self.open_dialog(c)))

    def open_dialog(self, partner):
        app = MDApp.get_running_app()
        if not app.sm.has_screen("chat_dialog"):
            app.nav.add(ChatDialogScreen(name="chat_dialog", service=self.service, auth=self.auth))
        app.sm.get_screen("chat_dialog").set_partner(partner)
        app.nav.go("chat_dialog")


class ChatDialogScreen(ModuleScreen):
    def __init__(self, service, auth, **kw):
        super().__init__(**kw)
        self.service, self.auth, self.partner = service, auth, None
        row = MDBoxLayout(size_hint_y=None, height=dp(72), padding=dp(8), spacing=dp(8))
        self.input = MDTextField(hint_text="Сообщение", mode="rectangle")
        row.add_widget(self.input)
        row.add_widget(MDIconButton(icon="send", pos_hint={"center_y": 0.5}, on_release=lambda *_: self.send()))
        self.root_box.add_widget(row)

    def set_partner(self, partner):
        self.partner = partner
        self.bar.title = partner.full_name

    def load(self):
        user = self.auth.current_user
        msgs = self.service.conversation(user, self.partner.id)
        if not msgs:
            self.empty("Сообщений пока нет")
        for m in msgs:
            self.list.add_widget(bubble(m.text, m.sent_at[:16], m.sender_id == user.id))
        Clock.schedule_once(lambda dt: setattr(self.scroll, "scroll_y", 0), 0.1)

    def send(self):
        try:
            self.service.send(self.auth.current_user, self.partner.id, self.input.text)
        except ValidationError as e:
            return toast(str(e))
        self.input.text = ""
        self.refresh()
