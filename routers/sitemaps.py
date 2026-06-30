from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from xml.sax.saxutils import escape

import models
from database import get_db
from datetime import datetime, timedelta, timezone
router = APIRouter()

SITE_URL = "https://viralnewsalert.com"
PUBLICATION_NAME = "Viral News"
LANGUAGE = "en"
NEWS_LOOKBACK_HOURS = 48

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
@router.get("/news-sitemap.xml")
def news_sitemap(db: Session = Depends(get_db)):
    cutoff = datetime.utcnow() - timedelta(hours=NEWS_LOOKBACK_HOURS)

    articles = (
        db.query(models.HighlightedArticle)
        .filter(
            (
                models.HighlightedArticle.published_at >= cutoff
            ) |
            (
                (models.HighlightedArticle.published_at == None) &
                (models.HighlightedArticle.created_at >= cutoff)
            )
        )
        .order_by(
            models.HighlightedArticle.published_at.desc().nullslast(),
            models.HighlightedArticle.created_at.desc(),
            models.HighlightedArticle.id.desc(),
        )
        .all()
    )

    xml = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset',
        'xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
        'xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">',
    ]

    for article in articles:

        lastmod = article.published_at or article.created_at

        xml.append("<url>")

        xml.append(
            f"<loc>{SITE_URL}/articles.html?id={article.id}</loc>"
        )

        xml.append("<news:news>")

        xml.append("<news:publication>")

        xml.append(
            f"<news:name>{PUBLICATION_NAME}</news:name>"
        )

        xml.append(
            f"<news:language>{LANGUAGE}</news:language>"
        )

        xml.append("</news:publication>")

        xml.append(
            f"<news:publication_date>{lastmod.isoformat()}</news:publication_date>"
        )

        xml.append(
            f"<news:title>{escape(article.title)}</news:title>"
        )

        xml.append("</news:news>")

        xml.append("</url>")

    xml.append("</urlset>")

    return Response(
        content="\n".join(xml),
        media_type="application/xml",
    )
