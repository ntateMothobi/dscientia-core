import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# --- Absolute Path for Database ---
# Build a path to the project root directory
# This makes the database path independent of the current working directory
PROJECT_ROOT = Path(__file__).parent.parent.parent
DB_NAME = "prosi_mini.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{PROJECT_ROOT.joinpath(DB_NAME)}"

print(f"Database URL: {SQLALCHEMY_DATABASE_URL}") # For debugging

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
