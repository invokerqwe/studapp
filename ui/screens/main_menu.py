from kivy.uix.scrollview import ScrollView
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import IconLeftWidget, MDList, OneLineIconListItem
from kivymd.uix.screen import MDScreen
from kivymd.uix.toolbar import MDTopAppBar


class MainMenuScreen(MDScreen):
    """Главное меню строится из реестра модулей с учётом роли пользователя."""

    def __init__(self, **kw):
        super().__init__(**kw)
        root = MDBoxLayout(orientation="vertical")
        self.bar = MDTopAppBar(
            title="Главное меню",
            left_action_items=[["logout", lambda *_: MDApp.get_running_app().logout()]],
            right_action_items=[["theme-light-dark", lambda *_: MDApp.get_running_app().toggle_theme()]],
        )
        root.add_widget(self.bar)
        self.list = MDList()
        scroll = ScrollView()
        scroll.add_widget(self.list)
        root.add_widget(scroll)
        self.add_widget(root)

    def on_pre_enter(self, *args):
        self.refresh()

    def refresh(self):
        app = MDApp.get_running_app()
        user = app.auth.current_user
        if user:
            kind = "преподаватель" if user.role == "teacher" else "студент"
            self.bar.title = f"{user.full_name} ({kind})"
        self.list.clear_widgets()
        mods = app.registry.for_role(app.auth.role)
        if not mods:
            self.list.add_widget(OneLineIconListItem(text="Модули пока не подключены"))
            return
        for info in mods:
            item = OneLineIconListItem(text=info.title,
                                       on_release=lambda _, i=info: app.nav.open_module(i))
            item.add_widget(IconLeftWidget(icon=info.icon))
            self.list.add_widget(item)
