from typing import Dict
from dataclasses import dataclass, field

def get_default_heatmap_colors() -> Dict[float, str]:
    return {
        0.0: "rgb(255, 0, 0)",      # Red (0% satisfied)
        0.2: "rgb(255, 69, 0)",     # Red-Orange
        0.4: "rgb(255, 165, 0)",    # Orange
        0.6: "rgb(255, 255, 0)",    # Yellow
        0.8: "rgb(144, 238, 144)",  # Light Green
        1.0: "rgb(0, 255, 0)"       # Green (100% satisfied)
    }

@dataclass
class Settings:
    # Heatmap settings
    HEATMAP_RADIUS_KM: float = 2.0  # Radius of influence for each crisis area
    HEATMAP_RESOLUTION_KM: float = 0.5  # Grid resolution for heatmap
    HEATMAP_MIN_GRID_STEPS: int = 10  # Minimum number of grid steps
    HEATMAP_GRADIENT_STEPS: int = 10  # Number of color steps in gradient
    
    # Color settings for heatmap (RGB values)
    HEATMAP_COLORS: Dict[float, str] = field(default_factory=get_default_heatmap_colors)
    
    # Authentication settings
    JWT_SECRET_KEY: str = "your-secret-key-here"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_HOURS: int = 24
    
    # Database settings
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/crisis_aid"
    
    # API settings
    CORS_ORIGINS: str = "http://localhost:3000"
    
    # Algorithm settings
    MATCHING_WEIGHT_DISTANCE: float = 0.3
    MATCHING_WEIGHT_INVENTORY: float = 0.3
    MATCHING_WEIGHT_SPECIALIZATION: float = 0.2
    MATCHING_WEIGHT_RESPONSE_TIME: float = 0.2
    
    def __post_init__(self):
        # Load environment variables if present
        import os
        self.JWT_SECRET_KEY = os.getenv('SECRET_KEY', self.JWT_SECRET_KEY)
        self.DATABASE_URL = os.getenv('DATABASE_URL', self.DATABASE_URL)
        self.CORS_ORIGINS = os.getenv('CORS_ORIGINS', self.CORS_ORIGINS)

# Create a global settings instance
settings = Settings()

# Matching algorithm weights
URGENCY_WEIGHT = 0.5      # Weight given to urgency of needs
DISTANCE_WEIGHT = 0.3     # Weight given to distance between NGO and crisis area
REACHABILITY_WEIGHT = 0.2 # Weight given to how accessible the crisis area is

# System settings
MAX_CACHE_SIZE = 10000    # Maximum number of distance calculations to cache
CACHE_EXPIRY_HOURS = 24   # How long to keep distance calculations in cache

# API rate limits (requests per minute)
WEATHER_API_RATE_LIMIT = 60
MAP_API_RATE_LIMIT = 100

# Heatmap settings
HEATMAP_INTENSITY_SCALE = 1000  # Scale factor for heatmap intensity values
HEATMAP_OPACITY = 0.6           # Default opacity for heatmap overlay

# Performance optimization
BATCH_SIZE = 100                # Number of records to process in one batch
WORKER_THREADS = 4              # Number of worker threads for parallel processing

# Security settings
PASSWORD_MIN_LENGTH = 12       # Minimum password length
REQUIRED_PASSWORD_STRENGTH = 3  # Required password strength (1-4)
