from enum import Enum
from typing import List, Dict, Optional
from datetime import datetime, time
from pydantic import BaseModel

class SupplyCategory(str, Enum):
    FOOD = "food"
    WATER = "water"
    MEDICAL = "medical"
    SHELTER = "shelter"
    CLOTHING = "clothing"
    HYGIENE = "hygiene"

class ReachabilityLevel(str, Enum):
    EASY = "easy"
    MODERATE = "moderate"
    DIFFICULT = "difficult"
    EXTREME = "extreme"

class SecurityLevel(str, Enum):
    SAFE = "safe"
    CAUTION = "caution"
    DANGEROUS = "dangerous"
    EXTREME = "extreme"

class DonationStatus(str, Enum):
    PENDING = "pending"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"

class Location(BaseModel):
    latitude: float
    longitude: float

class Supply(BaseModel):
    category: SupplyCategory
    quantity: int
    unit: str
    expiry_date: Optional[datetime] = None

class WorkingHours(BaseModel):
    start_time: time
    end_time: time
    days_of_week: List[int]  # 0 = Monday, 6 = Sunday

class NGOBase(BaseModel):
    id: str
    name: str
    is_busy: bool
    working_hours: WorkingHours
    location: Location
    reach_radius_km: float
    inventory: Dict[SupplyCategory, List[Supply]]
    replenishment_time_hours: Dict[SupplyCategory, float]
    credibility_score: float
    rating: float
    total_donations: int
    response_time_hours: float
    specializations: List[SupplyCategory]

class CrisisAreaBase(BaseModel):
    id: str
    name: str
    location: Location
    current_needs: Dict[SupplyCategory, int]
    reachability: ReachabilityLevel
    weather_conditions: str
    urgency_levels: Dict[SupplyCategory, int]  # 1-5, 5 being most urgent
    population: int
    current_inventory: Dict[SupplyCategory, List[Supply]]
    road_conditions: str
    security_level: SecurityLevel
    nearest_supply_routes: List[Location]

class DonationBase(BaseModel):
    id: str
    ngo_id: str
    crisis_area_id: str
    supplies: List[Supply]
    timestamp: datetime
    status: DonationStatus