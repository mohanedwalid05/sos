from fastapi import FastAPI, HTTPException, Depends, Security, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import jwt as PyJWT
from pydantic import BaseModel
import numpy as np
import os

from database import get_db, NGO, CrisisArea, Donation, SupplyCategoryEnum, User
from settings import JWT_EXPIRY_HOURS, HEATMAP_RADIUS_KM, HEATMAP_INTENSITY_SCALE
from algorithm import AidMatchingAlgorithm
from validation import validate_coordinates

app = FastAPI(
    title="Crisis Aid Coordination API",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Security
SECRET_KEY = os.getenv('SECRET_KEY', "your-secret-key-here")
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# CORS configuration
origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Initialize algorithm
algorithm = AidMatchingAlgorithm()

# Pydantic models
class Token(BaseModel):
    access_token: str
    token_type: str

class NGOUpdate(BaseModel):
    is_busy: Optional[bool]
    inventory_updates: Optional[Dict[str, List[Dict]]]

class CrisisAreaUpdate(BaseModel):
    needs_updates: Optional[Dict[str, int]]
    weather_conditions: Optional[str]
    security_level: Optional[str]

# Authentication
def create_token(data: dict) -> str:
    expiry = datetime.utcnow() + timedelta(hours=JWT_EXPIRY_HOURS)
    to_encode = data.copy()
    to_encode.update({"exp": expiry})
    return PyJWT.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = PyJWT.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except PyJWT.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except PyJWT.JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

# Helper functions
def calculate_intensity(point_lat: float, point_lng: float, crisis_areas: List[CrisisArea], category: Optional[str] = None) -> float:
    total_intensity = 0.0
    
    for area in crisis_areas:
        # Calculate distance using Haversine formula
        R = 6371  # Earth's radius in kilometers
        lat1, lon1 = np.radians(point_lat), np.radians(point_lng)
        lat2, lon2 = np.radians(area.latitude), np.radians(area.longitude)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
        distance = R * c
        
        if distance > HEATMAP_RADIUS_KM:
            continue
            
        # Calculate base intensity from distance
        distance_factor = 1 - (distance / HEATMAP_RADIUS_KM)
        
        # Calculate need intensity
        if category:
            need_intensity = area.current_needs.get(category, 0) / HEATMAP_INTENSITY_SCALE
            urgency = area.urgency_levels.get(category, 1) / 5
        else:
            need_intensity = sum(area.current_needs.values()) / HEATMAP_INTENSITY_SCALE
            urgency = max(area.urgency_levels.values()) / 5 if area.urgency_levels else 0.2
        
        # Combine factors
        intensity = (
            distance_factor * 
            need_intensity * 
            urgency * 
            (4 - area.reachability.value.count('_')) / 4  # Reachability factor
        )
        
        total_intensity += intensity
        
    return min(1.0, total_intensity)

# Routes
@app.post("/token")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    try:
        user = db.query(User).filter(User.username == form_data.username).first()
        if not user or not user.verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=401,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(status_code=401, detail="User is inactive")
        
        access_token = create_token({"sub": user.username})
        return Token(access_token=access_token, token_type="bearer")
    except Exception as e:
        print(f"Login error: {str(e)}")  # Debug logging
        raise

@app.get("/heatmap")
async def get_heatmap(
    sw_lat: float,
    sw_lng: float,
    ne_lat: float,
    ne_lng: float,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    """Get heatmap data for the specified bounds."""
    if not all(validate_coordinates(lat, lng) for lat, lng in [(sw_lat, sw_lng), (ne_lat, ne_lng)]):
        raise HTTPException(status_code=400, detail="Invalid coordinates")

    # Get crisis areas within the bounding box with some padding
    padding = HEATMAP_RADIUS_KM / 111  # Convert km to degrees (approximate)
    crisis_areas = db.query(CrisisArea).filter(
        CrisisArea.latitude >= sw_lat - padding,
        CrisisArea.latitude <= ne_lat + padding,
        CrisisArea.longitude >= sw_lng - padding,
        CrisisArea.longitude <= ne_lng + padding
    ).all()

    # Generate grid points
    lat_steps = int((ne_lat - sw_lat) * 111 / 1)  # 1km resolution
    lon_steps = int((ne_lng - sw_lng) * 111 * np.cos(np.radians(sw_lat)) / 1)
    
    lat_vals = np.linspace(sw_lat, ne_lat, max(lat_steps, 2))
    lon_vals = np.linspace(sw_lng, ne_lng, max(lon_steps, 2))
    
    points = []
    for lat in lat_vals:
        for lon in lon_vals:
            intensity = calculate_intensity(lat, lon, crisis_areas, category)
            if intensity > 0:
                points.append({
                    "lat": float(lat),
                    "lng": float(lon),
                    "intensity": float(intensity)
                })

    return {
        "points": points,
        "opacity": 0.6,
        "radius": HEATMAP_RADIUS_KM * 1000  # Convert to meters for frontend
    }

@app.get("/crisis-areas")
async def get_crisis_areas(
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
) -> List[Dict]:
    """Get all crisis areas."""
    crisis_areas = db.query(CrisisArea).all()
    return [{
        "id": area.id,
        "name": area.name,
        "position": {
            "lat": area.latitude,
            "lng": area.longitude
        },
        "urgency": max(area.urgency_levels.values()) if area.urgency_levels else 0,
        "reachability": area.reachability.value,
        "needs": area.current_needs,
        "population": area.population,
        "weather": area.weather_conditions,
        "security": area.security_level.value,
        "current_inventory": area.current_inventory
    } for area in crisis_areas]

@app.get("/ngos")
async def get_ngos(
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
) -> List[Dict]:
    """Get all NGOs."""
    ngos = db.query(NGO).all()
    return [{
        "id": ngo.id,
        "name": ngo.name,
        "is_busy": ngo.is_busy,
        "location": {
            "latitude": ngo.latitude,
            "longitude": ngo.longitude
        },
        "reach_radius_km": ngo.reach_radius_km,
        "inventory": ngo.inventory,
        "rating": ngo.rating,
        "credibility_score": ngo.credibility_score,
        "response_time_hours": ngo.response_time_hours,
        "specializations": ngo.specializations
    } for ngo in ngos]

@app.post("/match")
async def find_matches(
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
) -> List[Dict]:
    """Find optimal matches between NGOs and crisis areas."""
    ngos = db.query(NGO).filter(NGO.is_busy == False).all()
    crisis_areas = db.query(CrisisArea).all()
    
    matches = algorithm.find_optimal_matches(ngos, crisis_areas)
    donations = algorithm.create_donation_records(matches)
    
    # Save donations to database
    for donation in donations:
        db_donation = Donation(
            id=donation.id,
            ngo_id=donation.ngo_id,
            crisis_area_id=donation.crisis_area_id,
            supplies=donation.supplies,
            status=donation.status
        )
        db.add(db_donation)
    
    db.commit()
    
    return [
        {
            "ngo": ngo.name,
            "crisis_area": area.name,
            "supplies": [
                {
                    "category": s.category.value,
                    "quantity": s.quantity,
                    "unit": s.unit
                }
                for s in supplies
            ],
            "donation_id": donation.id
        }
        for (ngo, area, supplies), donation 
        in zip(matches, donations)
    ]

@app.patch("/ngos/{ngo_id}")
async def update_ngo(
    ngo_id: str,
    updates: NGOUpdate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    """Update NGO status and inventory."""
    ngo = db.query(NGO).filter(NGO.id == ngo_id).first()
    if not ngo:
        raise HTTPException(status_code=404, detail="NGO not found")
        
    if updates.is_busy is not None:
        ngo.is_busy = updates.is_busy
        
    if updates.inventory_updates:
        for category, supplies in updates.inventory_updates.items():
            if category in SupplyCategoryEnum.__members__:
                ngo.inventory[category] = supplies
                
    db.commit()
    return {"status": "success"}

@app.patch("/crisis-areas/{area_id}")
async def update_crisis_area(
    area_id: str,
    updates: CrisisAreaUpdate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    """Update crisis area needs and conditions."""
    area = db.query(CrisisArea).filter(CrisisArea.id == area_id).first()
    if not area:
        raise HTTPException(status_code=404, detail="Crisis area not found")
        
    if updates.needs_updates:
        for category, amount in updates.needs_updates.items():
            if category in SupplyCategoryEnum.__members__:
                area.current_needs[category] = amount
                
    if updates.weather_conditions:
        area.weather_conditions = updates.weather_conditions
        
    if updates.security_level:
        area.security_level = updates.security_level
        
    db.commit()
    return {"status": "success"} 