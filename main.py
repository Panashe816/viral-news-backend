from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Article
from datetime import datetime

DATABASE_URL = "postgresql://universalnews_user:V5niNC00UBFDXwyOvFJhCLjiYHFXZi8b@dpg-d4a28v7diees73cr0bm0-a.virginia-postgres.render.com/universalnewss"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

app = FastAPI(title="Viral News API", version="1.0.0")

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


# -------------------------
# HOME PAGE
# -------------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    db = SessionLocal()
    articles = (
        db.query(Article)
        .filter(Article.is_published == True)
        .order_by(Article.published_at.desc())
        .limit(20)
        .all()
    )
    db.close()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "articles": articles}
    )


# -------------------------
# ARTICLE PAGE
# -------------------------
@app.get("/news/{slug}", response_class=HTMLResponse)
def article_page(slug: str, request: Request):
    db = SessionLocal()
    article = db.query(Article).filter(Article.slug == slug).first()
    db.close()

    if not article:
        return HTMLResponse("Article not found", status_code=404)

    return templates.TemplateResponse(
        "article.html",
        {"request": request, "article": article}
    )


# -------------------------
# CATEGORY PAGE
# -------------------------
@app.get("/category/{category}", response_class=HTMLResponse)
def category_page(category: str, request: Request):
    db = SessionLocal()
    articles = (
        db.query(Article)
        .filter(Article.category == category, Article.is_published == True)
        .order_by(Article.published_at.desc())
        .all()
    )
    db.close()

    return templates.TemplateResponse(
        "category.html",
        {"request": request, "articles": articles, "category": category}
    )
