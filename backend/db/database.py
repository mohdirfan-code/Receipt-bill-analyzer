# backend/db/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from backend.db.models import Base # Ensure this import path is correct

# SQLite database URL. It will create 'receipts.db' inside the 'backend/db' folder.
DATABASE_URL = "sqlite:///backend/db/receipts.db"

# Create the SQLAlchemy engine
# connect_args={"check_same_thread": False} is crucial for SQLite with FastAPI/Flask to prevent concurrency issues.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create a SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """
    Initializes the database by creating all tables defined in Base.
    This function should be called once when the application starts.
    """
    print("Initializing database...")
    Base.metadata.create_all(bind=engine)
    print("Database initialized.")

def get_db():
    """
    Dependency for FastAPI to get a database session.
    It will close the session after the request is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()