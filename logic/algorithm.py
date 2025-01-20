from typing import List, Dict, Tuple
from datetime import datetime
import numpy as np
from models import NGO, CrisisArea, Supply, SupplyCategory, Donation
from settings import URGENCY_WEIGHT, DISTANCE_WEIGHT, REACHABILITY_WEIGHT
import uuid

class AidMatchingAlgorithm:
    def __init__(self):
        self.distance_cache = {}  # Cache for distance calculations
        
    def calculate_distance(self, ngo: NGO, crisis_area: CrisisArea) -> float:
        """Calculate the distance between an NGO and crisis area using Haversine formula."""
        cache_key = (ngo.id, crisis_area.id)
        if cache_key in self.distance_cache:
            return self.distance_cache[cache_key]
            
        lat1, lon1 = ngo.location.latitude, ngo.location.longitude
        lat2, lon2 = crisis_area.location.latitude, crisis_area.location.longitude
        
        R = 6371  # Earth's radius in kilometers
        
        dlat = np.radians(lat2 - lat1)
        dlon = np.radians(lon2 - lon1)
        a = (np.sin(dlat/2) * np.sin(dlat/2) +
             np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) *
             np.sin(dlon/2) * np.sin(dlon/2))
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
        distance = R * c
        
        self.distance_cache[cache_key] = distance
        return distance

    def calculate_supply_match_score(self, ngo: NGO, crisis_area: CrisisArea) -> Dict[SupplyCategory, float]:
        """Calculate how well an NGO's supplies match crisis area needs."""
        scores = {}
        for category, needed_amount in crisis_area.current_needs.items():
            if needed_amount == 0:
                scores[category] = 0
                continue
                
            ngo_supplies = ngo.inventory.get(category, [])
            available_amount = sum(supply.quantity for supply in ngo_supplies)
            
            # Calculate match score based on:
            # 1. How much of the need can be fulfilled (0-1)
            fulfillment_ratio = min(1.0, available_amount / needed_amount)
            
            # 2. Urgency of the need (1-5 normalized to 0-1)
            urgency = crisis_area.urgency_levels.get(category, 1) / 5
            
            # 3. NGO's specialization bonus
            specialization_bonus = 1.2 if category in ngo.specializations else 1.0
            
            scores[category] = fulfillment_ratio * urgency * specialization_bonus
            
        return scores

    def find_optimal_matches(self, ngos: List[NGO], crisis_areas: List[CrisisArea]) -> List[Tuple[NGO, CrisisArea, List[Supply]]]:
        """Find optimal matches between NGOs and crisis areas."""
        matches = []
        
        # Filter out busy NGOs
        available_ngos = [ngo for ngo in ngos if not ngo.is_busy]
        
        # Sort crisis areas by overall urgency
        crisis_areas = sorted(
            crisis_areas,
            key=lambda x: max(x.urgency_levels.values(), default=0),
            reverse=True
        )
        
        for crisis_area in crisis_areas:
            area_matches = []
            
            for ngo in available_ngos:
                # Skip if crisis area is beyond NGO's reach radius
                distance = self.calculate_distance(ngo, crisis_area)
                if distance > ngo.reach_radius_km:
                    continue
                    
                # Calculate match scores for each supply category
                supply_scores = self.calculate_supply_match_score(ngo, crisis_area)
                
                # Calculate overall match score
                distance_factor = 1 - (distance / ngo.reach_radius_km)
                reachability_factor = 1 - (crisis_area.reachability.value / 4)  # Normalized to 0-1
                
                overall_score = (
                    sum(supply_scores.values()) * URGENCY_WEIGHT +
                    distance_factor * DISTANCE_WEIGHT +
                    reachability_factor * REACHABILITY_WEIGHT
                ) * ngo.credibility_score  # Weight by NGO credibility
                
                if overall_score > 0:
                    area_matches.append((ngo, overall_score, supply_scores))
            
            # Sort matches by score and select the best one
            if area_matches:
                area_matches.sort(key=lambda x: x[1], reverse=True)
                best_match = area_matches[0]
                ngo, score, supply_scores = best_match
                
                # Determine optimal supplies to send
                supplies_to_send = []
                for category, score in supply_scores.items():
                    if score > 0:
                        needed = crisis_area.current_needs[category]
                        available = ngo.inventory.get(category, [])
                        
                        # Calculate optimal quantity considering urgency and other factors
                        optimal_quantity = min(
                            needed,
                            sum(s.quantity for s in available)
                        )
                        
                        if optimal_quantity > 0:
                            supplies_to_send.append(Supply(
                                category=category,
                                quantity=optimal_quantity,
                                unit="units"  # This should be made dynamic based on category
                            ))
                
                if supplies_to_send:
                    matches.append((ngo, crisis_area, supplies_to_send))
                    available_ngos.remove(ngo)  # Remove matched NGO from available pool
                    
        return matches

    def create_donation_records(self, matches: List[Tuple[NGO, CrisisArea, List[Supply]]]) -> List[Donation]:
        """Create donation records from matches."""
        donations = []
        for ngo, crisis_area, supplies in matches:
            donation = Donation(
                id=str(uuid.uuid4()),
                ngo_id=ngo.id,
                crisis_area_id=crisis_area.id,
                supplies=supplies,
                timestamp=datetime.now(),
                status="pending"
            )
            donations.append(donation)
        return donations
