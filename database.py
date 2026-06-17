from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

DATABASE_URL = "sqlite:///./traffic_vision.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Violation(Base):
    __tablename__ = "violations"

    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    vehicle_type = Column(String)
    violation_type = Column(String, index=True)
    confidence = Column(Float)
    plate_number = Column(String, index=True)
    image_url = Column(String)
    annotated_image_url = Column(String)
    explanation = Column(String)

class Offender(Base):
    __tablename__ = "offenders"

    id = Column(Integer, primary_key=True, index=True)
    plate_number = Column(String, unique=True, index=True)
    offence_count = Column(Integer, default=0)
    last_offence_timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class SystemLog(Base):
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    processing_time_ms = Column(Float)
    success = Column(Boolean)
    error_message = Column(String, nullable=True)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
