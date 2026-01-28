from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class UserPreviewModel(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    title: Optional[str] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    picture: Optional[str] = None


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
