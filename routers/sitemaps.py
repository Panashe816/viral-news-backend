from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from xml.sax.saxutils import escape

import models
from database import get_db
from datetime import datetime, timedelta, timezone
router = APIRouter()

SITE_URL = "https://viralnewsalert.com"

@router.get("/sitemap-articles.xml")
def sitemap_articles(db: Session = Depends(get_db)):
    articles = (
        db.query(models.HighlightedArticle)
        .order_by(
            models.HighlightedArticle.published_at.desc().nullslast(),
            models.HighlightedArticle.created_at.desc(),
            models.HighlightedArticle.id.desc(),
        )
        .all()
    )

    xml = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]

    for article in articles:
        lastmod = article.published_at or article.created_at
        loc = f"{SITE_URL}/articles.html?id={article.id}"

        xml.append("<url>")
        xml.append(f"<loc>{escape(loc)}</loc>")
        if lastmod:
            xml.append(f"<lastmod>{lastmod.isoformat()}</lastmod>")
        xml.append("<changefreq>hourly</changefreq>")
        xml.append("<priority>0.8</priority>")
        xml.append("</url>")

    xml.append("</urlset>")

    return Response(
        content="\n".join(xml),
        media_type="application/xml",
    )
