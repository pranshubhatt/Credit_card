from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

# Create SQLAlchemy engine with connection retry
def get_engine():
    try:
        # Try Docker container URL first
        engine = create_engine(DATABASE_URL.replace("localhost", "db"))
        engine.connect()
        return engine
    except:
        try:
            # Try localhost if Docker connection fails
            engine = create_engine(DATABASE_URL)
            engine.connect()
            return engine
        except Exception as e:
            print(f"Database connection error: {e}")
            # For development, use SQLite as fallback
            sqlite_url = "sqlite:///./fraud_detection.db"
            print(f"Falling back to SQLite: {sqlite_url}")
            return create_engine(sqlite_url)

engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(String, primary_key=True)
    timestamp = Column(DateTime)
    prediction = Column(String)
    probability = Column(Float)
    amount = Column(Float)
    v1 = Column(Float)
    v2 = Column(Float)
    v3 = Column(Float)
    v4 = Column(Float)
    v5 = Column(Float)
    v6 = Column(Float)
    v7 = Column(Float)
    v8 = Column(Float)
    v9 = Column(Float)
    v10 = Column(Float)
    v11 = Column(Float)
    v12 = Column(Float)
    v13 = Column(Float)
    v14 = Column(Float)
    v15 = Column(Float)
    v16 = Column(Float)
    v17 = Column(Float)
    v18 = Column(Float)
    v19 = Column(Float)
    v20 = Column(Float)
    v21 = Column(Float)
    v22 = Column(Float)
    v23 = Column(Float)
    v24 = Column(Float)
    v25 = Column(Float)
    v26 = Column(Float)
    v27 = Column(Float)
    v28 = Column(Float)
    # ... Add other V features as needed

# Create all tables
Base.metadata.create_all(bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 