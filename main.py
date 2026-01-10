# main.py
import os
from fastapi import FastAPI
from database import engine
import models
from routers import articles

# Create DB tables if they don't exist
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Viral News API",
    description="API for the Viral AI News Mobile App",
    version="1.0.0"
)

# Include routers
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
