from typing import Annotated, List, Optional, Literal
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.api.deps import get_current_user
from app.db.session import get_session
from app.models.user import User
from app.models.family import FamilyMember
from app.models.note import Note

router = APIRouter()


class CreateNoteRequest(BaseModel):
    family_id: int
    title_ciphertext: str
    content_ciphertext: str
    category: Optional[Literal["地址信息", "药方"]] = "地址信息"


class UpdateNoteRequest(BaseModel):
    title_ciphertext: Optional[str] = None
    content_ciphertext: Optional[str] = None
    category: Optional[Literal["地址信息", "药方"]] = None


class NoteResponse(BaseModel):
    id: int
    family_id: int
    creator_id: int
    title_ciphertext: str
    content_ciphertext: str
    category: Optional[Literal["地址信息", "药方"]]
    created_at: datetime
    updated_at: datetime


@router.post("/", response_model=NoteResponse)
async def create_note(
    request: CreateNoteRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)]
):
    result = await session.execute(
        select(FamilyMember).where(
            FamilyMember.family_id == request.family_id,
            FamilyMember.user_id == current_user.id
        )
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this family"
        )
    
    note = Note(
        family_id=request.family_id,
        creator_id=current_user.id,
        title_ciphertext=request.title_ciphertext,
        content_ciphertext=request.content_ciphertext,
        category=request.category or "地址信息"
    )
    session.add(note)
    await session.commit()
    await session.refresh(note)
    
    return NoteResponse(
        id=note.id,
        family_id=note.family_id,
        creator_id=note.creator_id,
        title_ciphertext=note.title_ciphertext,
        content_ciphertext=note.content_ciphertext,
        category=note.category,
        created_at=note.created_at,
        updated_at=note.updated_at
    )


@router.get("/", response_model=List[NoteResponse])
async def get_notes(
    family_id: int = Query(...),
    category: Optional[Literal["地址信息", "药方"]] = None,
    *,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)]
):
    result = await session.execute(
        select(FamilyMember).where(
            FamilyMember.family_id == family_id,
            FamilyMember.user_id == current_user.id
        )
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this family"
        )
    
    query = select(Note).where(Note.family_id == family_id)
    if category:
        query = query.where(Note.category == category)
    query = query.order_by(Note.created_at.desc())
    
    result = await session.execute(query)
    notes = result.scalars().all()
    
    return [
        NoteResponse(
            id=n.id,
            family_id=n.family_id,
            creator_id=n.creator_id,
            title_ciphertext=n.title_ciphertext,
            content_ciphertext=n.content_ciphertext,
            category=n.category,
            created_at=n.created_at,
            updated_at=n.updated_at
        )
        for n in notes
    ]


@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: int,
    request: UpdateNoteRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)]
):
    result = await session.execute(
        select(Note).where(Note.id == note_id)
    )
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    result = await session.execute(
        select(FamilyMember).where(
            FamilyMember.family_id == note.family_id,
            FamilyMember.user_id == current_user.id
        )
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this family"
        )
    
    if request.title_ciphertext is not None:
        note.title_ciphertext = request.title_ciphertext
    if request.content_ciphertext is not None:
        note.content_ciphertext = request.content_ciphertext
    if request.category is not None:
        note.category = request.category
    
    note.updated_at = datetime.utcnow()
    
    await session.commit()
    await session.refresh(note)
    
    return NoteResponse(
        id=note.id,
        family_id=note.family_id,
        creator_id=note.creator_id,
        title_ciphertext=note.title_ciphertext,
        content_ciphertext=note.content_ciphertext,
        category=note.category,
        created_at=note.created_at,
        updated_at=note.updated_at
    )


@router.delete("/{note_id}")
async def delete_note(
    note_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)]
):
    result = await session.execute(
        select(Note).where(Note.id == note_id)
    )
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    result = await session.execute(
        select(FamilyMember).where(
            FamilyMember.family_id == note.family_id,
            FamilyMember.user_id == current_user.id
        )
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this family"
        )
    
    await session.delete(note)
    await session.commit()
    
    return {"message": "Note deleted successfully"}
