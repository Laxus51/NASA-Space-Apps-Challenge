const API_BASE_URL = 'http://localhost:8000';

/**
 * Fetch air quality data for given coordinates
 * @param {number} lat - Latitude
 * @param {number} lon - Longitude
 * @returns {Promise<Object>} Air quality data
 */
export const fetchAirQualityData = async (lat, lon) => {
  try {
    const response = await fetch(`${API_BASE_URL}/air-quality?lat=${lat}&lon=${lon}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching air quality data:', error);
    throw error;
  }
};

/**
 * Fetch predictions for given coordinates (complete workflow)
 * @param {number} lat - Latitude
 * @param {number} lon - Longitude
 * @returns {Promise<Object>} Prediction data
 */
export const fetchPredictionsFromCoordinates = async (lat, lon) => {
  try {
    const response = await fetch(`${API_BASE_URL}/predict/from-coordinates`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ lat, lon }),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching predictions:', error);
    throw error;
  }
};

/**
 * Get air quality category and color based on PM2.5 value
 * Based on WHO Air Quality Guidelines
 * @param {number} pm25 - PM2.5 value in μg/m³
 * @returns {Object} Category info with color and label
 */
export const getAirQualityCategory = (pm25) => {
  if (pm25 === null || pm25 === undefined) {
    return {
      category: 'Unknown',
      color: 'bg-gray-500',
      textColor: 'text-white',
      description: 'No data available'
    };
  }

  if (pm25 <= 15) {
    return {
      category: 'Good',
      color: 'bg-green-500',
      textColor: 'text-white',
      description: 'Air quality is satisfactory'
    };
  } else if (pm25 <= 25) {
    return {
      category: 'Moderate',
      color: 'bg-yellow-500',
      textColor: 'text-black',
      description: 'Acceptable for most people'
    };
  } else if (pm25 <= 37.5) {
    return {
      category: 'Unhealthy for Sensitive',
      color: 'bg-orange-500',
      textColor: 'text-white',
      description: 'Sensitive groups may experience symptoms'
    };
  } else if (pm25 <= 75) {
    return {
      category: 'Unhealthy',
      color: 'bg-red-500',
      textColor: 'text-white',
      description: 'Everyone may experience health effects'
    };
  } else {
    return {
      category: 'Very Unhealthy',
      color: 'bg-purple-600',
      textColor: 'text-white',
      description: 'Health alert: everyone may experience serious effects'
    };
  }
};