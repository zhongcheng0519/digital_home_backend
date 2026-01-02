from typing import Annotated, List, Literal
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.api.deps import get_current_user
from app.db.session import get_session
from app.models.user import User
from app.models.family import Family, FamilyMember

router = APIRouter()


class CreateFamilyRequest(BaseModel):
    name: str
    encrypted_family_key: str
    role: Literal["男主人", "女主人"] = "男主人"


class FamilyResponse(BaseModel):
    id: int
    name: str
    owner_id: int


class AddMemberRequest(BaseModel):
    family_id: int
    target_phone: str
    encrypted_key_for_target: str
    role: Literal["男主人", "女主人", "儿子", "女儿", "爸爸", "妈妈", "岳父", "岳母"] = "儿子"


class FamilyWithKeyResponse(BaseModel):
    id: int
    name: str
    owner_id: int
    role: str
    encrypted_family_key: str


class FamilyMemberResponse(BaseModel):
    user_id: int
    phone: str
    username: str
    role: str


@router.post("/", response_model=FamilyResponse)
async def create_family(
    request: CreateFamilyRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)]
):
    family = Family(
        name=request.name,
        owner_id=current_user.id
    )
    session.add(family)
    await session.commit()
    await session.refresh(family)
    
    family_member = FamilyMember(
        family_id=family.id,
        user_id=current_user.id,
        role=request.role,
        encrypted_family_key=request.encrypted_family_key
    )
    session.add(family_member)
    await session.commit()
    
    return FamilyResponse(
        id=family.id,
        name=family.name,
        owner_id=family.owner_id
    )


@router.post("/member")
async def add_member(
    request: AddMemberRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)]
):
    result = await session.execute(
        select(Family).where(Family.id == request.family_id)
    )
    family = result.scalar_one_or_none()
    if not family:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Family not found"
        )
    
    if family.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can add members"
        )
    
    result = await session.execute(
        select(User).where(User.phone == request.target_phone)
    )
    target_user = result.scalar_one_or_none()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    result = await session.execute(
        select(FamilyMember).where(
            FamilyMember.family_id == request.family_id,
            FamilyMember.user_id == target_user.id
        )
    )
    existing_member = result.scalar_one_or_none()
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member of this family"
        )
    
    family_member = FamilyMember(
        family_id=request.family_id,
        user_id=target_user.id,
        role=request.role,
        encrypted_family_key=request.encrypted_key_for_target
    )
    session.add(family_member)
    await session.commit()
    
    return {"message": "Member added successfully"}


@router.get("/my", response_model=List[FamilyWithKeyResponse])
async def get_my_families(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)]
):
    result = await session.execute(
        select(FamilyMember, Family).join(Family).where(
            FamilyMember.user_id == current_user.id
        )
    )
    rows = result.all()
    
    families = []
    for family_member, family in rows:
        families.append(FamilyWithKeyResponse(
            id=family.id,
            name=family.name,
            owner_id=family.owner_id,
            role=family_member.role,
            encrypted_family_key=family_member.encrypted_family_key
        ))
    
    return families


@router.get("/{family_id}/members", response_model=List[FamilyMemberResponse])
async def get_family_members(
    family_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)]
):
    result = await session.execute(
        select(FamilyMember).where(FamilyMember.family_id == family_id)
    )
    family_members = result.scalars().all()
    
    if not family_members:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Family not found"
        )
    
    is_member = any(fm.user_id == current_user.id for fm in family_members)
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this family"
        )
    
    members = []
    for family_member in family_members:
        result = await session.execute(
            select(User).where(User.id == family_member.user_id)
        )
        user = result.scalar_one_or_none()
        if user:
            members.append(FamilyMemberResponse(
                user_id=user.id,
                phone=user.phone,
                username=user.username,
                role=family_member.role
            ))
    
    return members
