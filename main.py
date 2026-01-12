import asyncio
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, get_db
import models
from models import Article
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
    "https://viralnewsalert.com",  # GitHub Pages frontend
    "http://localhost:5500",       # local testing
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔹 Include article API router (JSON endpoints)
app.include_router(articles.router)

# 🔹 Root endpoint (health check)
@app.get("/")
def read_root():
    return {
        "message": "Viral News API is running",
        "endpoints": {
            "all_articles": "/articles/",
            "article_by_id": "/articles/{id}",
            "categories": "/articles/categories/list"
        }
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

        # ⏱ run every 1 hour
        await asyncio.sleep(3600)
