# =========================
# FILE: routers/articles.py
# =========================
from datetime import datetime
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

import models
from database import get_db

router = APIRouter(prefix="/articles", tags=["articles"])

# Canonical category order (must match your UI)
CANONICAL_ORDER = [
    "breaking",
    "trending",
    "top headlines",
    "General News",
    "World News",
    "Politics",
    "Technology",
    "Sports",
    "Health & Fitness",
    "Entertainment",
]

# Mapping for case-insensitive normalization
def normalize_category(raw: Optional[str]) -> str:
    c = (raw or "").strip()
    low = c.lower()

    if low in ("breaking", "breaking news", "breaking news (alt)"):
        return "breaking"
    if low in ("trending", "trending news"):
        return "trending"
    if low in ("top headlines", "topheadlines", "top-headlines", "top headline", "top"):
        return "top headlines"

    if low == "general news":
        return "General News"
    if low == "world news":
        return "World News"
    if low == "politics":
        return "Politics"
    if low in ("technology", "tech"):
        return "Technology"
    if low == "sports":
        return "Sports"
    if low in ("health & fitness", "health and fitness", "health", "fitness"):
        return "Health & Fitness"
    if low == "entertainment":
        return "Entertainment"

    # fallback: don’t break homepage buckets
    return "General News"


def to_iso(dt: Optional[datetime]) -> Optional[str]:
    if not dt:
        return None
    # Keep it simple: ISO string
    return dt.isoformat()


def serialize_highlighted(a: models.HighlightedArticle) -> Dict[str, Any]:
    # IMPORTANT: published_at fallback so frontend never loses items
    safe_pub = a.published_at or a.created_at

    return {
        "id": a.id,
        "headline_id": a.headline_id,
        "title": a.title,
        "summary": a.summary,
        "content": a.content,
        "url": a.url,
        "source": a.source,
        "image_url": a.image_url,
        "category": normalize_category(a.category),
        "meta_title": a.meta_title,
        "meta_description": a.meta_description,
        "published_at": to_iso(safe_pub),
        "created_at": to_iso(a.created_at),
        "source_table": "highlighted_articles",
    }


@router.get("/", response_model=None)
def list_articles(
    db: Session = Depends(get_db),
    category: Optional[str] = Query(default=None, description="Category filter (case-insensitive)"),
    limit: int = Query(default=200, ge=1, le=5000),
    offset: int = Query(default=0, ge=0),
):
    q = db.query(models.HighlightedArticle)

    if category:
        want = normalize_category(category)
        # case-insensitive match by normalizing in Python:
        # (fast enough for now; later you can store normalized_category in DB)
        items = (
            q.order_by(
                models.HighlightedArticle.published_at.desc().nullslast(),
                models.HighlightedArticle.created_at.desc(),
                models.HighlightedArticle.id.desc(),
            )
            .offset(offset)
            .limit(limit)
            .all()
        )
        filtered = [serialize_highlighted(a) for a in items if normalize_category(a.category) == want]
        return filtered

    items = (
        q.order_by(
            models.HighlightedArticle.published_at.desc().nullslast(),
            models.HighlightedArticle.created_at.desc(),
            models.HighlightedArticle.id.desc(),
        )
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [serialize_highlighted(a) for a in items]


@router.get("/categories/list")
def categories_list():
    return {"order": CANONICAL_ORDER}


@router.get("/{article_id}")
def get_article(article_id: int, db: Session = Depends(get_db)):
    a = db.query(models.HighlightedArticle).filter(models.HighlightedArticle.id == article_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Article not found")
    return serialize_highlighted(a)
