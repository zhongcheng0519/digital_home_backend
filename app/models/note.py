from typing import Optional, Literal
from datetime import datetime
from sqlmodel import Field, SQLModel, Column, String


class Note(SQLModel, table=True):
    __tablename__ = "note"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    family_id: int = Field(foreign_key="family.id", index=True)
    creator_id: int = Field(foreign_key="user.id")
    title_ciphertext: str = Field(sa_column=Column(String))
    content_ciphertext: str = Field(sa_column=Column(String))
    category: Optional[Literal["地址信息", "药方"]] = Field(default="地址信息", sa_column=Column(String))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
