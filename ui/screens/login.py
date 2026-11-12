from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField

from services.auth import AuthError


class LoginScreen(MDScreen):
    def __init__(self, **kw):
        super().__init__(**kw)
        box = MDBoxLayout(orientation="vertical", padding=dp(24), spacing=dp(16),
                          adaptive_height=True, pos_hint={"center_y": 0.5})
        box.add_widget(MDLabel(text="Вход", halign="center", font_style="H5", adaptive_height=True))
        self.login = MDTextField(hint_text="Логин", mode="rectangle")
        self.password = MDTextField(hint_text="Пароль", mode="rectangle", password=True)
        self.error = MDLabel(text="", halign="center", theme_text_color="Error", adaptive_height=True)
        box.add_widget(self.login)
        box.add_widget(self.password)
        box.add_widget(self.error)
        box.add_widget(MDRaisedButton(text="Войти", pos_hint={"center_x": 0.5}, on_release=self.submit))
        box.add_widget(MDFlatButton(text="Регистрация", pos_hint={"center_x": 0.5},
                                    on_release=lambda *_: MDApp.get_running_app().nav.go("register")))
        self.add_widget(box)

    def on_pre_enter(self, *args):
        self.password.text = ""
        self.error.text = ""

    def submit(self, *_):
        app = MDApp.get_running_app()
        try:
            app.auth.login(self.login.text, self.password.text)
        except AuthError as e:
            self.error.text = str(e)
            return
        app.on_authenticated()
