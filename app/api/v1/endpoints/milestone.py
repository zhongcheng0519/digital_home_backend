from typing import Annotated, List, Optional
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.api.deps import get_current_user
from app.db.session import get_session
from app.models.user import User
from app.models.family import FamilyMember
from app.models.milestone import Milestone

router = APIRouter()


class CreateMilestoneRequest(BaseModel):
    family_id: int
    event_date: date
    content_ciphertext: str


class MilestoneResponse(BaseModel):
    id: int
    family_id: int
    creator_id: int
    event_date: date
    content_ciphertext: str
    created_at: datetime


@router.post("/", response_model=MilestoneResponse)
async def create_milestone(
    request: CreateMilestoneRequest,
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
    
    milestone = Milestone(
        family_id=request.family_id,
        creator_id=current_user.id,
        event_date=request.event_date,
        content_ciphertext=request.content_ciphertext
    )
    session.add(milestone)
    await session.commit()
    await session.refresh(milestone)
    
    return MilestoneResponse(
        id=milestone.id,
        family_id=milestone.family_id,
        creator_id=milestone.creator_id,
        event_date=milestone.event_date,
        content_ciphertext=milestone.content_ciphertext,
        created_at=milestone.created_at
    )


@router.get("/", response_model=List[MilestoneResponse])
async def get_milestones(
    family_id: int = Query(...),
    year: Optional[int] = Query(None),
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
    
    query = select(Milestone).where(Milestone.family_id == family_id)
    
    if year:
        query = query.where(
            Milestone.event_date >= date(year, 1, 1),
            Milestone.event_date <= date(year, 12, 31)
        )
    
    query = query.order_by(Milestone.event_date.desc())
    
    result = await session.execute(query)
    milestones = result.scalars().all()
    
    return [
        MilestoneResponse(
            id=m.id,
            family_id=m.family_id,
            creator_id=m.creator_id,
            event_date=m.event_date,
            content_ciphertext=m.content_ciphertext,
            created_at=m.created_at
        )
        for m in milestones
    ]
