import requests
import os
import json
import sqlite3
import logging
from datetime import datetime

# Logging
logging.basicConfig(level=logging.INFO)

# Config
API_KEY = os.getenv("OPENWEATHER_API_KEY")
CITY = "Charlotte"

URL = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"

def extract():
    logging.info("Extracting weather data...")
    
    response = requests.get(URL)
    
    if response.status_code != 200:
        raise Exception(f"API failed: {response.status_code}")
    
    data = response.json()

    with open("raw_weather.json", "w") as f:
        json.dump(data, f, indent=4)

    return data

def transform(data):
    logging.info("Transforming weather data...")

    transformed = {
        "city": data["name"],
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "weather": data["weather"][0]["description"],
        "timestamp": datetime.utcfromtimestamp(data["dt"]).isoformat()
    }

    return transformed

def load(data):
    logging.info("Loading data into SQLite...")

    conn = sqlite3.connect("weather.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS weather (
        city TEXT,
        temperature REAL,
        humidity INTEGER,
        weather TEXT,
        timestamp TEXT
    )
    """)

    cursor.execute("""
    INSERT INTO weather VALUES (?, ?, ?, ?, ?)
    """, (
        data["city"],
        data["temperature"],
        data["humidity"],
        data["weather"],
        data["timestamp"]
    ))

    conn.commit()
    conn.close()

def run_pipeline():
    raw_data = extract()
    transformed_data = transform(raw_data)
    load(transformed_data)

    logging.info("Pipeline completed successfully!")

if __name__ == "__main__":
    run_pipeline()
