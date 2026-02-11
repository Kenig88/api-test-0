from pydantic import BaseModel, ConfigDict
from services.users.user_model import UserModel


class CommentModel(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    message: str
    owner: UserModel | None
    post: str | None
    publishDate: str | None