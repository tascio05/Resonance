import os
import shutil
import uuid

import mutagen
import schemas
from database.models import Favourite, Song
from fastapi import UploadFile
from sqlalchemy.orm import Session


def create_song(
    db: Session,
    song_in: schemas.SongCreate,
    audio_file: UploadFile,
    user_id: int,
) -> Song | None:
    os.makedirs("uploads/songs", exist_ok=True)

    _, ext = os.path.splitext(audio_file.filename)
    file_path = f"uploads/songs/{uuid.uuid4()}{ext}"

    audio_file.file.seek(0)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(audio_file.file, buffer)

    try:
        audio = mutagen.File(file_path)

        if not audio or not audio.info:
            raise ValueError("File is not a valid audio")

        length_seconds = int(audio.info.length)
    except Exception:
        os.remove(file_path)
        return None

    new_song = Song(
        user_id=user_id,
        title=song_in.title,
        cover_url=song_in.cover_url,
        is_public=song_in.is_public,
        audio_url=file_path,
        length_seconds=length_seconds,
    )

    db.add(new_song)
    db.commit()
    db.refresh(new_song)
    return new_song


def get_public_songs(db: Session, skip: int = 0, limit: int = 20) -> list[Song]:
    return (
        db.query(Song)
        .filter(Song.is_public == True, Song.is_active == True)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_song_by_id(db: Session, song_id: int) -> Song | None:
    return db.query(Song).filter(Song.id == song_id, Song.is_active == True).first()


def deactivate_song(db: Session, song: Song) -> Song:
    song.is_active = False
    db.commit()
    db.refresh(song)
    return song


def get_favourite(db: Session, user_id: int, song_id: int) -> Favourite | None:
    return (
        db.query(Favourite)
        .filter(Favourite.user_id == user_id, Favourite.song_id == song_id)
        .first()
    )


def add_favourite_song(db: Session, user_id: int, song_id: int) -> Favourite:
    new_favourite = Favourite(user_id=user_id, song_id=song_id)
    db.add(new_favourite)
    db.commit()
    db.refresh(new_favourite)
    return new_favourite


def remove_favourite_song(db: Session, favourite: Favourite) -> None:
    db.delete(favourite)
    db.commit()

def get_favourite_songs(db: Session, user_id: int, skip: int = 0, limit: int = 20) -> list[Song]:
    return (
        db.query(Song).join(Favourite).filter(Favourite.user_id == user_id, Song.is_public == True, Song.is_active == True)
        .offset(skip)
        .limit(limit)
        .all()
    )
    