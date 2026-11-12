from dataclasses import dataclass
from typing import Optional


@dataclass
class Deadline:
    user_id: int
    title: str
    due_at: str                    # YYYY-MM-DD HH:MM
    subject: str = ""
    done: int = 0
    id: Optional[int] = None
