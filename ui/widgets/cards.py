from kivy.metrics import dp
from kivy.uix.widget import Widget
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.list import OneLineListItem, ThreeLineListItem, TwoLineListItem


def list_item(text, secondary="", tertiary="", on_release=None):
    cls = ThreeLineListItem if tertiary else (TwoLineListItem if secondary else OneLineListItem)
    kw = {"text": text}
    if secondary:
        kw["secondary_text"] = secondary
    if tertiary:
        kw["tertiary_text"] = tertiary
    item = cls(**kw)
    if on_release:
        item.bind(on_release=lambda *_: on_release())
    return item


def bubble(text, time_text, mine):
    """Пузырь сообщения чата: свои — справа, чужие — слева."""
    t = MDApp.get_running_app().theme_cls
    row = MDBoxLayout(adaptive_height=True, padding=(dp(8), dp(4)))
    card = MDBoxLayout(orientation="vertical", adaptive_height=True, size_hint_x=0.8,
                       padding=dp(10), radius=[dp(12)],
                       md_bg_color=t.primary_color if mine else t.bg_dark)
    kw = {"theme_text_color": "Custom", "text_color": (1, 1, 1, 1)} if mine else {}
    card.add_widget(MDLabel(text=text, adaptive_height=True, **kw))
    card.add_widget(MDLabel(text=time_text, font_style="Caption", adaptive_height=True, **kw))
    spacer = Widget(size_hint_x=0.2)
    for w in ((spacer, card) if mine else (card, spacer)):
        row.add_widget(w)
    return row
