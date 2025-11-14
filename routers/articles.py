# routers/articles.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import models
from pydantic import BaseModel
from datetime import datetime

# Create Pydantic models for API responses
class ArticleBase(BaseModel):
    title: str
    category: str
    content: str
    created_at: datetime

class ArticleCreate(ArticleBase):
    pass

class Article(ArticleBase):
    id: int

    class Config:
        from_attributes = True  # Updated from 'orm_mode = True' for Pydantic v2

# Create router for all /articles endpoints
router = APIRouter(
    prefix="/articles",
    tags=["articles"]
)

# Get all articles with pagination
@router.get("/", response_model=List[Article])
def get_articles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    articles = db.query(models.Article).order_by(models.Article.created_at.desc()).offset(skip).limit(limit).all()
    return articles

# Get a single article by ID
@router.get("/{article_id}", response_model=Article)
def get_article(article_id: int, db: Session = Depends(get_db)):
    db_article = db.query(models.Article).filter(models.Article.id == article_id).first()
    if db_article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return db_article

# Get articles by category
@router.get("/category/{category_name}", response_model=List[Article])
def get_articles_by_category(category_name: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    articles = db.query(models.Article).filter(models.Article.category == category_name).order_by(models.Article.created_at.desc()).offset(skip).limit(limit).all()
    return articles

# Get all unique categories
@router.get("/categories/list")
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(models.Article.category).distinct().all()
    # Extract category names from the result
    category_list = [cat[0] for cat in categories if cat[0] is not None]
    return {"categories": category_list}