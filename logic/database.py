from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import enum
from typing import List
import os
from passlib.context import CryptContext

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/crisis_aid')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Enums
class SupplyCategoryEnum(str, enum.Enum):
    FOOD = "food"
    WATER = "water"
    MEDICAL = "medical"
    SHELTER = "shelter"
    CLOTHING = "clothing"
    HYGIENE = "hygiene"

class ReachabilityLevelEnum(str, enum.Enum):
    EASY = "easy"
    MODERATE = "moderate"
    DIFFICULT = "difficult"
    EXTREME = "extreme"

class SecurityLevelEnum(str, enum.Enum):
    SAFE = "safe"
    CAUTION = "caution"
    DANGEROUS = "dangerous"
    EXTREME = "extreme"

class DonationStatusEnum(str, enum.Enum):
    PENDING = "pending"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"

# Models
class NGO(Base):
    __tablename__ = "ngos"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    is_busy = Column(Boolean, default=False)
    working_hours = Column(JSON)  # Store as JSON: {start_time, end_time, days_of_week}
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    reach_radius_km = Column(Float, nullable=False)
    inventory = Column(JSON)  # Store as JSON: {category: [{quantity, unit, expiry_date}]}
    replenishment_time_hours = Column(JSON)  # Store as JSON: {category: hours}
    credibility_score = Column(Float, default=1.0)
    rating = Column(Float, default=5.0)
    total_donations = Column(Integer, default=0)
    response_time_hours = Column(Float, default=24.0)
    specializations = Column(JSON)  # Store as JSON array of categories

    # Relationships
    donations = relationship("Donation", back_populates="ngo")

class CrisisArea(Base):
    __tablename__ = "crisis_areas"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    current_needs = Column(JSON)  # Store as JSON: {category: amount}
    reachability = Column(Enum(ReachabilityLevelEnum), nullable=False)
    weather_conditions = Column(String)
    urgency_levels = Column(JSON)  # Store as JSON: {category: level}
    population = Column(Integer, nullable=False)
    current_inventory = Column(JSON)  # Store as JSON: {category: [{quantity, unit, expiry_date}]}
    road_conditions = Column(String)
    security_level = Column(Enum(SecurityLevelEnum), nullable=False)
    nearest_supply_routes = Column(JSON)  # Store as JSON array of coordinates

    # Relationships
    donations_received = relationship("Donation", back_populates="crisis_area")

class Donation(Base):
    __tablename__ = "donations"

    id = Column(String, primary_key=True)
    ngo_id = Column(String, ForeignKey("ngos.id"))
    crisis_area_id = Column(String, ForeignKey("crisis_areas.id"))
    supplies = Column(JSON)  # Store as JSON array of {category, quantity, unit}
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(DonationStatusEnum), default=DonationStatusEnum.PENDING)

    # Relationships
    ngo = relationship("NGO", back_populates="donations")
    crisis_area = relationship("CrisisArea", back_populates="donations_received")

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create all tables
def init_db():
    Base.metadata.create_all(bind=engine) 