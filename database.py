import os
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Use environment variables for security
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ⭐⭐⭐ ADD THIS FUNCTION ⭐⭐⭐
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()