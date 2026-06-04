from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from decimal import Decimal
from uuid import UUID


class PostCreate(BaseModel):
    title :str
    content: str
    published : bool = False
    rating : Optional[Decimal] = Field(default= Decimal('0.00'), max_digits=4, decimal_places=2 )
    
class PostResponse(PostCreate):
    id:UUID
    created_at: datetime
    
    class Config:
        from_attributes = True
        
class PostHomeResponse(BaseModel):
    id: UUID
    title:str
    snippet: str
    created_at: datetime
    
    class Config:
        from_attributes=True
        
class PostPatch(BaseModel):
    title: str | None = None
    content: str | None = None
    published: bool |None = None
    rating : Optional[Decimal] = Field(default= None, max_digits=4, decimal_places=2 )
    
    # -----User Database----#  
    
class CreateUser(BaseModel):
    username: str 
    email: str
    password: str
    
class UserResponse(BaseModel):
    id: UUID
    username: str 
    email: str
    created_at: datetime

    class Config:
        from_attributes=True