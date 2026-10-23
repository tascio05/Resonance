from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    password: str = Field(..., min_length=8, max_length=128)

    model_config = ConfigDict(str_strip_whitespace=True)


class UserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SongCreate(BaseModel):
    title: str = (Field(..., min_length=1, max_length=100),)
    cover_url: str | None = None
    is_public: bool = True


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


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
