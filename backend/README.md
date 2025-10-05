# Air Quality API Backend

A FastAPI backend that provides air quality data using the OpenAQ API v3.

## Features

- Get nearest air quality station data based on coordinates
- Progressive radius search (1km → 5km → 10km → 25km)
- Returns PM2.5 and PM10 measurements
- CORS enabled for frontend integration
- Proper error handling

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. (Optional) Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your OpenAQ API key
```

3. Run the server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### GET /air-quality

Get nearest air quality data for given coordinates.

**Parameters:**
- `lat` (float): Latitude coordinate
- `lon` (float): Longitude coordinate

**Example:**
```
GET http://localhost:8000/air-quality?lat=31.5204&lon=74.3587
```

**Response:**
```json
{
  "station_name": "Lahore US Consulate",
  "distance_km": 3.2,
  "latitude": 31.523,
  "longitude": 74.366,
  "pm25": 82.5,
  "pm10": 110.3,
  "last_updated": "2025-10-05T06:30:00Z"
}
```

If no station is found within 25km:
```json
{
  "message": "No station found within 25 km"
}
```

## Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.