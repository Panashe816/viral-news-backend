import asyncio
from datetime import datetime

from fastapi import FastAPI
from database import engine, get_db
import models
from models import Article
from routers import articles

# Create DB tables (SAFE – does NOT delete data)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Viral News API",
    description="API for the Viral AI News Mobile App",
    version="1.0.0"
)

# Routers
app.include_router(articles.router)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Viral News API!",
        "endpoints": {
            "all_articles": "/articles/",
            "article_by_id": "/articles/{id}",
            "articles_by_category": "/articles/category/{category_name}",
            "categories_list": "/articles/categories/list"
        }
    }

# 🔁 BACKGROUND AUTO-PUBLISH LOOP
@app.on_event("startup")
async def start_publisher():
    asyncio.create_task(publish_loop())

async def publish_loop():
    while True:
        try:
            db = next(get_db())

            # ✅ FIX: use published_at instead of published boolean
            unpublished = db.query(Article).filter(
                Article.published_at.is_(None)
            ).all()

            for article in unpublished:
                article.published_at = datetime.utcnow()

            db.commit()
            print(f"[AUTO-PUBLISH] Published {len(unpublished)} articles")

        except Exception as e:
            print("[AUTO-PUBLISH ERROR]", e)

        # ⏱ wait 1 hour
        await asyncio.sleep(3600)
