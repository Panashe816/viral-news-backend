from sqlalchemy import Column, Integer, Text, DateTime, Boolean
from database import Base
from datetime import datetime

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, nullable=False)
    category = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    image_url = Column(Text, nullable=True)
    country = Column(Text, nullable=True)
    source_url = Column(Text, nullable=True)
    fetched_at = Column(DateTime, nullable=True)
    used = Column(Boolean, default=False)
    is_trending = Column(Boolean, default=False)
    is_latest = Column(Boolean, default=False)
    is_breaking = Column(Boolean, default=False)
    is_top_headline = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    # ✅ REQUIRED FOR AUTO-PUBLISH
    published = Column(Boolean, default=False)
    published_at = Column(DateTime, nullable=True)


class Headline(Base):
    __tablename__ = "headlines"

    id = Column(Integer, primary_key=True, index=True)
    headline = Column(Text, nullable=False)
    category = Column(Text, nullable=False)
    source = Column(Text, nullable=True)
    url = Column(Text, nullable=True)
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    generated = Column(Boolean, default=False)
