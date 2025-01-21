from datetime import datetime, timedelta
import uuid

from db import SessionLocal
from models.database import NGO, CrisisArea, Donation, User
from models.types import SupplyCategory, ReachabilityLevel, SecurityLevel, DonationStatus

def seed_database():
    """Seed the database with initial data."""
    db = SessionLocal()
    try:
        # Clear existing data
        db.query(Donation).delete()
        db.query(NGO).delete()
        db.query(CrisisArea).delete()
        db.query(User).delete()

        # Create demo user
        demo_user = User(
            id=str(uuid.uuid4()),
            username="demo",
            hashed_password=User.get_password_hash("demo"),
            is_active=True,
            is_superuser=False
        )
        db.add(demo_user)

        # Create NGOs
        ngos = [
            NGO(
                id=str(uuid.uuid4()),
                name="Red International",
                is_busy=False,
                working_hours={
                    "start_time": "08:00",
                    "end_time": "20:00",
                    "days_of_week": [0, 1, 2, 3, 4, 5, 6]
                },
                latitude=34.0522,
                longitude=-118.2437,
                reach_radius_km=1000.0,
                inventory={
                    SupplyCategory.FOOD.value: [
                        {"quantity": 1000, "unit": "kg", "expiry_date": "2024-12-31"},
                        {"quantity": 500, "unit": "kg", "expiry_date": "2024-06-30"}
                    ],
                    SupplyCategory.WATER.value: [
                        {"quantity": 5000, "unit": "liters", "expiry_date": None}
                    ],
                    SupplyCategory.MEDICAL.value: [
                        {"quantity": 200, "unit": "boxes", "expiry_date": "2025-01-01"}
                    ]
                },
                replenishment_time_hours={
                    SupplyCategory.FOOD.value: 48,
                    SupplyCategory.WATER.value: 24,
                    SupplyCategory.MEDICAL.value: 72
                },
                credibility_score=0.95,
                rating=4.8,
                total_donations=150,
                response_time_hours=4.5,
                specializations=[
                    SupplyCategory.MEDICAL.value,
                    SupplyCategory.FOOD.value
                ]
            ),
            NGO(
                id=str(uuid.uuid4()),
                name="Doctors Without Borders",
                is_busy=True,
                working_hours={
                    "start_time": "00:00",
                    "end_time": "23:59",
                    "days_of_week": [0, 1, 2, 3, 4, 5, 6]
                },
                latitude=40.7128,
                longitude=-74.0060,
                reach_radius_km=800.0,
                inventory={
                    SupplyCategory.MEDICAL.value: [
                        {"quantity": 1000, "unit": "boxes", "expiry_date": "2024-12-31"},
                        {"quantity": 500, "unit": "boxes", "expiry_date": "2024-06-30"}
                    ],
                    SupplyCategory.HYGIENE.value: [
                        {"quantity": 2000, "unit": "kits", "expiry_date": None}
                    ]
                },
                replenishment_time_hours={
                    SupplyCategory.MEDICAL.value: 48,
                    SupplyCategory.HYGIENE.value: 72
                },
                credibility_score=0.98,
                rating=4.9,
                total_donations=200,
                response_time_hours=3.0,
                specializations=[SupplyCategory.MEDICAL.value]
            )
        ]

        # Create Crisis Areas
        crisis_areas = [
            CrisisArea(
                id=str(uuid.uuid4()),
                name="Port-au-Prince Earthquake Zone",
                latitude=18.5944,
                longitude=-72.3074,
                current_needs={
                    SupplyCategory.MEDICAL.value: 1000,
                    SupplyCategory.WATER.value: 5000,
                    SupplyCategory.FOOD.value: 2000,
                    SupplyCategory.SHELTER.value: 500
                },
                reachability=ReachabilityLevel.DIFFICULT,
                weather_conditions="Tropical Storm Warning",
                urgency_levels={
                    SupplyCategory.MEDICAL.value: 5,
                    SupplyCategory.WATER.value: 4,
                    SupplyCategory.FOOD.value: 4,
                    SupplyCategory.SHELTER.value: 3
                },
                population=50000,
                current_inventory={
                    SupplyCategory.MEDICAL.value: [
                        {"quantity": 100, "unit": "boxes", "expiry_date": "2024-03-01"}
                    ],
                    SupplyCategory.WATER.value: [
                        {"quantity": 1000, "unit": "liters", "expiry_date": None}
                    ]
                },
                road_conditions="Partially blocked",
                security_level=SecurityLevel.CAUTION,
                nearest_supply_routes=[
                    {"latitude": 18.5945, "longitude": -72.3080},
                    {"latitude": 18.5940, "longitude": -72.3070}
                ]
            ),
            CrisisArea(
                id=str(uuid.uuid4()),
                name="Syria Conflict Zone",
                latitude=36.2021,
                longitude=37.1343,
                current_needs={
                    SupplyCategory.MEDICAL.value: 2000,
                    SupplyCategory.FOOD.value: 3000,
                    SupplyCategory.SHELTER.value: 1000,
                    SupplyCategory.HYGIENE.value: 1500
                },
                reachability=ReachabilityLevel.EXTREME,
                weather_conditions="Clear",
                urgency_levels={
                    SupplyCategory.MEDICAL.value: 5,
                    SupplyCategory.FOOD.value: 5,
                    SupplyCategory.SHELTER.value: 4,
                    SupplyCategory.HYGIENE.value: 3
                },
                population=75000,
                current_inventory={
                    SupplyCategory.FOOD.value: [
                        {"quantity": 500, "unit": "kg", "expiry_date": "2024-02-15"}
                    ]
                },
                road_conditions="Dangerous",
                security_level=SecurityLevel.EXTREME,
                nearest_supply_routes=[
                    {"latitude": 36.2025, "longitude": 37.1340},
                    {"latitude": 36.2020, "longitude": 37.1345}
                ]
            )
        ]

        # Add to database
        db.add_all(ngos)
        db.add_all(crisis_areas)
        db.commit()

        # Create some donations
        donations = [
            Donation(
                id=str(uuid.uuid4()),
                ngo_id=ngos[0].id,
                crisis_area_id=crisis_areas[0].id,
                supplies=[
                    {
                        "category": SupplyCategory.MEDICAL.value,
                        "quantity": 100,
                        "unit": "boxes"
                    },
                    {
                        "category": SupplyCategory.WATER.value,
                        "quantity": 1000,
                        "unit": "liters"
                    }
                ],
                timestamp=datetime.utcnow(),
                status=DonationStatus.DELIVERED
            ),
            Donation(
                id=str(uuid.uuid4()),
                ngo_id=ngos[1].id,
                crisis_area_id=crisis_areas[1].id,
                supplies=[
                    {
                        "category": SupplyCategory.MEDICAL.value,
                        "quantity": 200,
                        "unit": "boxes"
                    },
                    {
                        "category": SupplyCategory.HYGIENE.value,
                        "quantity": 500,
                        "unit": "kits"
                    }
                ],
                timestamp=datetime.utcnow(),
                status=DonationStatus.IN_TRANSIT
            )
        ]

        db.add_all(donations)
        db.commit()

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database() 