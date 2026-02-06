from pydantic import BaseModel, ConfigDict
from services.users.user_model import UserPreviewModel


class PostPreviewModel(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    text: str
    image: str | None = None
    likes: int | None = None
    tags: list[str] = None
    owner: UserPreviewModel


class PostModel(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    text: str
    image: str | None = None
    likes: int | None = None
    tags: list[str] = None
    owner: UserPreviewModel