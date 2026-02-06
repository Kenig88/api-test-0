from pydantic import BaseModel, ConfigDict


class UserModel(BaseModel):
    model_config = ConfigDict(extra="ignore")  # list /user может возвращать другие/неполные поля

    id: str
    email: str | None = None   # <-- ВАЖНО: в списке email часто отсутствует
    firstName: str
    lastName: str
    title: str | None = None
    picture: str | None = None
    dateOfBirth: str | None = None
    phone: str | None = None
