import enum

from database.session import Base
from sqlalchemy import TIMESTAMP, Boolean, Column, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class UserRole(enum.Enum):
    Admin = 0
    Listener = 1
    Musician = 2


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.Listener, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    songs = relationship("Song", back_populates="owner")
    favourites = relationship("Favourite", back_populates="user")


class Song(Base):
    __tablename__ = "songs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    title = Column(String, nullable=False)
    cover_url = Column(String, default=None)
    audio_url = Column(String, nullable=False)
    length_seconds = Column(Integer, nullable=False)
    is_public = Column(Boolean, default=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    owner = relationship("User", back_populates="songs")
    favourited_by = relationship("Favourite", back_populates="song")


class Favourite(Base):
    __tablename__ = "favourites"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True, index=True)
    song_id = Column(Integer, ForeignKey("songs.id"), primary_key=True, index=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship("User", back_populates="favourites")
    song = relationship("Song", back_populates="favourited_by")
