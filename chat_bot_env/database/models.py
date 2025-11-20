from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class User:
    id: int
    username: Optional[str]
    first_name: Optional[str]
    created_at: datetime


@dataclass
class Note:
    id: int
    user_id: int
    title: str
    content: Optional[str]
    status: str
    is_pinned: bool
    created_at: datetime
    updated_at: datetime
    tags: List[str] = None


@dataclass
class Tag:
    id: int
    user_id: int
    name: str


@dataclass
class Reminder:
    id: int
    note_id: int
    reminder_time: datetime
    reminder_type: str
    is_active: bool
    created_at: datetime
