from kivy.uix.scrollview import ScrollView
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFloatingActionButton
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDList
from kivymd.uix.screen import MDScreen
from kivymd.uix.toolbar import MDTopAppBar


class ModuleScreen(MDScreen):
    """Каркас экрана модуля: панель с «назад», область header, прокручиваемый список, FAB «+»."""
    screen_title = ""

    def __init__(self, with_fab=False, actions=None, **kw):
        super().__init__(**kw)
        self.root_box = MDBoxLayout(orientation="vertical")
        self.bar = MDTopAppBar(
            title=self.screen_title,
            left_action_items=[["arrow-left", lambda *_: MDApp.get_running_app().nav.back()]],
            right_action_items=actions or [],
        )
        self.header = MDBoxLayout(orientation="vertical", adaptive_height=True)
        self.list = MDList()
        self.scroll = ScrollView()
        self.scroll.add_widget(self.list)
        for w in (self.bar, self.header, self.scroll):
            self.root_box.add_widget(w)
        self.add_widget(self.root_box)
        if with_fab:
            self.add_widget(MDFloatingActionButton(icon="plus", pos_hint={"right": 0.95, "y": 0.03},
                                                   on_release=lambda *_: self.on_add()))

    def on_pre_enter(self, *args):
        self.refresh()

    def refresh(self):
        self.list.clear_widgets()
        self.load()

    def load(self):
        raise NotImplementedError

    def on_add(self):
        pass

    def empty(self, text):
        self.list.add_widget(MDLabel(text=text, halign="center", adaptive_height=True, padding=(0, 24)))
