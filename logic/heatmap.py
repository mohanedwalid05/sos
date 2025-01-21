from typing import List, Dict, Tuple, Optional
import numpy as np
from models.types import SupplyCategory, Location
from models.database import CrisisArea
from settings import settings

class HeatmapGenerator:
    def __init__(self):
        self.resolution_km = settings.HEATMAP_RESOLUTION_KM
        self.radius_km = settings.HEATMAP_RADIUS_KM
        self.min_grid_steps = settings.HEATMAP_MIN_GRID_STEPS
        self.gradient_colors = settings.HEATMAP_COLORS
        
    def _calculate_satisfaction_level(
        self, 
        crisis_area: CrisisArea, 
        category: Optional[SupplyCategory] = None
    ) -> float:
        """Calculate how well the needs are met (0 = not met at all, 1 = fully met)."""
        if category:
            needed = crisis_area.current_needs.get(category, 0)
            if needed == 0:
                return 1.0  # No needs = fully satisfied
                
            # Calculate available supplies including pending donations
            available = sum(
                supply.quantity 
                for supply in crisis_area.current_inventory.get(category, [])
            )
            
            return min(1.0, available / needed)
        else:
            # For overall satisfaction, take weighted average based on urgency
            total_urgency = sum(crisis_area.urgency_levels.values())
            if total_urgency == 0:
                return 1.0
                
            weighted_satisfaction = 0.0
            for cat in SupplyCategory:
                if cat in crisis_area.current_needs:
                    urgency = crisis_area.urgency_levels.get(cat, 1)
                    satisfaction = self._calculate_satisfaction_level(crisis_area, cat)
                    weighted_satisfaction += satisfaction * (urgency / total_urgency)
                    
            return weighted_satisfaction
    
    def _haversine_distance(self, loc1: Location, loc2: Location) -> float:
        """Calculate distance between two points in kilometers."""
        R = 6371  # Earth's radius in kilometers
        
        lat1, lon1 = np.radians(loc1.latitude), np.radians(loc1.longitude)
        lat2, lon2 = np.radians(loc2.latitude), np.radians(loc2.longitude)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
        
        return R * c
    
    def _calculate_intensity(
        self, 
        point: Location, 
        crisis_areas: List[CrisisArea],
        category: Optional[SupplyCategory] = None
    ) -> Tuple[float, float]:
        """Calculate intensity and satisfaction at a point based on nearby crisis areas."""
        max_intensity = 0.0
        weighted_satisfaction = 0.0
        total_weight = 0.0
        
        for area in crisis_areas:
            distance = self._haversine_distance(point, area.location)
            if distance > self.radius_km:
                continue
                
            # Calculate distance weight (1 at center, 0 at radius)
            weight = 1 - (distance / self.radius_km)
            weight = weight ** 2  # Square to make it fall off more quickly
            
            # Calculate satisfaction level (0 = needs not met, 1 = fully met)
            satisfaction = self._calculate_satisfaction_level(area, category)
            
            # Update weighted satisfaction
            weighted_satisfaction += satisfaction * weight
            total_weight += weight
            
            # Calculate intensity based on urgency and distance
            urgency = max(area.urgency_levels.values()) if area.urgency_levels else 1
            intensity = urgency * weight
            max_intensity = max(max_intensity, intensity)
        
        if total_weight == 0:
            return 0.0, 1.0
            
        avg_satisfaction = weighted_satisfaction / total_weight
        return max_intensity, avg_satisfaction
    
    def generate_heatmap_data(
        self, 
        crisis_areas: List[CrisisArea],
        bounds: Tuple[Location, Location],  # SW, NE corners
        category: Optional[SupplyCategory] = None
    ) -> Dict:
        """Generate heatmap data for the given geographic bounds."""
        sw, ne = bounds
        
        # Calculate grid dimensions
        lat_steps = int((ne.latitude - sw.latitude) / self.resolution_km * 111)  # 111km per degree
        lon_steps = int((ne.longitude - sw.longitude) / self.resolution_km * 111 * np.cos(np.radians(sw.latitude)))
        
        # Ensure minimum number of steps
        lat_steps = max(lat_steps, self.min_grid_steps)
        lon_steps = max(lon_steps, self.min_grid_steps)
        
        # Generate grid points
        lat_vals = np.linspace(sw.latitude, ne.latitude, lat_steps)
        lon_vals = np.linspace(sw.longitude, ne.longitude, lon_steps)
        
        points = []
        for lat in lat_vals:
            for lon in lon_vals:
                point = Location(latitude=lat, longitude=lon)
                intensity, satisfaction = self._calculate_intensity(point, crisis_areas, category)
                
                if intensity > 0:
                    points.append({
                        "lat": lat,
                        "lng": lon,
                        "intensity": intensity,
                        "satisfaction": satisfaction
                    })
        
        return {
            "points": points,
            "gradient": self.gradient_colors
        }
    
    def generate_crisis_markers(self, crisis_areas: List[CrisisArea]) -> List[Dict]:
        """Generate marker data for crisis areas."""
        markers = []
        for area in crisis_areas:
            # Calculate overall satisfaction level
            satisfaction = self._calculate_satisfaction_level(area)
            
            markers.append({
                "id": area.id,
                "name": area.name,
                "position": {
                    "lat": area.location.latitude,
                    "lng": area.location.longitude
                },
                "satisfaction": satisfaction,
                "urgency": max(area.urgency_levels.values()) if area.urgency_levels else 1,
                "reachability": area.reachability.value,
                "needs": area.current_needs,
                "population": area.population,
                "weather": area.weather_conditions,
                "security": area.security_level.value
            })
        
        return markers 