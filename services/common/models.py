from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, ConfigDict


class UserPreviewModel(BaseModel):
    """User preview used as nested object in Post/Comment responses."""
    model_config = ConfigDict(extra="ignore")

    id: str
    title: Optional[str] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    picture: Optional[str] = None
