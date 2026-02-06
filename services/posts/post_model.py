from pydantic import BaseModel, ConfigDict
from services.users.user_model import UserModel


class PostModel(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    text: str
    image: str | None = None
    likes: int | None = None
    owner: UserModel
