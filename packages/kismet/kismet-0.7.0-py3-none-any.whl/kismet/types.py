from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Message:
  message_id: int
  author_id: int
  created_at: datetime
  edited_at: Optional[datetime]
  reply_id: Optional[int]
  content: str