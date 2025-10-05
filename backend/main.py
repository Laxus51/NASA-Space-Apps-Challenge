import os
import csv
import math
import requests
from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routers import prediction_router

# Load environment variables
load_dotenv()

app = FastAPI(title="Air Quality API", description="Get nearest air quality data using OpenAQ API")

# Add CORS middleware to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(prediction_router.router)

# OpenAQ API configuration
OPENAQ_BASE_URL = "https://api.openaq.org/v3"
OPENAQ_API_KEY = os.getenv("OPENAQ_API_KEY")  # Optional, but recommended for higher rate limits
OPEN_METEO_BASE_URL = "https://api.open-meteo.com/v1"

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees) using the Haversine formula.
    Returns distance in kilometers.
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    
    return c * r

def search_stations_by_radius(lat: float, lon: float, radius_meters: int) -> Optional[list]:
    """
    Search for air quality stations within a given radius from coordinates.
    Returns list of stations or None if request fails.
    """
    url = f"{OPENAQ_BASE_URL}/locations"
    params = {
        "coordinates": f"{lat},{lon}",
        "radius": radius_meters,
        "limit": 100  # Get more stations to find the closest one
    }
    
    headers = {}
    if OPENAQ_API_KEY:
        headers["X-API-Key"] = OPENAQ_API_KEY
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("results", [])
    except requests.RequestException as e:
        print(f"Error searching stations: {e}")
        return None

def get_sensor_parameter(sensor_id: int) -> Optional[str]:
    """
    Get parameter name for a specific sensor.
    Returns parameter name or None if request fails.
    """
    url = f"{OPENAQ_BASE_URL}/sensors/{sensor_id}"
    headers = {}
    if OPENAQ_API_KEY:
        headers["X-API-Key"] = OPENAQ_API_KEY
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])
        if results:
            parameter = results[0].get("parameter", {})
            return parameter.get("name")
    except requests.RequestException as e:
        print(f"Error getting sensor parameter: {e}")
    return None

def get_latest_measurements(location_id: int) -> Optional[dict]:
    """
    Get latest measurements for a specific location.
    Returns measurement data or None if request fails.
    """
    url = f"{OPENAQ_BASE_URL}/locations/{location_id}/latest"
    params = {}
    
    headers = {}
    if OPENAQ_API_KEY:
        headers["X-API-Key"] = OPENAQ_API_KEY
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("results", [])
    except requests.RequestException as e:
        print(f"Error getting measurements: {e}")
        return None

def get_weather_data(lat: float, lon: float) -> Optional[dict]:
    """
    Get current weather data from Open-Meteo API.
    Returns weather data including temperature, humidity, and wind speed or None if request fails.
    """
    url = f"{OPEN_METEO_BASE_URL}/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        current_data = data.get("current", {})
        return {
            "temperature_celsius": current_data.get("temperature_2m"),
            "relative_humidity": current_data.get("relative_humidity_2m"),
            "wind_speed": current_data.get("wind_speed_10m"),
            "weather_time": current_data.get("time")
        }
    except requests.RequestException as e:
        print(f"Error getting weather data: {e}")
        return None

