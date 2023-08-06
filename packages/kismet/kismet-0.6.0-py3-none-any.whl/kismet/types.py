from dataclasses import dataclass
from datetime import datetime

@dataclass
class Message:
  author_id: int
  message_id: int
  created_at: datetime
  edited_at: datetime
  content: str