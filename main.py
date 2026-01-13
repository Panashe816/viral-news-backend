import asyncio
from datetime import datetime

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import engine, get_db
import models
from models import Article, HighlightedArticle
from routers import articles

# Create DB tables safely (no data loss)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Viral News API",
    description="API backend for Viral News (JSON only)",
    version="1.0.0"
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

# 🔹 Include article API router
app.include_router(articles.router)

# 🔹 Root endpoint
@app.get("/")
def read_root():
    return {
        "message": "Viral News API is running",
        "endpoints": {
            "all_articles": "/articles/",
            "article_by_id": "/articles/{id}",
            "categories": "/articles/categories/list",
            "homepage": "/homepage"
        }
    }

# 🔹 HOMEPAGE DATA ENDPOINT (NO LIMITS — frontend controls display)
@app.get("/homepage")
def homepage(db: Session = Depends(get_db)):
    trending = (
        db.query(HighlightedArticle)
        .filter(HighlightedArticle.type == "trending")
        .order_by(HighlightedArticle.published_at.desc())
        .all()
    )

    breaking = (
        db.query(HighlightedArticle)
        .filter(HighlightedArticle.type == "breaking")
        .order_by(HighlightedArticle.published_at.desc())
        .all()
    )

    top_headlines = (
        db.query(HighlightedArticle)
        .filter(HighlightedArticle.type == "top")
        .order_by(HighlightedArticle.published_at.desc())
        .all()
    )

    latest = (
        db.query(Article)
        .filter(Article.published == True)
        .order_by(Article.published_at.desc())
        .limit(50)  # safe cap for performance
        .all()
    )

    return {
        "trending": trending,
        "breaking": breaking,
        "top_headlines": top_headlines,
        "latest": latest
    }

# 🔁 AUTO-PUBLISH LOOP
@app.on_event("startup")
async def start_publisher():
    asyncio.create_task(publish_loop())

async def publish_loop():
    while True:
        try:
            db = next(get_db())

            unpublished = db.query(Article).filter(
                Article.published == False
            ).all()

            for article in unpublished:
                article.published = True
                article.published_at = datetime.utcnow()

            db.commit()
            print(f"[AUTO-PUBLISH] Published {len(unpublished)} articles")

        except Exception as e:
            print("[AUTO-PUBLISH ERROR]", e)

        await asyncio.sleep(3600)
