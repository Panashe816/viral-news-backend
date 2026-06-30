from fastapi import APIRouter

router = APIRouter()

@router.get("/sitemap-articles.xml")
def sitemap_articles():
    return {
        "status": "working",
        "message": "Sitemap endpoint created successfully"
    }
