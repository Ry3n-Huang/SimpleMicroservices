
from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Annotated, Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

Title = Annotated[str, Field(min_length=1, max_length=120, description="Short task title")]

class Priority(str, Enum):
    low = "low"
    normal = "normal"
    high = "high"

class Todo(BaseModel):
    """Simple task owned by a user."""
    model_config = ConfigDict(extra='forbid')

    id: UUID = Field(description="Task identifier")
    owner_id: UUID = Field(description="User.id that owns this task")
    title: Title
    completed: bool = Field(default=False, description="Completion flag")
    priority: Priority = Field(default=Priority.normal)
    due_date: Optional[datetime] = Field(default=None, description="Optional deadline (UTC)")
    created_at: datetime = Field(default_factory=datetime.utcnow)
