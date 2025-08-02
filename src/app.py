from flask import Flask, render_template_string
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

# Initialize Flask application
app = Flask(__name__)

# Database configuration
# Use DATABASE_URL from Heroku, fallback to a local SQLite for testing
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace("postgres://", "postgresql://", 1) or 'sqlite:///Weather.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database model for weather data
class Weather(db.Model):
    __tablename__ = "weather_data"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    entry_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    temperature_celsius = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Weather(Time: {self.entry_time}, Temp: {self.temperature_celsius}°C)>"

# --- Web Application Routes ---
@app.route("/")
def index():
    # Fetch data from the database
    latest_temp_entry = Weather.query.order_by(Weather.entry_time.desc()).first()
    latest_temp = latest_temp_entry.temperature_celsius if latest_temp_entry else "N/A"
    latest_time = latest_temp_entry.entry_time.strftime("%Y-%m-%d %H:%M:%S") if latest_temp_entry else "N/A"

    all_historical_temps = Weather.query.order_by(Weather.entry_time.desc()).limit(50).all()
    display_historical_temps = Weather.query.order_by(Weather.entry_time.desc()).limit(10).all()

    # Calculate average temperature
    average_temp = "N/A"
    if all_historical_temps:
        temperatures_list = [entry.temperature_celsius for entry in all_historical_temps]
        if temperatures_list:
            average_temp = round(sum(temperatures_list) / len(temperatures_list), 2)

    # HTML content with placeholders for data
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Simple Weather Dashboard</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f4; color: #333; }}
            .container {{ max-width: 800px; margin: auto; background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            h1 {{ color: #0056b3; text-align: center; margin-bottom: 30px; }}
            h2 {{ color: #0056b3; border-bottom: 1px solid #eee; padding-bottom: 5px; margin-top: 25px; }}
            .current-temp-section {{ text-align: center; margin-bottom: 25px; }}
            .current-temp {{ font-size: 3em; color: #dc3545; font-weight: bold; }}
            .timestamp {{ font-size: 0.9em; color: #6c757d; display: block; margin-top: 5px; }}
            .analysis {{ font-size: 1.2em; color: #28a745; margin-top: 15px; text-align: center; border: 1px solid #e9ecef; padding: 10px; border-radius: 5px; background-color: #eafbea; }}
            ul {{ list-style-type: none; padding: 0; }}
            li {{ margin-bottom: 8px; padding: 10px; border: 1px solid #e9ecef; background-color: #f8f9fa; border-radius: 4px; display: flex; justify-content: space-between; align-items: center; }}
            li span.temp {{ font-weight: bold; color: #007bff; }}
            .health-link {{ margin-top: 25px; display: block; text-align: center; color: #007bff; text-decoration: none; }}
            .health-link:hover {{ text-decoration: underline; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Simple Weather Dashboard</h1>
            <div class="current-temp-section">
                <h2>Current Temperature:</h2>
                <p class="current-temp">{latest_temp}°C</p>
                <p class="timestamp">As of: {latest_time} (UTC)</p>
            </div>
            <div class="analysis">
                <h2>Analysis:</h2>
                <p>Average of last {len(all_historical_temps) if all_historical_temps else 0} recorded temperatures: {average_temp}°C</p>
            </div>
            <div>
                <h2>Recent Readings:</h2>
                <ul>
                    {''.join([f'<li><span>{entry.entry_time.strftime("%Y-%m-%d %H:%M:%S")}</span><span class="temp">{entry.temperature_celsius}°C</span></li>' for entry in display_historical_temps]) if display_historical_temps else '<li>No historical data available. Run the data collection script!</li>'}
                </ul>
            </div>
            <a href="/health" class="health-link">Check Application Health</a>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_content)

@app.route("/health")
def health_check():
    try:
        with db.engine.connect() as connection:
            connection.execute(db.text("SELECT 1"))
        return "OK", 200
    except Exception as e:
        return f"Error: {e}", 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)