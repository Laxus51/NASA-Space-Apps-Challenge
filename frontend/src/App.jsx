import React, { useState } from 'react';
import MapView from './components/MapView';
import DataCard from './components/DataCard';
import { fetchAirQualityData, fetchPredictionsFromCoordinates } from './api/airquality';

function App() {
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [airQualityData, setAirQualityData] = useState(null);
  const [predictions, setPredictions] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isPredictionLoading, setIsPredictionLoading] = useState(false);
  const [error, setError] = useState(null);
  const [predictionError, setPredictionError] = useState(null);

  const handleLocationSelect = async (lat, lng) => {
    setSelectedLocation([lat, lng]);
    setIsLoading(true);
    setError(null);
    setAirQualityData(null);
    setPredictions(null);
    setPredictionError(null);
    
    try {
      // Only fetch air quality data on map click
      const airQualityResult = await fetchAirQualityData(lat, lng);
      setAirQualityData(airQualityResult);
      
    } catch (err) {
      setError('Failed to fetch air quality data');
      console.error('Error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGeneratePredictions = async () => {
    if (!selectedLocation) return;
    
    setIsPredictionLoading(true);
    setPredictionError(null);
    setPredictions(null);
    
    try {
      const [lat, lng] = selectedLocation;
      const predictionsResult = await fetchPredictionsFromCoordinates(lat, lng);
      setPredictions(predictionsResult);
      
    } catch (err) {
      setPredictionError('Failed to generate predictions');
      console.error('Prediction Error:', err);
    } finally {
      setIsPredictionLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900 flex flex-col">
      {/* Header */}
      <header className="w-full bg-black/50 backdrop-blur-sm border-b border-gray-700 flex-shrink-0">
        <div className="w-full px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">🌍</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">AirWatch</h1>
                <p className="text-sm text-gray-400">Real-time Air Quality Monitor</p>
              </div>
            </div>
            <div className="hidden md:flex items-center space-x-4 text-sm text-gray-400">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span>Good</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                <span>Moderate</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-orange-500 rounded-full"></div>
                <span>Unhealthy</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                <span>Very Unhealthy</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 w-full px-4 py-6 min-h-0">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 h-full w-full max-h-full">
          {/* Map Section */}
          <div className="lg:col-span-2 bg-gray-800/30 backdrop-blur-sm border border-gray-700 rounded-xl overflow-hidden h-full">
            <MapView
              onLocationSelect={handleLocationSelect}
              selectedLocation={selectedLocation}
              airQualityData={airQualityData}
              isLoading={isLoading}
            />
          </div>

          {/* Data Card Section */}
          <div className="lg:col-span-1 h-full max-h-full overflow-hidden">
            <div className="h-full overflow-y-auto">
              <DataCard
                data={airQualityData}
                predictions={predictions}
                isLoading={isLoading}
                isPredictionLoading={isPredictionLoading}
                error={error}
                predictionError={predictionError}
                selectedLocation={selectedLocation}
                onGeneratePredictions={handleGeneratePredictions}
              />
            </div>
          </div>
        </div>
      </main>

      {/* Prevention Details Section */}
      <section className="w-full bg-gray-800/20 backdrop-blur-sm border-t border-gray-700 flex-shrink-0">
        <div className="w-full px-4 py-8">
          <div className="max-w-6xl mx-auto">
            <h2 className="text-2xl font-bold text-white mb-6 text-center">
              🛡️ Air Quality Protection Guide
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {/* Good Air Quality */}
              <div className="bg-green-900/30 border border-green-600/50 rounded-lg p-4">
                <div className="flex items-center mb-3">
                  <div className="w-4 h-4 bg-green-500 rounded-full mr-2"></div>
                  <h3 className="text-lg font-semibold text-green-400">Good (0-50 μg/m³)</h3>
                </div>
                <ul className="text-sm text-gray-300 space-y-2">
                  <li>• Perfect for outdoor activities</li>
                  <li>• No health precautions needed</li>
                  <li>• Ideal for exercise and sports</li>
                  <li>• Windows can stay open</li>
                </ul>
              </div>

              {/* Moderate Air Quality */}
              <div className="bg-yellow-900/30 border border-yellow-600/50 rounded-lg p-4">
                <div className="flex items-center mb-3">
                  <div className="w-4 h-4 bg-yellow-500 rounded-full mr-2"></div>
                  <h3 className="text-lg font-semibold text-yellow-400">Moderate (51-100 μg/m³)</h3>
                </div>
                <ul className="text-sm text-gray-300 space-y-2">
                  <li>• Sensitive people should limit outdoor time</li>
                  <li>• Consider indoor exercise</li>
                  <li>• Close windows during peak hours</li>
                  <li>• Use air purifiers if available</li>
                </ul>
              </div>

              {/* Unhealthy Air Quality */}
              <div className="bg-red-900/30 border border-red-600/50 rounded-lg p-4">
                <div className="flex items-center mb-3">
                  <div className="w-4 h-4 bg-red-500 rounded-full mr-2"></div>
                  <h3 className="text-lg font-semibold text-red-400">Unhealthy (101+ μg/m³)</h3>
                </div>
                <ul className="text-sm text-gray-300 space-y-2">
                  <li>• Avoid outdoor activities</li>
                  <li>• Wear N95 masks when outside</li>
                  <li>• Keep windows closed</li>
                  <li>• Use air purifiers indoors</li>
                </ul>
              </div>
            </div>

            {/* General Tips */}
            <div className="mt-8 bg-blue-900/20 border border-blue-600/50 rounded-lg p-6">
              <h3 className="text-xl font-semibold text-blue-400 mb-4 flex items-center">
                💡 General Protection Tips
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 className="text-lg font-medium text-white mb-2">Indoor Protection</h4>
                  <ul className="text-sm text-gray-300 space-y-1">
                    <li>• Use HEPA air purifiers</li>
                    <li>• Keep windows closed during high pollution</li>
                    <li>• Avoid smoking indoors</li>
                    <li>• Use exhaust fans while cooking</li>
                    <li>• Consider indoor plants for natural air cleaning</li>
                  </ul>
                </div>
                <div>
                  <h4 className="text-lg font-medium text-white mb-2">Outdoor Protection</h4>
                  <ul className="text-sm text-gray-300 space-y-1">
                    <li>• Check air quality before going out</li>
                    <li>• Wear N95 or P100 masks in polluted areas</li>
                    <li>• Avoid busy roads and industrial areas</li>
                    <li>• Exercise early morning or late evening</li>
                    <li>• Stay hydrated and eat antioxidant-rich foods</li>
                  </ul>
                </div>
              </div>
            </div>

            {/* Vulnerable Groups */}
            <div className="mt-6 bg-purple-900/20 border border-purple-600/50 rounded-lg p-6">
              <h3 className="text-xl font-semibold text-purple-400 mb-4 flex items-center">
                ⚠️ Special Precautions for Vulnerable Groups
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <h4 className="text-lg font-medium text-white mb-2">Children & Elderly</h4>
                  <ul className="text-sm text-gray-300 space-y-1">
                    <li>• More sensitive to air pollution</li>
                    <li>• Limit outdoor time when AQI {'>'}100</li>
                    <li>• Monitor for breathing difficulties</li>
                  </ul>
                </div>
                <div>
                  <h4 className="text-lg font-medium text-white mb-2">Respiratory Conditions</h4>
                  <ul className="text-sm text-gray-300 space-y-1">
                    <li>• Asthma, COPD patients extra careful</li>
                    <li>• Keep rescue inhalers handy</li>
                    <li>• Consult doctor for action plans</li>
                  </ul>
                </div>
                <div>
                  <h4 className="text-lg font-medium text-white mb-2">Heart Conditions</h4>
                  <ul className="text-sm text-gray-300 space-y-1">
                    <li>• Avoid strenuous outdoor activities</li>
                    <li>• Monitor symptoms closely</li>
                    <li>• Follow medical advice strictly</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="w-full bg-black/50 backdrop-blur-sm border-t border-gray-700 flex-shrink-0">
        <div className="w-full px-4 py-4">
          <div className="flex flex-col md:flex-row items-center justify-between text-sm text-gray-400">
            <div className="flex items-center space-x-4">
              <span>Powered by OpenAQ & Open-Meteo APIs</span>
              <span>•</span>
              <span>Real-time Environmental Data</span>
            </div>
            <div className="mt-2 md:mt-0">
              <span>Built with React + Leaflet</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
