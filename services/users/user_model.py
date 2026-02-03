from pydantic import BaseModel, ConfigDict


class UserModel(BaseModel):
    model_config = ConfigDict(extra="ignore")  # игнорируем лишние поля из ответа

    id: str | None = None
    email: str | None = None
    firstName: str | None = None
    lastName: str | None = None
    dateOfBirth: str | None = None
    phone: str | None = None


class UserPreviewModel(BaseModel):
    model_config = ConfigDict(extra="ignore")  # list /user может возвращать дополнительные поля

    id: str | None = None
    title: str | None = None
    firstName: str | None = None
    lastName: str | None = None
    picture: str | None = None
