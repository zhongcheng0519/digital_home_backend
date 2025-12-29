from typing import Optional
from sqlmodel import Field, SQLModel, Column, String


class User(SQLModel, table=True):
    __tablename__ = "user"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    phone: str = Field(unique=True, index=True)
    username: str
    hashed_password: str
    public_key: str = Field(sa_column=Column(String))
    encrypted_private_key: str = Field(sa_column=Column(String))
    private_key_salt: str = Field(sa_column=Column(String))
