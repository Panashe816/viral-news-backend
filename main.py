# =========================
# FILE: main.py
# =========================
import asyncio
from datetime import datetime, timezone

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import engine, get_db
import models
from routers import articles

# Create DB tables safely (no data loss)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Viral News API",
    description="API backend for Viral News (JSON only)",
    version="2.0.0"
)

# 🔹 CORS configuration
origins = [
    "https://viralnewsalert.com",
    "http://localhost:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔹 Include your existing article API router
app.include_router(articles.router)

# 🔹 Root endpoint
@app.get("/")
def read_root():
    return {
        "message": "Viral News API is running",
        "endpoints": {
            "homepage": "/homepage",
            "highlighted_articles": "/articles/",
            "article_by_id": "/articles/{id}",
            "categories": "/articles/categories/list"
        },
        "note": "Current architecture uses highlighted_articles as the ONLY feed source for homepage."
    }

# =========================================================
# HOMEPAGE DATA ENDPOINT
# - Uses ONLY highlighted_articles (generated content)
# - Returns all categories with NO limits (frontend controls)
# - Also returns a flat list 'all' sorted newest->oldest
# =========================================================
@app.get("/homepage")
def homepage(db: Session = Depends(get_db)):
    # Category order must match scraper2/generator2
    order = [
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

    # Fetch all highlighted articles once (fast + consistent)
    all_items = (
        db.query(models.HighlightedArticle)
        .order_by(
            models.HighlightedArticle.published_at.desc().nullslast(),
            models.HighlightedArticle.created_at.desc()
        )
        .all()
    )

    # Group by category
    grouped = {k: [] for k in order}
    for a in all_items:
        cat = (a.category or "").strip()
        if cat in grouped:
            grouped[cat].append(a)
        else:
            grouped.setdefault("Other", []).append(a)

    return {
        "order": order,
        "categories": grouped,
        "all": all_items
    }

# =========================================================
# AUTO-PUBLISH LOOP
# Old system published from "articles" table.
# Current architecture uses highlighted_articles directly,
# so auto-publish is no longer needed.
# We keep a lightweight loop so deployment expectations
# don't break, but it does nothing.
# =========================================================
@app.on_event("startup")
async def start_publisher():
    asyncio.create_task(publish_loop())

async def publish_loop():
    while True:
        try:
            # No-op: highlighted_articles are already treated as "published"
            pass
        except Exception as e:
            print("[AUTO-PUBLISH ERROR]", e)

        await asyncio.sleep(3600)
