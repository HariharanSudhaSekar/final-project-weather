#!/usr/bin/env python3

import requests
import os
from datetime import datetime

# Import the app, db, and Weather model from the main application file
# This ensures we use the same database configuration (PostgreSQL)
from src.app import app, db, Weather

# Function to fetch temperature from Open-Meteo API for Chennai
def get_temperature():
    # Coordinates for Chennai (Latitude: 13.0827, Longitude: 80.2707)
    API_URL = "https://api.open-meteo.com/v1/forecast?latitude=13.0827&longitude=80.2707&current_weather=true"

    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        current_temperature = data['current_weather']['temperature']
        return current_temperature
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Open-Meteo API: {e}")
        return None

# Main execution block
if __name__ == "__main__":
    # All database operations must run within the Flask application context
    with app.app_context():
        current_temperature = get_temperature()

        if current_temperature is not None:
            new_weather_entry = Weather(temperature_celsius=current_temperature)
            db.session.add(new_weather_entry)
            try:
                db.session.commit()
                print(f"Successfully added temperature {current_temperature}°C at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} to PostgreSQL database.")
            except Exception as e:
                db.session.rollback()
                print(f"Error saving data to database: {e}")
        else:
            print("Failed to get temperature, not saving to database.")