from decimal import Decimal
from uuid import UUID
import uuid
from sqlalchemy import Numeric, text
from datetime import datetime
from database import Base
from sqlalchemy.orm import Mapped, mapped_column


class PostModel(Base):
    __tablename__ = "post_table"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, index= True, default=uuid.uuid4)
    title: Mapped[str] 
    content: Mapped[str]
    published: Mapped[bool] = mapped_column(server_default=text("False"))
    rating: Mapped[Decimal] = mapped_column(Numeric(precision=4, scale=2))
    created_at: Mapped[datetime] = mapped_column(server_default=text("now()"))