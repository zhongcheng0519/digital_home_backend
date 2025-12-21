from typing import Optional
from sqlmodel import Field, SQLModel


class Family(SQLModel, table=True):
    __tablename__ = "family"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    owner_id: int = Field(foreign_key="user.id")


class FamilyMember(SQLModel, table=True):
    __tablename__ = "family_member"
    
    family_id: int = Field(foreign_key="family.id", primary_key=True)
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    role: str = Field(default="member")
    encrypted_family_key: str = Field(sa_column_kwargs={"type_": "Text"})
