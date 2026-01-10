from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    slug = Column(String(255), unique=True)
    content = Column(Text)
    category = Column(String(100))
    image_url = Column(String(500))
    is_published = Column(Boolean, default=False)
    published_at = Column(DateTime, default=datetime.utcnow)
