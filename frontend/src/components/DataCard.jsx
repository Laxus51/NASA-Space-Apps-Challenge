import React from 'react';
import { getAirQualityCategory } from '../api/airquality';

const DataCard = ({ data, isLoading, error, selectedLocation, predictions, isPredictionLoading, predictionError, onGeneratePredictions }) => {
  if (!selectedLocation) {
    return (
      <div className="bg-gray-900/90 backdrop-blur-sm border border-gray-700 rounded-xl p-6 text-white h-full flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">🗺️</div>
          <h3 className="text-xl font-semibold mb-2">Air Quality Monitor</h3>
          <p className="text-gray-400">Click anywhere on the map to get air quality data</p>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="bg-gray-900/90 backdrop-blur-sm border border-gray-700 rounded-xl p-6 text-white h-full flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <h3 className="text-xl font-semibold mb-2">Analyzing Location</h3>
          <p className="text-gray-400">Fetching air quality data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-gray-900/90 backdrop-blur-sm border border-red-500/50 rounded-xl p-6 text-white h-full flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">⚠️</div>
          <h3 className="text-xl font-semibold mb-2 text-red-400">Error</h3>
          <p className="text-gray-400">Failed to fetch air quality data</p>
          <p className="text-sm text-red-400 mt-2">{error.message}</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="bg-gray-900/90 backdrop-blur-sm border border-gray-700 rounded-xl p-6 text-white h-full flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">📍</div>
          <h3 className="text-xl font-semibold mb-2">Location Selected</h3>
          <p className="text-gray-400">No data available for this location</p>
        </div>
      </div>
    );
  }

  const airQualityInfo = getAirQualityCategory(data.pm25);
  const formatDateTime = (dateString) => {
    if (!dateString) return 'N/A';
    try {
      return new Date(dateString).toLocaleString();
    } catch {
      return dateString;
    }
  };

  const formatValue = (value, unit = '', decimals = 1) => {
    if (value === null || value === undefined) return 'N/A';
    if (typeof value === 'number') {
      return `${value.toFixed(decimals)}${unit}`;
    }
    return `${value}${unit}`;
  };

  return (
    <div className="bg-gray-900/90 backdrop-blur-sm border border-gray-700 rounded-xl h-full flex flex-col">
      {/* Fixed Header */}
      <div className="border-b border-gray-700 p-4 flex-shrink-0">
        <h2 className="text-xl font-bold text-blue-400 mb-1">Air Quality Data</h2>
        <div className="text-sm text-gray-400">
          📍 {selectedLocation[0].toFixed(4)}, {selectedLocation[1].toFixed(4)}
        </div>
      </div>

      {/* Scrollable Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Station Info */}
        {data.station_name ? (
          <div className="bg-gray-800/50 p-3 rounded-lg border border-gray-600">
            <div className="flex items-center justify-between mb-1">
              <h3 className="text-sm font-semibold text-green-400">🏢 {data.station_name}</h3>
              <span className="text-xs text-gray-400">
                📏 {formatValue(data.distance_km, ' km')}
              </span>
            </div>
            <div className="text-xs text-gray-400">
              {formatValue(data.latitude, '°', 4)}, {formatValue(data.longitude, '°', 4)}
            </div>
          </div>
        ) : (
          <div className="p-3 bg-orange-900/30 border border-orange-500/30 rounded-lg">
            <div className="text-orange-400 font-semibold text-sm mb-1">⚠️ No Station Found</div>
            <div className="text-xs text-gray-400">{data.message}</div>
          </div>
        )}

        {/* Air Quality Status */}
        {data.pm25 !== null && data.pm25 !== undefined && (
          <div className={`${airQualityInfo.color} ${airQualityInfo.textColor} p-3 rounded-lg`}>
            <div className="flex items-center justify-between">
              <span className="font-bold text-sm">{airQualityInfo.category}</span>
              <span className="text-lg font-bold">{formatValue(data.pm25, ' μg/m³')}</span>
            </div>
            <div className="text-xs mt-1 opacity-90">{airQualityInfo.description}</div>
          </div>
        )}

        {/* Data Grid */}
        <div className="grid grid-cols-2 gap-2">
          {/* PM2.5 */}
          <div className="bg-gray-800/50 p-3 rounded-lg border border-gray-600">
            <div className="text-xs text-gray-400 mb-1">PM2.5</div>
            <div className="text-sm font-bold text-white">
              {formatValue(data.pm25, ' μg/m³')}
            </div>
          </div>

          {/* Temperature */}
          <div className="bg-gray-800/50 p-3 rounded-lg border border-gray-600">
            <div className="text-xs text-gray-400 mb-1">🌡️ Temperature</div>
            <div className="text-sm font-bold text-white">
              {formatValue(data.temperature_celsius, '°C')}
            </div>
          </div>

          {/* Humidity */}
          <div className="bg-gray-800/50 p-3 rounded-lg border border-gray-600">
            <div className="text-xs text-gray-400 mb-1">💧 Humidity</div>
            <div className="text-sm font-bold text-white">
              {formatValue(data.relative_humidity, '%', 0)}
            </div>
          </div>

          {/* Wind Speed */}
          <div className="bg-gray-800/50 p-3 rounded-lg border border-gray-600">
            <div className="text-xs text-gray-400 mb-1">💨 Wind Speed</div>
            <div className="text-sm font-bold text-white">
              {formatValue(data.wind_speed, ' m/s')}
            </div>
          </div>
        </div>

        {/* Generate Predictions Button */}
        <div className="bg-gray-800/30 border border-gray-600 rounded-lg p-3">
          <button
            onClick={onGeneratePredictions}
            disabled={isPredictionLoading}
            className={`w-full py-2 px-4 rounded-lg font-medium text-sm transition-all duration-200 border-0 ${
              isPredictionLoading
                ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                : 'bg-purple-600 hover:bg-purple-700 text-white hover:shadow-lg'
            }`}
            style={{
              backgroundColor: isPredictionLoading ? '#4B5563' : '#7C3AED',
              color: isPredictionLoading ? '#9CA3AF' : '#FFFFFF',
              border: 'none'
            }}
          >
            {isPredictionLoading ? (
              <div className="flex items-center justify-center">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Generating Predictions...
              </div>
            ) : (
              '🔮 Generate PM2.5 Predictions'
            )}
          </button>
          
          {predictionError && (
            <div className="mt-2 text-xs text-red-400 text-center">
              {predictionError}
            </div>
          )}
        </div>

        {/* Predictions */}
        {predictions && predictions.status === 'success' && (
          <div className="bg-gray-800/30 border border-gray-600 rounded-lg p-3">
            <h3 className="text-sm font-semibold text-purple-400 mb-3 flex items-center">
              🔮 PM2.5 Predictions
            </h3>
            <div className="grid grid-cols-2 gap-2">
              {Object.entries(predictions.predictions).map(([horizon, value]) => {
                const category = getAirQualityCategory(value);
                return (
                  <div key={horizon} className="bg-gray-700/50 rounded p-2">
                    <div className="text-xs text-gray-400 mb-1">{horizon}</div>
                    <div className="text-sm font-semibold text-white mb-1">
                      {value} μg/m³
                    </div>
                    <div className={`px-2 py-1 rounded text-xs font-medium ${category.color} ${category.textColor}`}>
                      {category.category}
                    </div>
                  </div>
                );
              })}
            </div>
            <div className="mt-2 text-xs text-gray-500">
              Based on: {predictions.input_data?.timestamp ? 
                formatDateTime(predictions.input_data.timestamp) : 'Current time'}
            </div>
          </div>
        )}

        {/* Timestamps */}
        <div className="space-y-1 text-xs">
          {data.last_updated && (
            <div>
              <span className="text-gray-400">Air Quality: </span>
              <span className="text-white">{formatDateTime(data.last_updated)}</span>
            </div>
          )}
          {data.weather_time && (
            <div>
              <span className="text-gray-400">Weather: </span>
              <span className="text-white">{formatDateTime(data.weather_time)}</span>
            </div>
          )}
          {data.warning && (
            <div className="text-yellow-400">
              ⚠️ {data.warning}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DataCard;