"""Реестр модулей: модуль подключается одной строкой registry.register(ModuleInfo(...))."""
import importlib
import pkgutil
from dataclasses import dataclass
from typing import Callable, Optional


@dataclass
class ModuleInfo:
    name: str                      # id модуля и имя его экрана
    title: str                     # заголовок в меню
    icon: str                      # иконка MDI
    screen_factory: Callable       # () -> Screen (name == ModuleInfo.name)
    roles: tuple = ("student", "teacher")
    order: int = 100


class ModuleRegistry:
    def __init__(self):
        self._mods: dict[str, ModuleInfo] = {}
        self.periodic: list[tuple[Callable, float]] = []   # (fn(app), интервал в сек)

    def register(self, info: ModuleInfo) -> None:
        self._mods[info.name] = info

    def register_periodic(self, fn: Callable, interval: float) -> None:
        self.periodic.append((fn, interval))

    def get(self, name: str) -> Optional[ModuleInfo]:
        return self._mods.get(name)

    def for_role(self, role: Optional[str] = None) -> list[ModuleInfo]:
        mods = [m for m in self._mods.values() if role is None or role in m.roles]
        return sorted(mods, key=lambda m: (m.order, m.title))

    def discover(self, package: str = "modules") -> None:
        """Импортирует modules/*/module.py и вызывает register(registry), если он есть."""
        pkg = importlib.import_module(package)
        for m in pkgutil.iter_modules(pkg.__path__):
            target = f"{package}.{m.name}.module"
            try:
                mod = importlib.import_module(target)
            except ModuleNotFoundError as e:
                if e.name == target:   # у пакета нет module.py — пропускаем
                    continue
                raise
            if hasattr(mod, "register"):
                mod.register(self)
