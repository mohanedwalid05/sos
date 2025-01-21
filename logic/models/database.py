from sqlalchemy import Column, String, Boolean, Float, Integer, JSON, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid
from passlib.context import CryptContext

from .types import SupplyCategory, ReachabilityLevel, SecurityLevel, DonationStatus

Base = declarative_base()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class NGO(Base):
    __tablename__ = "ngos"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    is_busy = Column(Boolean, default=False)
    working_hours = Column(JSON, nullable=False)  # WorkingHours as JSON
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    reach_radius_km = Column(Float, nullable=False)
    inventory = Column(JSON, nullable=False)  # Dict[SupplyCategory, List[Supply]]
    replenishment_time_hours = Column(JSON, nullable=False)  # Dict[SupplyCategory, float]
    credibility_score = Column(Float, default=1.0)
    rating = Column(Float, default=5.0)
    total_donations = Column(Integer, default=0)
    response_time_hours = Column(Float, default=24.0)
    specializations = Column(JSON, nullable=False)  # List[SupplyCategory]

    # Relationships
    donations = relationship("Donation", back_populates="ngo")

class CrisisArea(Base):
    __tablename__ = "crisis_areas"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    current_needs = Column(JSON, nullable=False)  # Dict[SupplyCategory, int]
    reachability = Column(Enum(ReachabilityLevel), nullable=False)
    weather_conditions = Column(String, nullable=False)
    urgency_levels = Column(JSON, nullable=False)  # Dict[SupplyCategory, int]
    population = Column(Integer, nullable=False)
    current_inventory = Column(JSON, nullable=False)  # Dict[SupplyCategory, List[Supply]]
    road_conditions = Column(String, nullable=False)
    security_level = Column(Enum(SecurityLevel), nullable=False)
    nearest_supply_routes = Column(JSON, nullable=False)  # List[Location]

    # Relationships
    donations_received = relationship("Donation", back_populates="crisis_area")

class Donation(Base):
    __tablename__ = "donations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    ngo_id = Column(String, ForeignKey("ngos.id"), nullable=False)
    crisis_area_id = Column(String, ForeignKey("crisis_areas.id"), nullable=False)
    supplies = Column(JSON, nullable=False)  # List[Supply]
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(DonationStatus), default=DonationStatus.PENDING)

    # Relationships
    ngo = relationship("NGO", back_populates="donations")
    crisis_area = relationship("CrisisArea", back_populates="donations_received")

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
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