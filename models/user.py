from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    login: str
    password_hash: str
    full_name: str
    role: str = "student"          # student | teacher
    id: Optional[int] = None
