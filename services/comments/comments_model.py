from typing import Optional
from pydantic import BaseModel, ConfigDict


class UserPreviewModel(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    title: Optional[str] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    picture: Optional[str] = None


class CommentPreviewModel(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    message: str
    owner: Optional[UserPreviewModel] = None
    post: Optional[str] = None
    publishDate: Optional[str] = None


class CommentModel(CommentPreviewModel):
    # у DummyAPI Comment = то же самое, просто “full”
    pass
