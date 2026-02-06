from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from services.users.user_model import UserPreviewModel


class PostPreviewModel(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    text: str
    image: Optional[str] = None
    likes: Optional[int] = 0
    tags: Optional[List[str]] = None
    owner: Optional[UserPreviewModel] = None


class PostModel(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    text: str
    image: Optional[str] = None
    likes: Optional[int] = 0
    tags: Optional[List[str]] = None
    owner: Optional[UserPreviewModel] = None
