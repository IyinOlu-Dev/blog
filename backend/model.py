from decimal import Decimal
from uuid import UUID
# import uuid
from sqlalchemy import Numeric, text, ForeignKey
from datetime import datetime
from backend.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship


class PostModel(Base):
    __tablename__ = "post_table"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, index= True, default=uuid.uuid4)
    title: Mapped[str | None]
    content: Mapped[str | None] 
    published: Mapped[bool | None] = mapped_column(server_default=text("false"), default=False)
    likes: Mapped[int | None]
    created_at: Mapped[datetime] = mapped_column(server_default=text("now()"))
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user_table.id"), nullable =False, index=True)
    owner: Mapped["UserModel"] = relationship("UserModel", back_populates="posts")
    
class UserModel(Base):
    __tablename__ = "user_table"
    
    id: Mapped[UUID] =  mapped_column(primary_key= True, index=True, default=uuid.uuid4, unique= True, nullable=False )
    username: Mapped[str | None] = mapped_column(unique=True)
    email: Mapped[str | None] = mapped_column( unique= True)
    password: Mapped[str | None] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=text("now()"))
    posts: Mapped[list["PostModel"]] = relationship("PostModel", back_populates="owner")
    
class LikedModel(Base):
    __tablename__ = "likes"    
    post_id: Mapped[UUID] = mapped_column(ForeignKey("post_table.id", ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user_table.id", ondelete="CASCADE"), primary_key=True)