from dataclasses import dataclass
from typing import Optional


@dataclass
class Message:
    sender_id: int
    recipient_id: int
    text: str
    sent_at: str
    is_read: int = 0
    id: Optional[int] = None
