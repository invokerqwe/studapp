from typing import Optional

from data.repositories.base import SqliteRepo
from models.user import User


class UserRepo(SqliteRepo[User]):
    table = "users"
    model = User

    def get_by_login(self, login: str) -> Optional[User]:
        found = self.list(login=login)
        return found[0] if found else None

    def list_by_role(self, role: str) -> list[User]:
        return self.list(role=role)
