"""Регистрация, вход, роли и сохранение сессии (автовход)."""
import hashlib
import hmac
import os
from typing import Optional

from models.user import User

ITERATIONS = 120_000
SESSION_KEY = "session_user_id"
ROLES = ("student", "teacher")


class AuthError(Exception):
    """Ошибка с текстом, пригодным для показа пользователю."""


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITERATIONS)
    return f"pbkdf2${ITERATIONS}${salt.hex()}${dk.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        _, iters, salt, digest = stored.split("$")
        dk = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), int(iters))
    except ValueError:
        return False
    return hmac.compare_digest(dk.hex(), digest)


class AuthService:
    def __init__(self, users, db):
        self.users = users          # UserRepo
        self.db = db
        self.current_user: Optional[User] = None

    @property
    def role(self) -> Optional[str]:
        return self.current_user.role if self.current_user else None

    @property
    def is_authenticated(self) -> bool:
        return self.current_user is not None

    def register(self, login: str, password: str, full_name: str, role: str = "student") -> User:
        login, full_name = login.strip().lower(), full_name.strip()
        if not full_name:
            raise AuthError("Введите имя")
        if len(login) < 3:
            raise AuthError("Логин: минимум 3 символа")
        if len(password) < 6:
            raise AuthError("Пароль: минимум 6 символов")
        if role not in ROLES:
            raise AuthError("Неизвестная роль")
        if self.users.get_by_login(login):
            raise AuthError("Такой логин уже занят")
        user = self.users.add(User(login, hash_password(password), full_name, role))
        self._start_session(user)
        return user

    def login(self, login: str, password: str) -> User:
        user = self.users.get_by_login(login.strip().lower())
        if not user or not verify_password(password, user.password_hash):
            raise AuthError("Неверный логин или пароль")
        self._start_session(user)
        return user

    def restore_session(self) -> bool:
        uid = self.db.get_setting(SESSION_KEY, "")
        user = self.users.get(int(uid)) if uid.isdigit() else None
        self.current_user = user
        return user is not None

    def logout(self) -> None:
        self.current_user = None
        self.db.set_setting(SESSION_KEY, "")

    def _start_session(self, user: User) -> None:
        self.current_user = user
        self.db.set_setting(SESSION_KEY, str(user.id))
