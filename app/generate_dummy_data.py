from faker import Faker
from sqlalchemy.orm import Session
import sys
import os
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# print(sys.path)

from database import Sessionlocal  # Adjust the import path based on your project structure
from models import City, Airport, Flight, TravelPackage  # Adjust the import path
import random

fake = Faker()


cities_countries = {
    "Hyderabad":"India",
    "Mumbai": "India",
    "Delhi": "India",
    "Bangalore": "India",
    "New York": "USA",
    "Los Angeles": "USA",
    "Chicago": "USA",
    "London": "UK",
    "Manchester": "UK",
    "Liverpool": "UK",
    "Paris": "France",
    "Lyon": "France",
    "Marseille": "France",
    "Hong Kong": "China",
    "Beijing": "China",
    "Shanghai": "China",
    "Tokyo": "Japan",
    "Osaka": "Japan",
    "Kyoto": "Japan"
}

def generate_cities(db: Session, count: int = 50):
    for _ in range(count):
        # Randomly select a city-country pair from the predefined dictionary
        city_name, country_name = random.choice(list(cities_countries.items()))
        
        # Generate a city object with the selected names and a random timezone
        city = City(
            name=city_name,
            country=country_name,
            timezone=fake.timezone()
        )
        db.add(city)
    
    db.commit()

def generate_airports(db: Session, count: int = 50):
    cities = db.query(City).all()
    for _ in range(count):
        airport = Airport(
            city_id=random.choice(cities).id,
            name=f"{fake.city()} International Airport",
            iata_code=fake.bothify(text='???')  # Generates a 3-letter code
        )
        db.add(airport)
    db.commit()

def generate_flights(db: Session, count: int = 180):
    airports = db.query(Airport).all()
    for _ in range(count):
        flight = Flight(
            departure_airport_id=random.choice(airports).id,
            arrival_airport_id=random.choice(airports).id,
            flight_duration=fake.random_int(min=1, max=18),  # Duration in hours
            operating_airlines=fake.company()
        )
        db.add(flight)
    db.commit()

def generate_travel_package_name(db: Session):
    # Fetch all city names from the database
    cities = db.query(City.name).all()
    city_names = [city.name for city in cities]  # Extract city names from the query results
    
    if not city_names:
        return "No destinations available"  # Fallback in case no cities are found

    themes = ['Luxury', 'Budget-Friendly', 'Family', 'Romantic', 'Adventure', 'Cultural Discovery']
    experiences = ['Getaway', 'Escape', 'Adventure', 'Journey', 'Expedition', 'Tour']
    
    destination = random.choice(city_names)  # Choose a random destination from the database
    theme = random.choice(themes)
    experience = random.choice(experiences)

    package_name = f"{theme} {experience} to {destination}"
    return package_name

def generate_travel_package_description():
    highlights = [
        'breathtaking cityscapes', 'serene beaches', 'historic monuments', 'world-renowned museums', 
        'vibrant nightlife', 'culinary delights', 'scenic nature trails', 'luxurious accommodations'
    ]
    activities = [
        'guided tours', 'sunset cruises', 'wine tastings', 'safari adventures', 
        'mountain trekking', 'cultural workshops', 'shopping excursions', 'spa retreats'
    ]
    
    highlight1, highlight2 = random.sample(highlights, 2)
    activity1, activity2 = random.sample(activities, 2)

    base_description = (
        f"Experience {highlight1} and {highlight2}. "
        f"Enjoy {activity1} and {activity2}. "
    )
    
    final_description = "Each package offers a unique blend of attractions and experiences, ensuring memorable moments."
    
    
    # Concatenate base description with the final part, ensuring it doesn't exceed 255 characters
    if len(base_description) + len(final_description) <= 300:
        description = base_description + final_description
    else:
        # If the total length exceeds 255, use as much of the base description as possible
        remaining_length = 300 - len(final_description) - 3  # 3 dots for ellipsis
        description = base_description[:remaining_length] + '... ' + final_description
    
    # Ensure the final string is not beyond 255 characters in any case
    return description[:300]

def generate_travel_packages(db: Session, count: int = 40):
    cities = db.query(City).all()
    if not cities:
        print("Please generate cities first.")
        return
    for _ in range(count):
        travel_package = TravelPackage(
            name=generate_travel_package_name(db),
            description=generate_travel_package_description(),
            cost=fake.random_number(digits=3),
            origin_city_id=random.choice(cities).id,
            destination_city_id=random.choice(cities).id,
            valid_from=fake.date_time_this_decade(before_now=True, after_now=False),
            valid_to=fake.date_time_this_decade(before_now=False, after_now=True)
        )
        db.add(travel_package)
    db.commit()

def main():
    db = Sessionlocal()
    generate_cities(db)
    generate_airports(db)
    generate_flights(db)
    generate_travel_packages(db)
    db.close()

if __name__ == "__main__":
    main()
