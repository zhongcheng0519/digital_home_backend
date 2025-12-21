from typing import Optional
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "user"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    phone: str = Field(unique=True, index=True)
    username: str
    hashed_password: str
    public_key: str = Field(sa_column_kwargs={"type_": "Text"})
    encrypted_private_key: str = Field(sa_column_kwargs={"type_": "Text"})
