from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime, time
from enum import Enum
import uuid

class SupplyCategory(Enum):
    FOOD = "food"
    WATER = "water"
    MEDICAL = "medical"
    SHELTER = "shelter"
    CLOTHING = "clothing"
    HYGIENE = "hygiene"

class ReachabilityLevel(Enum):
    EASY = "easy"
    MODERATE = "moderate" 
    DIFFICULT = "difficult"
    EXTREME = "extreme"

@dataclass
class Location:
    latitude: float
    longitude: float
    
@dataclass
class WorkingHours:
    start_time: time
    end_time: time
    days_of_week: List[int]  # 0 = Monday, 6 = Sunday

@dataclass
class Supply:
    category: SupplyCategory
    quantity: int
    unit: str
    expiry_date: Optional[datetime] = None

@dataclass
class Donation:
    id: str
    ngo_id: str
    crisis_area_id: str
    supplies: List[Supply]
    timestamp: datetime
    status: str  # pending, in_transit, delivered

@dataclass
class NGO:
    id: str
    name: str
    is_busy: bool
    working_hours: WorkingHours
    location: Location
    reach_radius_km: float  # Maximum distance they can travel
    inventory: Dict[SupplyCategory, List[Supply]]
    replenishment_time_hours: Dict[SupplyCategory, float]
    credibility_score: float  # 0 to 1
    rating: float  # 0 to 5
    last_donation: Optional[Donation]
    total_donations: int
    response_time_hours: float  # Average response time
    specializations: List[SupplyCategory]  # What they're best at providing

@dataclass
class CrisisArea:
    id: str
    name: str
    location: Location
    current_needs: Dict[SupplyCategory, int]  # Category -> Amount needed
    reachability: ReachabilityLevel
    weather_conditions: str
    urgency_levels: Dict[SupplyCategory, int]  # 1-5, 5 being most urgent
    population: int
    current_inventory: Dict[SupplyCategory, List[Supply]]
    last_donation_received: Optional[Donation]
    donation_history: List[Donation]
    road_conditions: str
    security_level: str  # Indicates safety for aid workers
    nearest_supply_routes: List[Location] 