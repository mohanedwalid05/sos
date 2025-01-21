from typing import Dict, List, Optional
from datetime import datetime, time
import re
from pydantic import BaseModel, validator, constr
from models.types import SupplyCategory, ReachabilityLevel

class ValidationError(Exception):
    pass

class SecurityError(Exception):
    pass

# Input validation models
class LocationValidation(BaseModel):
    latitude: float
    longitude: float
    
    @validator('latitude')
    def validate_latitude(cls, v):
        if not -90 <= v <= 90:
            raise ValueError("Latitude must be between -90 and 90")
        return v
    
    @validator('longitude')
    def validate_longitude(cls, v):
        if not -180 <= v <= 180:
            raise ValueError("Longitude must be between -180 and 180")
        return v

class SupplyValidation(BaseModel):
    category: SupplyCategory
    quantity: int
    unit: str
    expiry_date: Optional[datetime]
    
    @validator('quantity')
    def validate_quantity(cls, v):
        if v < 0:
            raise ValueError("Quantity cannot be negative")
        return v
    
    @validator('unit')
    def validate_unit(cls, v):
        valid_units = {"kg", "liters", "pieces", "boxes", "packets"}
        if v.lower() not in valid_units:
            raise ValueError(f"Unit must be one of: {valid_units}")
        return v.lower()

class NGOValidation(BaseModel):
    name: constr(min_length=2, max_length=100)
    reach_radius_km: float
    credibility_score: float
    rating: float
    response_time_hours: float
    
    @validator('reach_radius_km')
    def validate_reach_radius(cls, v):
        if v <= 0:
            raise ValueError("Reach radius must be positive")
        return v
    
    @validator('credibility_score')
    def validate_credibility(cls, v):
        if not 0 <= v <= 1:
            raise ValueError("Credibility score must be between 0 and 1")
        return v
    
    @validator('rating')
    def validate_rating(cls, v):
        if not 0 <= v <= 5:
            raise ValueError("Rating must be between 0 and 5")
        return v
    
    @validator('response_time_hours')
    def validate_response_time(cls, v):
        if v < 0:
            raise ValueError("Response time cannot be negative")
        return v

class CrisisAreaValidation(BaseModel):
    name: constr(min_length=2, max_length=100)
    reachability: ReachabilityLevel
    population: int
    security_level: str
    
    @validator('population')
    def validate_population(cls, v):
        if v < 0:
            raise ValueError("Population cannot be negative")
        return v
    
    @validator('security_level')
    def validate_security(cls, v):
        valid_levels = {"safe", "caution", "dangerous", "extreme"}
        if v.lower() not in valid_levels:
            raise ValueError(f"Security level must be one of: {valid_levels}")
        return v.lower()

# Security validation functions
def validate_password_strength(password: str) -> bool:
    """
    Validate password strength:
    - At least 12 characters
    - Contains uppercase and lowercase
    - Contains numbers
    - Contains special characters
    """
    if len(password) < 12:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True

def sanitize_input(text: str) -> str:
    """Remove potentially dangerous characters from input."""
    # Remove HTML tags
    text = re.sub(r'<[^>]*>', '', text)
    # Remove special characters
    text = re.sub(r'[^\w\s-]', '', text)
    return text.strip()

def validate_coordinates(lat: float, lng: float) -> bool:
    """Validate latitude and longitude coordinates."""
    return -90 <= lat <= 90 and -180 <= lng <= 180

def validate_ngo_data(data: Dict) -> Dict:
    """Validate NGO data and return cleaned version."""
    try:
        validated = NGOValidation(**data)
        return validated.dict()
    except Exception as e:
        raise ValidationError(f"Invalid NGO data: {str(e)}")

def validate_crisis_area_data(data: Dict) -> Dict:
    """Validate crisis area data and return cleaned version."""
    try:
        validated = CrisisAreaValidation(**data)
        return validated.dict()
    except Exception as e:
        raise ValidationError(f"Invalid crisis area data: {str(e)}")

def validate_supply_data(data: Dict) -> Dict:
    """Validate supply data and return cleaned version."""
    try:
        validated = SupplyValidation(**data)
        return validated.dict()
    except Exception as e:
        raise ValidationError(f"Invalid supply data: {str(e)}")

# Rate limiting
class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}
    
    def is_allowed(self, client_id: str) -> bool:
        now = datetime.now().timestamp()
        
        # Clean old requests
        self.requests = {
            client: times for client, times in self.requests.items()
            if times[-1] > now - self.window_seconds
        }
        
        if client_id not in self.requests:
            self.requests[client_id] = []
        
        # Remove old requests for this client
        self.requests[client_id] = [
            t for t in self.requests[client_id]
            if t > now - self.window_seconds
        ]
        
        # Check if allowed
        if len(self.requests[client_id]) >= self.max_requests:
            return False
        
        # Add new request
        self.requests[client_id].append(now)
        return True 