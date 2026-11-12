"""Локальные уведомления: plyer (Android/Windows), запасной вариант — toast."""
from kivy.utils import platform


class NotificationService:
    def request_permission(self) -> None:
        if platform != "android":
            return
        try:
            from android.permissions import request_permissions   # type: ignore
            request_permissions(["android.permission.POST_NOTIFICATIONS"])
        except Exception:
            pass

    def notify(self, title: str, message: str) -> None:
        try:
            from plyer import notification
            notification.notify(title=title, message=message, app_name="Учебный процесс", timeout=10)
        except Exception:
            try:
                from kivymd.toast import toast
                toast(f"{title}: {message}")
            except Exception:
                print(f"[notify] {title}: {message}")
