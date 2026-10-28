import schemas
from core.security import required_role
from database.models import User, UserRole
from database.session import get_db
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from services.songs_services import create_song
from sqlalchemy.orm import Session

router = APIRouter()


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.SongResponse,
)
def add_song(
    title: str = Form(..., min_length=1, max_length=100),
    cover_url: str | None = Form(None),
    is_public: bool = Form(True),
    audio_file: UploadFile = File(...),
    current_user: User = Depends(required_role(UserRole.Musician)),
    db: Session = Depends(get_db),
):

    song_in = schemas.SongCreate(title=title, cover_url=cover_url, is_public=is_public)

    song = create_song(db, song_in, audio_file, current_user.id)
    if not song:
        raise HTTPException(status_code=400, detail="Invalid audio file")
    return song
