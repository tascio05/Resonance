import schemas
from core.security import get_current_user, required_role
from database.models import User, UserRole
from database.session import get_db
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from services.songs_services import create_song, get_public_songs, get_song_by_id
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


@router.get("/", response_model=list[schemas.SongResponse])
def read_public_songs(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_public_songs(db, skip=skip, limit=limit)


@router.get("/{song_id}", response_model=schemas.SongResponse)
def read_song_by_id(
    song_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    song = get_song_by_id(db, song_id)
    if not song or (not song.is_public and song.user_id != current_user.id):
        raise HTTPException(status_code=404, detail="Song not found")
    return song
