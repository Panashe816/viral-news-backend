from sqlalchemy import Column, Integer, Text, DateTime, Boolean
from database import Base
from datetime import datetime


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, nullable=False)
    category = Column(Text, nullable=False)
    content = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    # ✅ USE THIS FOR PUBLISH STATUS (NULL = unpublished)
    published_at = Column(DateTime, nullable=True)


class Headline(Base):
    __tablename__ = "headlines"

    id = Column(Integer, primary_key=True, index=True)
    headline = Column(Text, nullable=False)
    category = Column(Text, nullable=False)
    source = Column(Text)
    url = Column(Text)
    published_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    generated = Column(Boolean, default=False)
