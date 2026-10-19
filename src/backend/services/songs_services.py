import os
import shutil
import uuid

import mutagen
from database.models import Song
from fastapi import UploadFile
from sqlalchemy.orm import Session


def create_song(
    db: Session,
    title: str,
    cover_url: str | None,
    is_public: bool,
    audio_file: UploadFile,
    user_id: int,
) -> Song | None:
    os.makedirs("uploads/songs", exist_ok=True)
    file_path = f"uploads/songs/{uuid.uuid4()}.mp3"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(audio_file.file, buffer)

    audio = mutagen.File(file_path)

    if not audio or not audio.info:
        os.remove(file_path)
        return None

    length_seconds = int(audio.info.length)

    new_song = Song(
        user_id=user_id,
        title=title,
        cover_url=cover_url,
        audio_url=file_path,
        length_seconds=length_seconds,
        is_public=is_public,
    )

    db.add(new_song)
    db.commit()
    db.refresh(new_song)
    return new_song
