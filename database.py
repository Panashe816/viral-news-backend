# =========================
# FILE: database.py
# =========================
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

# Tip: echo=True is noisy in production. Keep it False unless debugging.
ECHO_SQL = os.getenv("ECHO_SQL", "false").lower() in ("1", "true", "yes")

engine = create_engine(
    DATABASE_URL,
    echo=ECHO_SQL,
    future=True,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
