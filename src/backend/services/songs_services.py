import os
import shutil
import uuid

import mutagen
import schemas
from database.models import Song
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
