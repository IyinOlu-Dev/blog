from decimal import Decimal
from uuid import UUID
import uuid
from sqlalchemy import Numeric, text
from datetime import datetime
from backend.database import Base
from sqlalchemy.orm import Mapped, mapped_column


class PostModel(Base):
    __tablename__ = "post_table"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, index= True, default=uuid.uuid4)
    title: Mapped[str | None]
    content: Mapped[str | None] 
    published: Mapped[bool | None] = mapped_column(server_default=text("False"))
    rating: Mapped[Decimal | None] = mapped_column(Numeric(precision=4, scale=2))
    created_at: Mapped[datetime] = mapped_column(server_default=text("now()"))
    
    
class User(Base):
    __tablename__ = "user"
    
    id: Mapped[UUID] =  mapped_column(primary_key= True, index=True, default=uuid.uuid4, unique= True, nullable=False )
    username: Mapped[str | None] = mapped_column(unique=True)
    email: Mapped[str | None] = mapped_column( unique= True)
    password: Mapped[str | None] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=text("now()"))
    
    