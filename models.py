from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Column

from db import Base


class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer,primary_key=True)
    caption = Column(Text)
    url=Column(String)
    created_at=Column(DateTime,default=datetime.utcnow)