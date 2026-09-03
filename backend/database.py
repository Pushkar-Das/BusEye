from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./buseye.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class DetectionEvent(Base):
    __tablename__ = "detection_events"

    id = Column(Integer, primary_key=True, index=True)
    bus_id = Column(String, index=True)
    event_type = Column(String, index=True)      # pothole, vehicle, pedestrian, incident, sign_missing, etc.
    severity = Column(String, default="medium")  # low, medium, high, critical
    latitude = Column(Float)
    longitude = Column(Float)
    confidence = Column(Float)
    description = Column(Text, default="")
    plate_number = Column(String, default="")    # for incidents
    timestamp = Column(DateTime, default=datetime.utcnow)
    image_path = Column(String, default="")


class BusPosition(Base):
    __tablename__ = "bus_positions"

    id = Column(Integer, primary_key=True, index=True)
    bus_id = Column(String, unique=True, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    speed = Column(Float, default=0)
    route = Column(String, default="")
    status = Column(String, default="active")
    last_updated = Column(DateTime, default=datetime.utcnow)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
