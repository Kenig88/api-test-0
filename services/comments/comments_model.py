from typing import Optional
from pydantic import BaseModel, ConfigDict
from services.users.user_model import UserPreviewModel


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
