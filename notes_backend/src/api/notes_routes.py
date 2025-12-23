from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from src.auth import get_current_user
from src.db import get_db
from src.models import Note, User
from src.schemas import NoteCreate, NoteOut, NoteUpdate

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get(
    "",
    response_model=List[NoteOut],
    summary="List notes (optionally search)",
    description="Returns notes for the authenticated user. Use `q` to search by title/content.",
)
# PUBLIC_INTERFACE
def list_notes(
    q: Optional[str] = Query(None, description="Search query over title/content."),
    limit: int = Query(100, ge=1, le=200, description="Max number of notes to return."),
    offset: int = Query(0, ge=0, description="Pagination offset."),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> List[NoteOut]:
    """List notes belonging to the authenticated user, optionally filtered by query."""
    stmt = select(Note).where(Note.user_id == user.id)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(or_(Note.title.ilike(like), Note.content.ilike(like)))
    stmt = stmt.order_by(Note.updated_at.desc()).limit(limit).offset(offset)
    return list(db.scalars(stmt).all())


@router.post(
    "",
    response_model=NoteOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a note",
    description="Creates a new note for the authenticated user.",
)
# PUBLIC_INTERFACE
def create_note(
    payload: NoteCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> NoteOut:
    """Create a note for the authenticated user."""
    note = Note(user_id=user.id, title=payload.title, content=payload.content)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.get(
    "/{note_id}",
    response_model=NoteOut,
    summary="Get a note",
    description="Returns a single note owned by the authenticated user.",
)
# PUBLIC_INTERFACE
def get_note(
    note_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> NoteOut:
    """Get a note by id, only if owned by current user."""
    note = db.get(Note, note_id)
    if not note or note.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note


@router.put(
    "/{note_id}",
    response_model=NoteOut,
    summary="Update a note",
    description="Updates a note owned by the authenticated user.",
)
# PUBLIC_INTERFACE
def update_note(
    note_id: int,
    payload: NoteUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> NoteOut:
    """Update a note (title/content) if owned by current user."""
    note = db.get(Note, note_id)
    if not note or note.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    if payload.title is not None:
        note.title = payload.title
    if payload.content is not None:
        note.content = payload.content

    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.delete(
    "/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a note",
    description="Deletes a note owned by the authenticated user.",
)
# PUBLIC_INTERFACE
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    """Delete a note if owned by current user."""
    note = db.get(Note, note_id)
    if not note or note.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    db.delete(note)
    db.commit()
    return None
