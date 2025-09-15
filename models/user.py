
from __future__ import annotations
from datetime import datetime
from typing import Annotated
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, EmailStr, ConfigDict

Name = Annotated[str, Field(min_length=1, max_length=80, description="User display name")]

class User(BaseModel):
    """User DTO for API input/output."""
    model_config = ConfigDict(extra='forbid')  # reject unknown fields

    id: UUID = Field(default_factory=uuid4, description="Server-assigned unique identifier")
    email: EmailStr = Field(description="Unique email address")
    name: Name
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp (UTC)")
