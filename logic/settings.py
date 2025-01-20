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
HEATMAP_RADIUS_KM = 50          # Radius to consider for heatmap intensity
HEATMAP_INTENSITY_SCALE = 1000  # Scale factor for heatmap intensity values
HEATMAP_OPACITY = 0.6           # Default opacity for heatmap overlay

# Performance optimization
BATCH_SIZE = 100                # Number of records to process in one batch
WORKER_THREADS = 4              # Number of worker threads for parallel processing

# Security settings
JWT_EXPIRY_HOURS = 24          # How long JWT tokens are valid
PASSWORD_MIN_LENGTH = 12       # Minimum password length
REQUIRED_PASSWORD_STRENGTH = 3  # Required password strength (1-4)
