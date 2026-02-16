# =========================
# FILE: models.py
# =========================
from datetime import datetime
from sqlalchemy import Column, Integer, Text, DateTime, Boolean, Index
from database import Base

# =======================
# MAIN ARTICLES TABLE (legacy)
# =======================
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

    published = Column(Boolean, default=False)
    published_at = Column(DateTime, nullable=True)


# =======================
# RAW HEADLINES TABLE
# =======================
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


# =======================
# HIGHLIGHTED ARTICLES (NEW FEED SOURCE)
# =======================
class HighlightedArticle(Base):
    __tablename__ = "highlighted_articles"

    id = Column(Integer, primary_key=True, index=True)
    headline_id = Column(Integer, nullable=False, index=True)

    title = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    content = Column(Text, nullable=False)

    url = Column(Text, nullable=True)
    source = Column(Text, nullable=True)
    image_url = Column(Text, nullable=True)

    category = Column(Text, nullable=False, index=True)

    meta_title = Column(Text, nullable=True)
    meta_description = Column(Text, nullable=True)

    published_at = Column(DateTime, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


# ✅ Composite index for your common ordering pattern
Index(
    "idx_highlighted_pub_created_id",
    HighlightedArticle.published_at,
    HighlightedArticle.created_at,
    HighlightedArticle.id,
)
