from sqlalchemy import Column, Integer, Text, DateTime, Boolean
from database import Base
from datetime import datetime


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, nullable=False)
    category = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    image_url = Column(Text)
    country = Column(Text)
    meta_data = Column(Text)  # renamed from `metadata` to avoid reserved word
    source_url = Column(Text)
    fetched_at = Column(DateTime)
    used = Column(Boolean)
    is_trending = Column(Boolean)
    is_latest = Column(Boolean)
    is_breaking = Column(Boolean)
    is_top_headline = Column(Boolean)

    created_at = Column(DateTime, default=datetime.utcnow)

    # ✅ REQUIRED FOR AUTO-PUBLISH
    published = Column(Boolean, default=False)
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
