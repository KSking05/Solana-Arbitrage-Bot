import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# Handle different database configurations
if not DATABASE_URL:
    # Use SQLite as fallback if no DATABASE_URL is provided
    DATABASE_URL = "sqlite:///./arbitrage_bot.db"
    print("Using SQLite database for development")
elif DATABASE_URL.startswith('postgres://'):
    # Fix PostgreSQL URL for SQLAlchemy (postgres:// -> postgresql://)
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

print(f"Using database: {DATABASE_URL.split('@')[0].split('://')[0]} (connection details hidden)")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
