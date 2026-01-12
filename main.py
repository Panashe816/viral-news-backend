import asyncio
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from database import engine, get_db
import models
from models import Article
from routers import articles

# Create DB tables safely
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Viral News API",
    description="API for the Viral News platform",
    version="1.0.0"
)

# 🔹 CORS
origins = [
    "https://viralnewsalert.com",
    "http://localhost:5500"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Routers
app.include_router(articles.router)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Viral News API",
        "endpoints": {
            "articles": "/articles/",
            "article": "/articles/{id}"
        }
    }

# 📰 FULL ARTICLE PAGE (OPTION A)
@app.get("/articles/{article_id}", response_class=HTMLResponse)
def read_article(article_id: int):
    db = next(get_db())

    article = db.query(Article).filter(
        Article.id == article_id,
        Article.published == True
    ).first()

    if not article or not article.title:
        raise HTTPException(status_code=404, detail="Article not found")

    image_html = ""
    if article.image_url:
        image_html = f'<img src="{article.image_url}" />'

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>{article.title}</title>
        <meta name="description" content="{article.title}">
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 900px;
                margin: auto;
                padding: 20px;
                line-height: 1.7;
            }}
            img {{
                max-width: 100%;
                border-radius: 8px;
                margin: 15px 0;
            }}
            h1 {{
                font-size: 28px;
            }}
        </style>
    </head>
    <body>

        <h1>{article.title}</h1>
        {image_html}
        {article.content}

    </body>
    </html>
    """

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
