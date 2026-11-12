class Navigation:
    """Обёртка над ScreenManager: переходы, история, ленивое создание экранов модулей."""

    def __init__(self, manager):
        self.sm = manager
        self._history: list[str] = []

    def add(self, screen) -> None:
        if not self.sm.has_screen(screen.name):
            self.sm.add_widget(screen)

    def go(self, name: str, direction: str = "left") -> None:
        if name == self.sm.current:
            return
        self._history.append(self.sm.current)
        self.sm.transition.direction = direction
        self.sm.current = name

    def open_module(self, info) -> None:
        if not self.sm.has_screen(info.name):
            self.add(info.screen_factory())
        self.go(info.name)

    def back(self) -> bool:
        if not self._history:
            return False
        self.sm.transition.direction = "right"
        self.sm.current = self._history.pop()
        return True

    def drop_except(self, keep: set) -> None:
        """Удалить кэшированные экраны (например, модулей) при смене пользователя."""
        for scr in list(self.sm.screens):
            if scr.name not in keep:
                self.sm.remove_widget(scr)

    def reset(self, name: str) -> None:
        self._history.clear()
        self.sm.current = name
