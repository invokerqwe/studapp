class ThemeManager:
    """Светлая/тёмная тема с сохранением выбора в БД."""

    def __init__(self, theme_cls, db):
        self.theme_cls = theme_cls
        self.db = db

    def apply_saved(self) -> None:
        self.theme_cls.theme_style = self.db.get_setting("theme", "Light")

    def toggle(self) -> None:
        new = "Dark" if self.theme_cls.theme_style == "Light" else "Light"
        self.theme_cls.theme_style = new
        self.db.set_setting("theme", new)
