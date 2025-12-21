from typing import Optional
from datetime import date, datetime
from sqlmodel import Field, SQLModel


class Milestone(SQLModel, table=True):
    __tablename__ = "milestone"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    family_id: int = Field(foreign_key="family.id", index=True)
    creator_id: int = Field(foreign_key="user.id")
    event_date: date
    content_ciphertext: str = Field(sa_column_kwargs={"type_": "Text"})
    created_at: datetime = Field(default_factory=datetime.utcnow)
