from typing import List, Dict, Tuple
import numpy as np
from .models import CrisisArea, SupplyCategory, Location
from .settings import HEATMAP_RADIUS_KM, HEATMAP_INTENSITY_SCALE, HEATMAP_OPACITY

class HeatmapGenerator:
    def __init__(self, resolution_km: float = 1.0):
        self.resolution_km = resolution_km
        
    def _calculate_intensity(self, point: Location, crisis_areas: List[CrisisArea], category: SupplyCategory = None) -> float:
        """Calculate intensity at a point based on nearby crisis areas."""
        total_intensity = 0.0
        
        for area in crisis_areas:
            distance = self._haversine_distance(point, area.location)
            if distance > HEATMAP_RADIUS_KM:
                continue
                
            # Calculate base intensity from distance
            distance_factor = 1 - (distance / HEATMAP_RADIUS_KM)
            
            # Calculate need intensity
            if category:
                need_intensity = area.current_needs.get(category, 0) / HEATMAP_INTENSITY_SCALE
                urgency = area.urgency_levels.get(category, 1) / 5
            else:
                # Overall intensity across all categories
                need_intensity = sum(area.current_needs.values()) / HEATMAP_INTENSITY_SCALE
                urgency = max(area.urgency_levels.values(), default=1) / 5
            
            # Combine factors
            intensity = (
                distance_factor * 
                need_intensity * 
                urgency * 
                (4 - area.reachability.value) / 4  # Reachability factor
            )
            
            total_intensity += intensity
            
        return min(1.0, total_intensity)  # Normalize to [0,1]
    
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
    
    def generate_heatmap_data(
        self, 
        crisis_areas: List[CrisisArea],
        bounds: Tuple[Location, Location],  # SW, NE corners
        category: SupplyCategory = None
    ) -> Dict:
        """Generate heatmap data for the given geographic bounds."""
        sw, ne = bounds
        
        # Calculate grid dimensions
        lat_steps = int((ne.latitude - sw.latitude) / self.resolution_km * 111)  # 111km per degree
        lon_steps = int((ne.longitude - sw.longitude) / self.resolution_km * 111 * np.cos(np.radians(sw.latitude)))
        
        # Generate grid points
        lat_vals = np.linspace(sw.latitude, ne.latitude, lat_steps)
        lon_vals = np.linspace(sw.longitude, ne.longitude, lon_steps)
        
        points = []
        for lat in lat_vals:
            for lon in lon_vals:
                point = Location(latitude=lat, longitude=lon)
                intensity = self._calculate_intensity(point, crisis_areas, category)
                
                if intensity > 0:
                    points.append({
                        "lat": lat,
                        "lng": lon,
                        "intensity": intensity
                    })
        
        return {
            "points": points,
            "opacity": HEATMAP_OPACITY,
            "radius": HEATMAP_RADIUS_KM * 1000,  # Convert to meters for frontend
            "category": category.value if category else None
        }
    
    def generate_crisis_markers(self, crisis_areas: List[CrisisArea]) -> List[Dict]:
        """Generate marker data for crisis areas."""
        markers = []
        for area in crisis_areas:
            # Calculate overall urgency
            avg_urgency = sum(area.urgency_levels.values()) / len(area.urgency_levels) if area.urgency_levels else 0
            
            markers.append({
                "id": area.id,
                "name": area.name,
                "position": {
                    "lat": area.location.latitude,
                    "lng": area.location.longitude
                },
                "urgency": avg_urgency,
                "reachability": area.reachability.value,
                "needs": {
                    category.value: amount 
                    for category, amount in area.current_needs.items()
                },
                "population": area.population,
                "weather": area.weather_conditions,
                "security": area.security_level
            })
        
        return markers 