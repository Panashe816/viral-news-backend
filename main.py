# =========================
# FILE: main.py
# =========================

import time
from fastapi import FastAPI, Depends, Response, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from sqlalchemy.orm import Session

from database import engine, get_db
import models
from routers import articles

# =========================
# DB INIT (safe)
# =========================
models.Base.metadata.create_all(bind=engine)

# =========================
# APP INIT
# =========================
app = FastAPI(
    title="Viral News API",
    description="API backend for Viral News (JSON only)",
    version="2.4.0",
)

# GZip compression (big win)
app.add_middleware(GZipMiddleware, minimum_size=800)

# =========================
# CORS
# =========================
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

# =========================
# ROUTERS
# =========================
app.include_router(articles.router)

# =========================
# HEALTH CHECKS (GET + HEAD)
# =========================
@app.get("/health")
@app.head("/health")
def health(response: Response):
    response.status_code = 200
    return {"ok": True}

@app.get("/healthz")
@app.head("/healthz")
def healthz(response: Response):
    response.status_code = 200
    return {"ok": True}

# =========================
# ROOT
# =========================
@app.get("/")
def read_root():
    return {
        "message": "Viral News API is running",
        "endpoints": {
            "homepage": "/homepage",
            "articles": "/articles/",
            "article_by_id": "/articles/{id}",
            "health": "/health",
        },
    }

# =========================
# CATEGORY NORMALIZATION
# =========================
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
    c = (raw or "").strip().lower()
    if c in ("breaking", "breaking news", "breaking news (alt)"):
        return "breaking"
    if c in ("trending", "trending news"):
        return "trending"
    if c in ("top headlines", "topheadlines", "top-headlines", "top"):
        return "top headlines"
    if c == "general news":
        return "General News"
    if c == "world news":
        return "World News"
    if c == "politics":
        return "Politics"
    if c in ("technology", "tech"):
        return "Technology"
    if c == "sports":
        return "Sports"
    if c in ("health", "fitness", "health & fitness", "health and fitness"):
        return "Health & Fitness"
    if c == "entertainment":
        return "Entertainment"
    return "General News"

# =========================
# FAST HOMEPAGE SERIALIZER
# (NO content field)
# =========================
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
        "published_at": safe_pub.isoformat() if safe_pub else None,
        "created_at": a.created_at.isoformat() if a.created_at else None,
    }

# =========================
# 🔥 SIMPLE IN-MEMORY CACHE
# =========================
HOMEPAGE_CACHE = {
    "data": None,
    "timestamp": 0.0,
    "buckets": {},  # ✅ cache per (limit, offset)
}

CACHE_TTL_SECONDS = 30  # ✅ safe (30–60s recommended)

# =========================
# HOMEPAGE ENDPOINT (CACHED)
# =========================
@app.get("/homepage")
def homepage(
    response: Response,
    db: Session = Depends(get_db),
    limit: int = Query(default=30, ge=5, le=80),
    offset: int = Query(default=0, ge=0),
):
    now = time.time()
    cache_key = f"{limit}:{offset}"

    # Serve cached response if fresh (per limit/offset)
    bucket = HOMEPAGE_CACHE["buckets"].get(cache_key)
    if bucket and (now - bucket["timestamp"] < CACHE_TTL_SECONDS):
        response.headers["Cache-Control"] = "public, max-age=30"
        return bucket["data"]

    items = (
        db.query(models.HighlightedArticle)
        .order_by(
            models.HighlightedArticle.published_at.desc().nullslast(),
            models.HighlightedArticle.created_at.desc(),
            models.HighlightedArticle.id.desc(),
        )
        .offset(offset)
        .limit(limit)
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

    payload = {
        "order": CATEGORY_ORDER,
        "categories": grouped,
        "count": len(serialized),
        "limit": limit,
        "offset": offset,
    }

    # Save to cache
    HOMEPAGE_CACHE["buckets"][cache_key] = {"data": payload, "timestamp": now}
    HOMEPAGE_CACHE["data"] = payload
    HOMEPAGE_CACHE["timestamp"] = now

    response.headers["Cache-Control"] = "public, max-age=30"
    return payload
