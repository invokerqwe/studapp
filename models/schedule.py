from dataclasses import dataclass
from typing import Optional


@dataclass
class Lesson:
    subject: str
    weekday: int                   # 0=пн .. 6=вс
    start_time: str                # HH:MM
    end_time: str
    room: str = ""
    teacher_id: Optional[int] = None
    group_name: str = ""
    id: Optional[int] = None
