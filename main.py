# =========================
# FILE: main.py
# =========================
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import engine, get_db
import models
from routers import articles

# Create DB tables safely (won’t drop data)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Viral News API",
    description="API backend for Viral News (JSON only)",
    version="2.1.0"
)

# ✅ Add your site + GitHub Pages origin (important if you host index.html on GitHub Pages)
origins = [
    "https://viralnewsalert.com",
    "https://www.viralnewsalert.com",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    # If you use GitHub Pages, add it here (safe even if unused):
    "https://panasheganyani.github.io",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Router (now guaranteed to read from highlighted_articles)
app.include_router(articles.router)

# Canonical category order
CATEGORY_ORDER = [
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

def normalize_category(raw: str) -> str:
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

    return "General News"


def serialize(a: models.HighlightedArticle):
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
        "published_at": safe_pub.isoformat() if safe_pub else None,
        "created_at": a.created_at.isoformat() if a.created_at else None,
        "source_table": "highlighted_articles",
    }


@app.get("/")
def read_root():
    return {
        "message": "Viral News API is running",
        "endpoints": {
            "homepage": "/homepage",
            "articles": "/articles/",
            "article_by_id": "/articles/{id}",
            "categories": "/articles/categories/list"
        },
        "note": "Current architecture uses highlighted_articles as the ONLY feed source."
    }


# =========================================================
# HOMEPAGE DATA ENDPOINT (THE ONE YOUR FRONTEND SHOULD USE)
# - Uses ONLY highlighted_articles
# - Returns grouped categories + flat list
# - Everything is JSON-safe (dicts)
# =========================================================
@app.get("/homepage")
def homepage(db: Session = Depends(get_db)):
    items = (
        db.query(models.HighlightedArticle)
        .order_by(
            models.HighlightedArticle.published_at.desc().nullslast(),
            models.HighlightedArticle.created_at.desc(),
            models.HighlightedArticle.id.desc(),
        )
        .all()
    )

    # Prepare dicts first
    serialized = [serialize(a) for a in items]

    # Group by normalized category
    grouped = {k: [] for k in CATEGORY_ORDER}
    for a in serialized:
        cat = a["category"]
        if cat in grouped:
            grouped[cat].append(a)
        else:
            grouped.setdefault("General News", []).append(a)

    return {
        "order": CATEGORY_ORDER,
        "categories": grouped,
        "all": serialized
    }
