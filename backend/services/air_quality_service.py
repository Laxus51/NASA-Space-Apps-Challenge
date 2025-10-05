import os
import csv
import math
import requests
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
    """Search for air quality monitoring stations within a radius."""
    headers = {}
    if OPENAQ_API_KEY:
        headers["X-API-Key"] = OPENAQ_API_KEY
    
    params = {
        "coordinates": f"{lat},{lon}",
        "radius": radius_meters,
        "limit": 100
    }
    
    try:
        response = requests.get(f"{OPENAQ_BASE_URL}/locations", params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get("results", [])
    except requests.RequestException as e:
        print(f"Error searching stations: {e}")
        return None

def get_sensor_parameter(sensor_id: int) -> Optional[str]:
    """Get the parameter type for a specific sensor."""
    headers = {}
    if OPENAQ_API_KEY:
        headers["X-API-Key"] = OPENAQ_API_KEY
    
    try:
        response = requests.get(f"{OPENAQ_BASE_URL}/sensors/{sensor_id}", headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if "results" in data and len(data["results"]) > 0:
            sensor = data["results"][0]
            return sensor.get("parameter", {}).get("name")
        return None
    except requests.RequestException as e:
        print(f"Error getting sensor parameter: {e}")
        return None

def get_latest_measurements(location_id: int) -> Optional[dict]:
    """Get the latest measurements for a location."""
    headers = {}
    if OPENAQ_API_KEY:
        headers["X-API-Key"] = OPENAQ_API_KEY
    
    params = {
        "locations_id": location_id,
        "limit": 100,
        "order_by": "datetime",
        "sort": "desc"
    }
    
    try:
        response = requests.get(f"{OPENAQ_BASE_URL}/latest", params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get("results", [])
    except requests.RequestException as e:
        print(f"Error getting latest measurements: {e}")
        return None

def get_weather_data(lat: float, lon: float) -> Optional[dict]:
    """Get current weather data from Open-Meteo API."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m"
    }
    
    try:
        response = requests.get(f"{OPEN_METEO_BASE_URL}/forecast", params=params)
        response.raise_for_status()
        data = response.json()
        
        if "current" in data:
            return {
                "t2m": data["current"].get("temperature_2m"),
                "relative_humidity": data["current"].get("relative_humidity_2m"),
                "wind_speed": data["current"].get("wind_speed_10m"),
                "datetime": data["current"].get("time")
            }
        return None
    except requests.RequestException as e:
        print(f"Error getting weather data: {e}")
        return None

def save_airquality_csv(data: dict, lat: float, lon: float) -> None:
    """Save air quality data to CSV file."""
    filename = f"data/airquality_{lat}_{lon}.csv"
    
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    # Check if file exists to determine if we need headers
    file_exists = os.path.exists(filename)
    
    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['date', 'pm25', 't2m', 'wind_speed', 'relative_humidity']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write header if file is new
        if not file_exists:
            writer.writeheader()
        
        # Write data row
        writer.writerow({
            'date': data.get('datetime', ''),
            'pm25': data.get('pm25', ''),
            't2m': data.get('t2m', ''),
            'wind_speed': data.get('wind_speed', ''),
            'relative_humidity': data.get('relative_humidity', '')
        })

async def get_air_quality_data(lat: float, lon: float) -> dict:
    """
    Get air quality data for given coordinates.
    This is the main function that combines air quality and weather data.
    """
    try:
        # Search for nearby stations
        stations = search_stations_by_radius(lat, lon, 50000)  # 50km radius
        
        if not stations:
            # Get weather data as fallback
            weather_data = get_weather_data(lat, lon)
            if weather_data:
                result = {
                    "location": {"lat": lat, "lon": lon},
                    "current": {
                        "pm25": None,
                        "t2m": weather_data.get("t2m"),
                        "wind_speed": weather_data.get("wind_speed"),
                        "relative_humidity": weather_data.get("relative_humidity"),
                        "datetime": weather_data.get("datetime")
                    },
                    "warning": "No nearby air quality stations found. Weather data only."
                }
                save_airquality_csv(result["current"], lat, lon)
                return result
            else:
                raise Exception("No air quality stations or weather data found")
        
        # Find the closest station with PM2.5 data
        closest_station = None
        min_distance = float('inf')
        
        for station in stations:
            if station.get("coordinates"):
                coords = station["coordinates"]
                station_lat = coords.get("latitude")
                station_lon = coords.get("longitude")
                
                if station_lat is not None and station_lon is not None:
                    distance = haversine_distance(lat, lon, station_lat, station_lon)
                    
                    # Check if station has PM2.5 sensors
                    has_pm25 = False
                    if "sensors" in station:
                        for sensor in station["sensors"]:
                            if sensor.get("parameter", {}).get("name") == "pm25":
                                has_pm25 = True
                                break
                    
                    if has_pm25 and distance < min_distance:
                        min_distance = distance
                        closest_station = station
        
        if not closest_station:
            # Get weather data as fallback
            weather_data = get_weather_data(lat, lon)
            if weather_data:
                result = {
                    "location": {"lat": lat, "lon": lon},
                    "current": {
                        "pm25": None,
                        "t2m": weather_data.get("t2m"),
                        "wind_speed": weather_data.get("wind_speed"),
                        "relative_humidity": weather_data.get("relative_humidity"),
                        "datetime": weather_data.get("datetime")
                    },
                    "warning": "No PM2.5 stations found nearby. Weather data only."
                }
                save_airquality_csv(result["current"], lat, lon)
                return result
            else:
                raise Exception("No PM2.5 stations or weather data found")
        
        # Get latest measurements from the closest station
        measurements = get_latest_measurements(closest_station["id"])
        
        if not measurements:
            raise Exception("No recent measurements available")
        
        # Extract PM2.5 data
        pm25_value = None
        measurement_time = None
        
        for measurement in measurements:
            if measurement.get("parameter", {}).get("name") == "pm25":
                pm25_value = measurement.get("value")
                measurement_time = measurement.get("date", {}).get("utc")
                break
        
        # Get weather data
        weather_data = get_weather_data(lat, lon)
        
        # Combine air quality and weather data
        result = {
            "location": {"lat": lat, "lon": lon},
            "station": {
                "id": closest_station["id"],
                "name": closest_station.get("name", "Unknown"),
                "distance_km": round(min_distance, 2),
                "coordinates": closest_station.get("coordinates")
            },
            "current": {
                "pm25": pm25_value,
                "t2m": weather_data.get("t2m") if weather_data else None,
                "wind_speed": weather_data.get("wind_speed") if weather_data else None,
                "relative_humidity": weather_data.get("relative_humidity") if weather_data else None,
                "datetime": measurement_time or (weather_data.get("datetime") if weather_data else None)
            },
            "last_updated": measurement_time,
            "weather_time": weather_data.get("datetime") if weather_data else None
        }
        
        # Save to CSV
        save_airquality_csv(result["current"], lat, lon)
        
        return result
        
    except Exception as e:
        raise Exception(f"Failed to get air quality data: {str(e)}")