from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField

from services.auth import AuthError


class RegisterScreen(MDScreen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.role = "student"
        box = MDBoxLayout(orientation="vertical", padding=dp(24), spacing=dp(16), adaptive_height=True)
        box.add_widget(MDLabel(text="Регистрация", halign="center", font_style="H5", adaptive_height=True))
        self.full_name = MDTextField(hint_text="Имя и фамилия", mode="rectangle")
        self.login = MDTextField(hint_text="Логин", mode="rectangle")
        self.password = MDTextField(hint_text="Пароль", mode="rectangle", password=True)
        self.confirm = MDTextField(hint_text="Повторите пароль", mode="rectangle", password=True)
        for w in (self.full_name, self.login, self.password, self.confirm):
            box.add_widget(w)

        roles = MDBoxLayout(spacing=dp(12), adaptive_height=True)
        self.btn_student = MDRaisedButton(text="Студент", on_release=lambda *_: self.set_role("student"))
        self.btn_teacher = MDRaisedButton(text="Преподаватель", on_release=lambda *_: self.set_role("teacher"))
        roles.add_widget(self.btn_student)
        roles.add_widget(self.btn_teacher)
        box.add_widget(roles)

        self.error = MDLabel(text="", halign="center", theme_text_color="Error", adaptive_height=True)
        box.add_widget(self.error)
        box.add_widget(MDRaisedButton(text="Создать аккаунт", pos_hint={"center_x": 0.5}, on_release=self.submit))
        box.add_widget(MDFlatButton(text="Уже есть аккаунт", pos_hint={"center_x": 0.5},
                                    on_release=lambda *_: MDApp.get_running_app().nav.back()))
        scroll = ScrollView()
        scroll.add_widget(box)
        self.add_widget(scroll)
        self.set_role("student")

    def set_role(self, role: str):
        self.role = role
        app = MDApp.get_running_app()
        active = app.theme_cls.primary_color if app else (0.2, 0.3, 0.8, 1)
        for btn, r in ((self.btn_student, "student"), (self.btn_teacher, "teacher")):
            btn.md_bg_color = active if r == role else (0.5, 0.5, 0.5, 1)

    def on_pre_enter(self, *args):
        self.error.text = ""
        self.set_role(self.role)

    def submit(self, *_):
        if self.password.text != self.confirm.text:
            self.error.text = "Пароли не совпадают"
            return
        app = MDApp.get_running_app()
        try:
            app.auth.register(self.login.text, self.password.text, self.full_name.text, self.role)
        except AuthError as e:
            self.error.text = str(e)
            return
        app.on_authenticated()
