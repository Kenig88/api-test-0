from pydantic import BaseModel, ConfigDict


class UserPreviewModel(BaseModel):
    """User preview used as nested object in Post/Comment responses."""
    model_config = ConfigDict(extra="ignore")

    id: str
    title: str | None = None
    firstName: str | None = None
    lastName: str | None = None
    picture: str | None = None
