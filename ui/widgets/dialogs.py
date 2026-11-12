from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.list import OneLineListItem
from kivymd.uix.textfield import MDTextField

from core.errors import ValidationError


class FormDialog:
    """Универсальная форма. fields: [(key, подсказка, начальное значение)].
    on_save(values) бросает ValidationError при ошибке; on_delete() — по желанию."""

    def __init__(self, title, fields, on_save, on_delete=None):
        self.on_save, self.on_delete = on_save, on_delete
        self.inputs = {}
        content = MDBoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None,
                              height=dp(64) * len(fields) + dp(28))
        for key, hint, init in fields:
            tf = MDTextField(hint_text=hint, text="" if init is None else str(init))
            self.inputs[key] = tf
            content.add_widget(tf)
        self.error = MDLabel(text="", theme_text_color="Error", size_hint_y=None, height=dp(24))
        content.add_widget(self.error)
        buttons = [MDFlatButton(text="Отмена", on_release=lambda *_: self.dialog.dismiss())]
        if on_delete:
            buttons.append(MDFlatButton(text="Удалить", on_release=self._delete))
        buttons.append(MDFlatButton(text="Сохранить", on_release=self._save))
        self.dialog = MDDialog(title=title, type="custom", content_cls=content, buttons=buttons)
        self.dialog.open()

    def _run(self, fn, *args):
        try:
            fn(*args)
        except ValidationError as e:
            self.error.text = str(e)
            return
        self.dialog.dismiss()

    def _save(self, *_):
        self._run(self.on_save, {k: tf.text.strip() for k, tf in self.inputs.items()})

    def _delete(self, *_):
        self._run(self.on_delete)


def choice_dialog(title, actions):
    """Диалог-меню. actions: [(подпись, функция)]."""
    def wrap(fn):
        def handler(*_):
            dlg.dismiss()
            fn()
        return handler
    dlg = MDDialog(title=title, type="simple",
                   items=[OneLineListItem(text=label, on_release=wrap(fn)) for label, fn in actions])
    dlg.open()
    return dlg
