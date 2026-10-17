from datetime import datetime
from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SongResponse(BaseModel):
    id: int
    user_id: int
    title: str
    length_seconds: int
    cover_url: str | None = None
    audio_url: str
    is_public: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
