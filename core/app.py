import os

from kivy.clock import Clock
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager

from core.navigation import Navigation
from core.registry import ModuleRegistry
from core.theme import ThemeManager
from data.database import Database
from data.repositories.user_repo import UserRepo
from services.auth import AuthService
from services.notifications import NotificationService
from ui.screens.login import LoginScreen
from ui.screens.main_menu import MainMenuScreen
from ui.screens.register import RegisterScreen

CORE_SCREENS = {"login", "register", "main_menu"}


class StudentApp(MDApp):
    def build(self):
        self.title = "Учебный процесс"
        self.theme_cls.primary_palette = "Indigo"

        self.db = Database(os.path.join(self.user_data_dir, "student_app.db"))
        self.db.migrate()

        self.theme_mgr = ThemeManager(self.theme_cls, self.db)
        self.theme_mgr.apply_saved()

        self.auth = AuthService(UserRepo(self.db), self.db)
        self.notifier = NotificationService()
        Window.softinput_mode = "below_target"
        Window.bind(on_keyboard=self._on_keyboard)

        self.registry = ModuleRegistry()
        self.registry.discover()

        self.sm = MDScreenManager()
        self.nav = Navigation(self.sm)
        for cls, name in ((LoginScreen, "login"), (RegisterScreen, "register"),
                          (MainMenuScreen, "main_menu")):
            self.nav.add(cls(name=name))
        # автовход, если сессия сохранена
        self.sm.current = "main_menu" if self.auth.restore_session() else "login"
        return self.sm

    def on_start(self):
        self.notifier.request_permission()
        for fn, interval in self.registry.periodic:
            Clock.schedule_once(lambda dt, f=fn: self._safe(f), 3)
            Clock.schedule_interval(lambda dt, f=fn: self._safe(f), interval)

    def _safe(self, fn):
        try:
            fn(self)
        except Exception as e:      # фоновая задача не должна ронять приложение
            print(f"[periodic] {fn.__name__}: {e}")

    def _on_keyboard(self, window, key, *args):
        return key == 27 and self.nav.back()    # Android «назад» / Esc

    @property
    def current_role(self):
        return self.auth.role

    def on_authenticated(self):
        self.nav.drop_except(CORE_SCREENS)   # модули пересоздадутся под нового пользователя
        self.nav.reset("main_menu")

    def logout(self):
        self.auth.logout()
        self.nav.drop_except(CORE_SCREENS)
        self.nav.reset("login")

    def toggle_theme(self):
        self.theme_mgr.toggle()

    def on_stop(self):
        self.db.close()
