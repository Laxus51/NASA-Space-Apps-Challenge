# prediction_router.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from services.prediction_service import predict_air_quality
from services.air_quality_service import get_air_quality_data
import pandas as pd
import os

router = APIRouter(prefix="/predict", tags=["predictions"])

class PredictionRequest(BaseModel):
    """Request model for air quality prediction."""
    pm25: float = Field(None, description="Current PM2.5 concentration (μg/m³) - optional, uses latest from CSV if not provided", ge=0)
    t2m: float = Field(None, description="Current temperature (°C) - optional, uses latest from CSV if not provided")
    wind_speed: float = Field(None, description="Current wind speed (m/s) - optional, uses latest from CSV if not provided", ge=0)
    relative_humidity: float = Field(None, description="Current relative humidity (%) - optional, uses latest from CSV if not provided", ge=0, le=100)
    lat: float = Field(None, description="Latitude coordinate - optional")
    lon: float = Field(None, description="Longitude coordinate - optional")

class PredictionResponse(BaseModel):
    """Response model for air quality prediction."""
    status: str
    predictions: Dict[str, float]

@router.post("/", response_model=PredictionResponse)
async def predict_pm25_levels(request: PredictionRequest):
    """
    Predict PM2.5 levels for multiple time horizons using real data from CSV files.
    
    This endpoint now uses real air quality data from CSV files in the data directory.
    If coordinates (lat, lon) are provided, it uses data from the specific CSV file for those coordinates.
    If input parameters are not provided, it automatically uses the latest available data.
    
    Parameters are optional - if not provided, the system will use the most recent data
    from CSV files for predictions.
    """
    try:
        result = predict_air_quality(
            pm25=request.pm25,
            t2m=request.t2m,
            wind_speed=request.wind_speed,
            relative_humidity=request.relative_humidity,
            lat=request.lat,
            lon=request.lon
        )
        
        return PredictionResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class CoordinateRequest(BaseModel):
    lat: float = Field(..., description="Latitude coordinate")
    lon: float = Field(..., description="Longitude coordinate")


@router.post("/from-coordinates", response_model=PredictionResponse)
async def predict_from_coordinates(request: CoordinateRequest):
    """
    Complete workflow: Fetch air quality data for coordinates, create CSV file, and generate predictions.
    
    This endpoint:
    1. Fetches current air quality data from the API for the given coordinates
    2. Creates a CSV file with the fetched data
    3. Uses that CSV file to generate predictions
    4. Returns the predictions
    
    Args:
        request: CoordinateRequest with latitude and longitude
    
    Returns:
        PredictionResponse with predictions based on the newly created CSV data
    """
    try:
        # Step 1: Fetch air quality data from API
        air_quality_data = await get_air_quality_data(request.lat, request.lon)
        
        if not air_quality_data or 'current' not in air_quality_data:
            raise HTTPException(status_code=404, detail="No air quality data found for these coordinates")
        
        current_data = air_quality_data['current']
        
        # Step 2: Create CSV file with the fetched data
        csv_filename = f"airquality_{request.lat}_{request.lon}.csv"
        csv_filepath = os.path.join("data", csv_filename)
        
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        # Create DataFrame with the current data
        df_data = {
            'date': [current_data['datetime']],
            'pm25': [current_data.get('pm25', 25.0)],
            't2m': [current_data.get('t2m', 20.0)],
            'wind_speed': [current_data.get('wind_speed', 5.0)],
            'relative_humidity': [current_data.get('relative_humidity', 60.0)]
        }
        
        df = pd.DataFrame(df_data)
        df.to_csv(csv_filepath, index=False)
        
        print(f"Created CSV file: {csv_filepath} with data: {df_data}")
        
        # Step 3: Generate predictions using the newly created CSV
        result = predict_air_quality(
            lat=request.lat,
            lon=request.lon
        )
        
        return PredictionResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to complete workflow: {str(e)}")