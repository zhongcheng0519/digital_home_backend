from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.core.security import create_access_token, get_password_hash, verify_password
from app.db.session import get_session
from app.models.user import User

router = APIRouter()


class RegisterRequest(BaseModel):
    phone: str
    username: str
    password: str
    public_key: str
    encrypted_private_key: str


class LoginRequest(BaseModel):
    phone: str
    password: str


class UserInfo(BaseModel):
    id: int
    phone: str
    username: str
    public_key: str
    encrypted_private_key: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_info: UserInfo


@router.post("/register", response_model=UserInfo)
async def register(
    request: RegisterRequest,
    session: Annotated[AsyncSession, Depends(get_session)]
):
    result = await session.execute(select(User).where(User.phone == request.phone))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered"
        )
    
    user = User(
        phone=request.phone,
        username=request.username,
        hashed_password=get_password_hash(request.password),
        public_key=request.public_key,
        encrypted_private_key=request.encrypted_private_key
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    
    return UserInfo(
        id=user.id,
        phone=user.phone,
        username=user.username,
        public_key=user.public_key,
        encrypted_private_key=user.encrypted_private_key
    )


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    session: Annotated[AsyncSession, Depends(get_session)]
):
    result = await session.execute(select(User).where(User.phone == request.phone))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect phone or password"
        )
    
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return LoginResponse(
        access_token=access_token,
        user_info=UserInfo(
            id=user.id,
            phone=user.phone,
            username=user.username,
            public_key=user.public_key,
            encrypted_private_key=user.encrypted_private_key
        )
    )
