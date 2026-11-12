from dataclasses import dataclass
from typing import Optional


@dataclass
class Grade:
    student_id: int
    subject: str
    value: float
    date: str                      # YYYY-MM-DD
    comment: str = ""
    id: Optional[int] = None