def save_airquality_csv(data: dict, lat: float, lon: float) -> None:
    """
    Save air quality and weather data to a CSV file.
    Creates data directory if it doesn't exist.
    """
    try:
        # Create data directory if it doesn't exist
        data_dir = "data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        # Round coordinates to 2 decimal places for clean filenames
        lat_rounded = round(lat, 2)
        lon_rounded = round(lon, 2)
        
        # Create filename
        filename = f"airquality_{lat_rounded}_{lon_rounded}.csv"
        filepath = os.path.join(data_dir, filename)
        
        # Prepare CSV data with the required mapping
        csv_data = {
            "date": data.get("weather_time"),
            "pm25": data.get("pm25"),
            "t2m": data.get("temperature_celsius"),
            "wind_speed": data.get("wind_speed"),
            "relative_humidity": data.get("relative_humidity")
        }
        
        # Write to CSV file
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ["date", "pm25", "t2m", "wind_speed", "relative_humidity"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write header
            writer.writeheader()
            # Write data row
            writer.writerow(csv_data)
            
        print(f"CSV file saved: {filepath}")
        
    except Exception as e:
        print(f"Error saving CSV file: {e}")

@app.get("/air-quality")
async def get_air_quality(
    lat: float = Query(..., description="Latitude coordinate"),
    lon: float = Query(..., description="Longitude coordinate")
):
    """
    Get nearest air quality data for given coordinates
    and current temperature data from Open-Meteo API.
    Searches progressively with increasing radius: 1km → 5km → 10km → 25km
    """
    # Progressive radius search in meters
    search_radii = [1000, 5000, 10000, 25000]
    
    nearest_station = None
    min_distance = float('inf')
    
    # Search with progressive radius
    for radius in search_radii:
        stations = search_stations_by_radius(lat, lon, radius)
        
        if stations is None:
            raise HTTPException(status_code=500, detail="Failed to fetch station data from OpenAQ API")
        
        if stations:
            # Find the nearest station among all found stations
            for station in stations:
                station_lat = station.get("coordinates", {}).get("latitude")
                station_lon = station.get("coordinates", {}).get("longitude")
                
                if station_lat is not None and station_lon is not None:
                    distance = haversine_distance(lat, lon, station_lat, station_lon)
                    
                    if distance < min_distance:
                        min_distance = distance
                        nearest_station = station
            
            # If we found a station, break out of the radius loop
            if nearest_station:
                break
    
    # If no station found within 25km, still try to get weather data
    if not nearest_station:
        weather_data = get_weather_data(lat, lon)
        response = {"message": "No air quality station found within 25 km"}
        
        if weather_data:
            response["temperature_celsius"] = weather_data["temperature_celsius"]
            response["relative_humidity"] = weather_data["relative_humidity"]
            response["wind_speed"] = weather_data["wind_speed"]
            response["weather_time"] = weather_data["weather_time"]
        else:
            response["temperature_celsius"] = None
            response["relative_humidity"] = None
            response["wind_speed"] = None
            response["weather_time"] = None
            response["warning"] = "Weather data also unavailable"
        
        # Save data to CSV file (even when no air quality station found)
        save_airquality_csv(response, lat, lon)
        
        return response
    
    # Get latest measurements for the nearest station
    location_id = nearest_station.get("id")
    if not location_id:
        raise HTTPException(status_code=500, detail="Station ID not found")
    
    measurements = get_latest_measurements(location_id)
    if measurements is None:
        raise HTTPException(status_code=500, detail="Failed to fetch measurement data from OpenAQ API")
    
    # Extract PM2.5 values from sensors data
    pm25_value = None
    last_updated = None
    
    # Cache for sensor parameters to avoid repeated API calls
    sensor_params_cache = {}
    
    for measurement in measurements:
        sensor_id = measurement.get("sensorsId")
        value = measurement.get("value")
        datetime_info = measurement.get("datetime", {})
        
        if datetime_info.get("utc"):
            last_updated = datetime_info.get("utc")
        
        # Get parameter name for this sensor
        if sensor_id not in sensor_params_cache:
            sensor_params_cache[sensor_id] = get_sensor_parameter(sensor_id)
        
        parameter_name = sensor_params_cache[sensor_id]
        
        if parameter_name == "pm25" and value is not None:
            pm25_value = value
    
    # Fetch weather data from Open-Meteo API
    weather_data = get_weather_data(lat, lon)
    
    # Prepare response with both air quality and temperature data
    response_data = {
        "station_name": nearest_station.get("name", "Unknown Station"),
        "distance_km": round(min_distance, 1),
        "latitude": nearest_station.get("coordinates", {}).get("latitude"),
        "longitude": nearest_station.get("coordinates", {}).get("longitude"),
        "pm25": pm25_value,
        "last_updated": last_updated
    }
    
    # Add weather data if available
    if weather_data:
        response_data["temperature_celsius"] = weather_data["temperature_celsius"]
        response_data["relative_humidity"] = weather_data["relative_humidity"]
        response_data["wind_speed"] = weather_data["wind_speed"]
        response_data["weather_time"] = weather_data["weather_time"]
    else:
        response_data["temperature_celsius"] = None
        response_data["relative_humidity"] = None
        response_data["wind_speed"] = None
        response_data["weather_time"] = None
        response_data["warning"] = "Weather data unavailable"
    
    # Save data to CSV file
    save_airquality_csv(response_data, lat, lon)
    
    return response_data

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Air Quality API",
        "description": "Get nearest air quality data using OpenAQ API",
        "endpoints": {
            "/air-quality": "GET - Get air quality data for given coordinates (lat, lon)"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)