from typing import Optional, Literal
from datetime import datetime
from sqlmodel import Field, SQLModel, Column, String


class Todo(SQLModel, table=True):
    __tablename__ = "todo"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    family_id: int = Field(foreign_key="family.id", index=True)
    creator_id: int = Field(foreign_key="user.id")
    title_ciphertext: str = Field(sa_column=Column(String))
    description_ciphertext: Optional[str] = Field(default=None, sa_column=Column(String))
    category: Optional[Literal["生活", "学习", "运动", "心愿"]] = Field(default="生活", sa_column=Column(String))
    is_completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
