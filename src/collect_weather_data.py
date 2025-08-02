#!/usr/bin/env python3

import requests
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

# Create a minimal Flask app instance just for SQLAlchemy to connect
app = Flask(__name__)

# Configure the database URI for Heroku deployment
# The os.path.dirname(base_dir) part ensures we look for the database file one level up
base_dir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(os.path.dirname(base_dir), 'Weather.sqlite3')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the Weather database model
class Weather(db.Model):
    __tablename__ = "weather_data"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    entry_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    temperature_celsius = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Weather(Time: {self.entry_time}, Temp: {self.temperature_celsius}°C)>"

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
    with app.app_context():
        # This will create the database file and table if they don't exist
        db.create_all()

        current_temperature = get_temperature()

        if current_temperature is not None:
            new_weather_entry = Weather(temperature_celsius=current_temperature)
            db.session.add(new_weather_entry)
            try:
                db.session.commit()
                print(f"Successfully added temperature {current_temperature}°C at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} to Weather.sqlite3")
            except Exception as e:
                db.session.rollback()
                print(f"Error saving data to database: {e}")
        else:
            print("Failed to get temperature, not saving to database.")