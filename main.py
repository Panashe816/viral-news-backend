# =========================
# FILE: main.py
# =========================
import time
from fastapi import FastAPI, Depends, Response
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

# ✅ Add your site + GitHub Pages origin
origins = [
    "https://viralnewsalert.com",
    "https://www.viralnewsalert.com",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "https://panasheganyani.github.io",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Router
app.include_router(articles.router)

# =========================================================
# HEALTH ENDPOINTS (for UptimeRobot + Render health checks)
# =========================================================
@app.get("/health")
def health():
    return {"ok": True}

@app.get("/healthz")
def healthz():
    return {"ok": True}

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


# =========================================================
# SERIALIZERS
# - serialize_home: for homepage (FAST, NO huge content)
# =========================================================
def serialize_home(a: models.HighlightedArticle):
    safe_pub = a.published_at or a.created_at
    return {
        "id": a.id,
        "headline_id": a.headline_id,
        "title": a.title,
        "summary": a.summary,
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
            "health": "/health",
            "homepage": "/homepage",
            "articles": "/articles/",
            "article_by_id": "/articles/{id}",
            "categories": "/articles/categories/list"
        },
        "note": "Current architecture uses highlighted_articles as the ONLY feed source."
    }


# =========================================================
# HOMEPAGE ENDPOINT (FAST + CACHED)
# - Limits results (no .all() huge)
# - Removes article 'content' from payload
# - In-memory TTL cache to speed up repeated calls
# =========================================================
_HOMEPAGE_CACHE = {"ts": 0.0, "data": None}
_HOMEPAGE_TTL_SECONDS = 20  # 10–60 seconds is fine

@app.get("/homepage")
def homepage(response: Response, db: Session = Depends(get_db)):
    # ✅ allow short caching (browser/proxy); helps repeat loads
    response.headers["Cache-Control"] = "public, max-age=20, stale-while-revalidate=120"

    # ✅ in-memory cache (huge speed win)
    now = time.time()
    cached = _HOMEPAGE_CACHE["data"]
    if cached is not None and (now - _HOMEPAGE_CACHE["ts"] < _HOMEPAGE_TTL_SECONDS):
        return cached

    # ✅ limit query (avoid downloading your entire table)
    LIMIT = 500  # you can lower to 300 if you want lighter

    items = (
        db.query(models.HighlightedArticle)
        .order_by(
            models.HighlightedArticle.published_at.desc().nullslast(),
            models.HighlightedArticle.created_at.desc(),
            models.HighlightedArticle.id.desc(),
        )
        .limit(LIMIT)
        .all()
    )

    serialized = [serialize_home(a) for a in items]

    grouped = {k: [] for k in CATEGORY_ORDER}
    for a in serialized:
        cat = a["category"]
        if cat in grouped:
            grouped[cat].append(a)
        else:
            grouped["General News"].append(a)

    data = {
        "order": CATEGORY_ORDER,
        "categories": grouped,
        "all": serialized,
        "limit": LIMIT,
        "cached_ttl": _HOMEPAGE_TTL_SECONDS,
    }

    _HOMEPAGE_CACHE["ts"] = now
    _HOMEPAGE_CACHE["data"] = data
    return data
