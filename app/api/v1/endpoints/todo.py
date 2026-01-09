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
from app.models.todo import Todo

router = APIRouter()


class CreateTodoRequest(BaseModel):
    family_id: int
    title_ciphertext: str
    description_ciphertext: Optional[str] = None
    category: Optional[Literal["生活", "学习", "运动", "心愿"]] = "生活"


class UpdateTodoRequest(BaseModel):
    title_ciphertext: Optional[str] = None
    description_ciphertext: Optional[str] = None
    category: Optional[Literal["生活", "学习", "运动", "心愿"]] = None
    is_completed: Optional[bool] = None


class TodoResponse(BaseModel):
    id: int
    family_id: int
    creator_id: int
    title_ciphertext: str
    description_ciphertext: Optional[str]
    category: Optional[Literal["生活", "学习", "运动", "心愿"]]
    is_completed: bool
    created_at: datetime
    updated_at: datetime


@router.post("/", response_model=TodoResponse)
async def create_todo(
    request: CreateTodoRequest,
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
    
    todo = Todo(
        family_id=request.family_id,
        creator_id=current_user.id,
        title_ciphertext=request.title_ciphertext,
        description_ciphertext=request.description_ciphertext,
        category=request.category or "生活",
        is_completed=False
    )
    session.add(todo)
    await session.commit()
    await session.refresh(todo)
    
    return TodoResponse(
        id=todo.id,
        family_id=todo.family_id,
        creator_id=todo.creator_id,
        title_ciphertext=todo.title_ciphertext,
        description_ciphertext=todo.description_ciphertext,
        category=todo.category,
        is_completed=todo.is_completed,
        created_at=todo.created_at,
        updated_at=todo.updated_at
    )


@router.get("/", response_model=List[TodoResponse])
async def get_todos(
    family_id: int = Query(...),
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
    
    query = select(Todo).where(Todo.family_id == family_id).order_by(Todo.created_at.desc())
    
    result = await session.execute(query)
    todos = result.scalars().all()
    
    return [
        TodoResponse(
            id=t.id,
            family_id=t.family_id,
            creator_id=t.creator_id,
            title_ciphertext=t.title_ciphertext,
            description_ciphertext=t.description_ciphertext,
            category=t.category,
            is_completed=t.is_completed,
            created_at=t.created_at,
            updated_at=t.updated_at
        )
        for t in todos
    ]


@router.put("/{todo_id}", response_model=TodoResponse)
async def update_todo(
    todo_id: int,
    request: UpdateTodoRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)]
):
    result = await session.execute(
        select(Todo).where(Todo.id == todo_id)
    )
    todo = result.scalar_one_or_none()
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
    
    result = await session.execute(
        select(FamilyMember).where(
            FamilyMember.family_id == todo.family_id,
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
        todo.title_ciphertext = request.title_ciphertext
    if request.description_ciphertext is not None:
        todo.description_ciphertext = request.description_ciphertext
    if request.category is not None:
        todo.category = request.category
    if request.is_completed is not None:
        todo.is_completed = request.is_completed
    
    todo.updated_at = datetime.utcnow()
    
    await session.commit()
    await session.refresh(todo)
    
    return TodoResponse(
        id=todo.id,
        family_id=todo.family_id,
        creator_id=todo.creator_id,
        title_ciphertext=todo.title_ciphertext,
        description_ciphertext=todo.description_ciphertext,
        category=todo.category,
        is_completed=todo.is_completed,
        created_at=todo.created_at,
        updated_at=todo.updated_at
    )


@router.delete("/{todo_id}")
async def delete_todo(
    todo_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)]
):
    result = await session.execute(
        select(Todo).where(Todo.id == todo_id)
    )
    todo = result.scalar_one_or_none()
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
    
    result = await session.execute(
        select(FamilyMember).where(
            FamilyMember.family_id == todo.family_id,
            FamilyMember.user_id == current_user.id
        )
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this family"
        )
    
    await session.delete(todo)
    await session.commit()
    
    return {"message": "Todo deleted successfully"}
