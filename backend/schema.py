from pydantic import BaseModel, Field, EmailStr, computed_field
from datetime import datetime
from typing import Optional
from decimal import Decimal
from uuid import UUID


class PostCreate(BaseModel):
    title :str
    content: str
    published : bool = False
        
class PostResponse(PostCreate):
    id:UUID
    created_at: datetime
    user_id: UUID
    
    model_config= {"from_attributes": True}
        
class PostHomeResponse(BaseModel):
    id: UUID
    user_id: UUID
    title:str
    content: str = Field(exclude=True)
    created_at: datetime
    
    @computed_field
    @property
    def snippet (self) -> str:
        if self.content and len (self.content) > 30:
            return f"{self.content[:30]}..."
        return self.content or ""
    model_config= {"from_attributes": True}
    
class PostPatch(BaseModel):
    title: str | None = None
    content: str | None = None
    published: bool |None = None
    rating : Optional[Decimal] = Field(default= None, max_digits=4, decimal_places=2 )
    
    
class PostLikes(BaseModel):
    id: UUID
    user_id : UUID
    
    model_config= {"from_attributes": True}
        
    # -----User Database----#  
    
class CreateUser(BaseModel):
    username: str 
    email: EmailStr
    password: str
    
class UserResponse(BaseModel):
    id: UUID
    username: str 
    email: str
    created_at: datetime

    model_config= {"from_attributes": True}
        
class LoginRequest(BaseModel):
    identifier: str
    password: str
    

class UserPosts(UserResponse):
    posts: list[PostResponse] = []
    
    model_config= {"from_attributes": True}