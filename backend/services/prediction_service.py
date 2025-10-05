# prediction_service.py
import os
import pandas as pd
from datetime import datetime
from typing import Optional, Dict, Any
from forecast.forecast_utils import load_models, forecast_pm25

# Load models once when the module is imported
models = None

def get_models():
    """Get loaded models, loading them if necessary."""
    global models
    if models is None:
        models = load_models()
    return models

def get_data_from_csv_by_coordinates(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """
    Read data from CSV file for specific coordinates.
    
    Args:
        lat: Latitude
        lon: Longitude
    
    Returns:
        Dict with the air quality data for the coordinates, or None if not found
    """
    data_dir = "data"
    if not os.path.exists(data_dir):
        return None
    
    # Create filename based on coordinates (same format as backend creates)
    filename = f"airquality_{lat}_{lon}.csv"
    filepath = os.path.join(data_dir, filename)
    
    if not os.path.exists(filepath):
        print(f"CSV file not found for coordinates {lat}, {lon}: {filepath}")
        return None
    
    try:
        df = pd.read_csv(filepath)
        if df.empty:
            print(f"CSV file is empty: {filepath}")
            return None
        
        # Get the most recent row from this file
        df['date'] = pd.to_datetime(df['date'])
        latest_row = df.loc[df['date'].idxmax()]
        
        return {
            'date': latest_row['date'],
            'pm25': latest_row['pm25'],
            't2m': latest_row['t2m'],
            'wind_speed': latest_row['wind_speed'],
            'relative_humidity': latest_row['relative_humidity']
        }
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None

def get_latest_data_from_csv() -> Optional[Dict[str, Any]]:
    """
    Read the most recent data from all CSV files in the data directory.
    Fallback method when no specific coordinates are provided.
    
    Returns:
        Dict with the latest air quality data, or None if no data found
    """
    data_dir = "data"
    if not os.path.exists(data_dir):
        return None
    
    latest_data = None
    latest_timestamp = None
    
    # Iterate through all CSV files in the data directory
    for filename in os.listdir(data_dir):
        if filename.endswith('.csv'):
            filepath = os.path.join(data_dir, filename)
            try:
                df = pd.read_csv(filepath)
                if not df.empty:
                    # Get the most recent row from this file
                    df['date'] = pd.to_datetime(df['date'])
                    latest_row = df.loc[df['date'].idxmax()]
                    
                    # Check if this is the most recent across all files
                    if latest_timestamp is None or latest_row['date'] > latest_timestamp:
                        latest_timestamp = latest_row['date']
                        latest_data = {
                            'date': latest_row['date'],
                            'pm25': latest_row['pm25'],
                            't2m': latest_row['t2m'],
                            'wind_speed': latest_row['wind_speed'],
                            'relative_humidity': latest_row['relative_humidity']
                        }
            except Exception as e:
                print(f"Error reading {filename}: {e}")
                continue
    
    return latest_data

def predict_air_quality(pm25: Optional[float] = None, 
                        t2m: Optional[float] = None, 
                        wind_speed: Optional[float] = None, 
                        relative_humidity: Optional[float] = None,
                        lat: Optional[float] = None,
                        lon: Optional[float] = None) -> Dict[str, Any]:
    """
    Predict air quality using the trained models.
    If coordinates are provided, uses data from the specific CSV file for those coordinates.
    If parameters are not provided, uses the latest data from CSV files.
    
    Args:
        pm25: PM2.5 concentration (μg/m³)
        t2m: Temperature at 2 meters (°C)
        wind_speed: Wind speed (m/s)
        relative_humidity: Relative humidity (%)
        lat: Latitude (for CSV file lookup)
        lon: Longitude (for CSV file lookup)
    
    Returns:
        Dictionary containing predictions for different time horizons
    """
    try:
        # Try to get data from specific CSV if coordinates provided
        if lat is not None and lon is not None:
            csv_data = get_data_from_csv_by_coordinates(lat, lon)
            if csv_data:
                pm25 = pm25 if pm25 is not None else csv_data['pm25']
                t2m = t2m if t2m is not None else csv_data['t2m']
                wind_speed = wind_speed if wind_speed is not None else csv_data['wind_speed']
                relative_humidity = relative_humidity if relative_humidity is not None else csv_data['relative_humidity']
                latest_datetime = csv_data['date']
                print(f"Using data from CSV for coordinates ({lat}, {lon}) from {latest_datetime}: PM2.5={pm25}, T={t2m}°C, Wind={wind_speed}m/s, RH={relative_humidity}%")
            else:
                print(f"No CSV data found for coordinates ({lat}, {lon}), using fallback")
                # Fallback to default values if no CSV data available for coordinates
                pm25 = pm25 if pm25 is not None else 25.0
                t2m = t2m if t2m is not None else 20.0
                wind_speed = wind_speed if wind_speed is not None else 5.0
                relative_humidity = relative_humidity if relative_humidity is not None else 60.0
                latest_datetime = datetime.now()
        # Try to get latest data from any CSV if parameters not provided and no coordinates
        elif any(param is None for param in [pm25, t2m, wind_speed, relative_humidity]):
            csv_data = get_latest_data_from_csv()
            if csv_data:
                pm25 = pm25 if pm25 is not None else csv_data['pm25']
                t2m = t2m if t2m is not None else csv_data['t2m']
                wind_speed = wind_speed if wind_speed is not None else csv_data['wind_speed']
                relative_humidity = relative_humidity if relative_humidity is not None else csv_data['relative_humidity']
                latest_datetime = csv_data['date']
                print(f"Using real data from {latest_datetime}: PM2.5={pm25}, T={t2m}°C, Wind={wind_speed}m/s, RH={relative_humidity}%")
            else:
                # Fallback to default values if no CSV data available
                pm25 = pm25 if pm25 is not None else 25.0
                t2m = t2m if t2m is not None else 20.0
                wind_speed = wind_speed if wind_speed is not None else 5.0
                relative_humidity = relative_humidity if relative_humidity is not None else 60.0
                latest_datetime = datetime.now()
                print(f"Using fallback data: PM2.5={pm25}, T={t2m}°C, Wind={wind_speed}m/s, RH={relative_humidity}%")
        else:
            latest_datetime = datetime.now()
            print(f"Using provided data: PM2.5={pm25}, T={t2m}°C, Wind={wind_speed}m/s, RH={relative_humidity}%")
        
        # Load models
        models = load_models()
        
        # Make predictions using forecast_pm25 function
        predictions = forecast_pm25(
            models, 
            latest_datetime,
            pm25, 
            t2m, 
            wind_speed, 
            relative_humidity
        )
        
        return {
            'status': 'success',
            'predictions': predictions,
            'input_data': {
                'pm25': pm25,
                't2m': t2m,
                'wind_speed': wind_speed,
                'relative_humidity': relative_humidity,
                'timestamp': latest_datetime.isoformat() if hasattr(latest_datetime, 'isoformat') else str(latest_datetime)
            }
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Prediction failed: {str(e)}'
        }