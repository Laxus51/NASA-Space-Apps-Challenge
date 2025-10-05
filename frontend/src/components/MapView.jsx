import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default markers in react-leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Custom marker icon for air quality stations
const createCustomIcon = (color) => {
  return L.divIcon({
    className: 'custom-marker',
    html: `<div style="background-color: ${color}; width: 20px; height: 20px; border-radius: 50%; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);"></div>`,
    iconSize: [20, 20],
    iconAnchor: [10, 10],
  });
};

// Component to handle map clicks
function MapClickHandler({ onMapClick }) {
  useMapEvents({
    click: (e) => {
      const { lat, lng } = e.latlng;
      onMapClick(lat, lng);
    },
  });
  return null;
}

const MapView = ({ onLocationSelect, selectedLocation, airQualityData, isLoading }) => {
  const [userLocation, setUserLocation] = useState(null);
  const [mapCenter, setMapCenter] = useState([40.7128, -74.0060]); // Default to NYC

  // Get user's current location
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          setUserLocation([latitude, longitude]);
          setMapCenter([latitude, longitude]);
        },
        (error) => {
          console.warn('Geolocation error:', error);
          // Keep default location if geolocation fails
        },
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 600000, // 10 minutes
        }
      );
    }
  }, []);

  const handleMapClick = (lat, lng) => {
    onLocationSelect(lat, lng);
  };

  // Create marker icon based on air quality data
  const getMarkerIcon = () => {
    if (!airQualityData || !airQualityData.pm25) {
      return createCustomIcon('#6b7280'); // Gray for no data
    }

    const pm25 = airQualityData.pm25;
    let color = '#6b7280'; // Default gray

    if (pm25 <= 15) color = '#10b981'; // Green
    else if (pm25 <= 25) color = '#f59e0b'; // Yellow
    else if (pm25 <= 37.5) color = '#f97316'; // Orange
    else if (pm25 <= 75) color = '#ef4444'; // Red
    else color = '#8b5cf6'; // Purple

    return createCustomIcon(color);
  };

  return (
    <div className="relative w-full h-full">
      {/* Loading overlay */}
      {isLoading && (
        <div className="absolute top-4 left-4 z-[1000] bg-black/80 text-white px-4 py-2 rounded-lg backdrop-blur-sm">
          <div className="flex items-center space-x-2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            <span className="text-sm">Loading air quality data...</span>
          </div>
        </div>
      )}

      {/* Instructions */}
      <div className="absolute top-4 right-4 z-[1000] bg-black/80 text-white px-4 py-2 rounded-lg backdrop-blur-sm max-w-xs">
        <p className="text-sm">
          📍 Click anywhere on the map to get air quality data for that location
        </p>
      </div>

      <MapContainer
        center={mapCenter}
        zoom={10}
        className="w-full h-full rounded-lg"
        style={{ minHeight: '400px' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        <MapClickHandler onMapClick={handleMapClick} />

        {/* User location marker */}
        {userLocation && (
          <Marker position={userLocation}>
            <Popup>
              <div className="text-center">
                <strong>Your Location</strong>
                <br />
                <span className="text-sm text-gray-600">
                  {userLocation[0].toFixed(4)}, {userLocation[1].toFixed(4)}
                </span>
              </div>
            </Popup>
          </Marker>
        )}

        {/* Selected location marker with air quality data */}
        {selectedLocation && (
          <Marker 
            position={selectedLocation} 
            icon={getMarkerIcon()}
          >
            <Popup>
              <div className="text-center min-w-[200px]">
                <strong>Selected Location</strong>
                <br />
                <span className="text-sm text-gray-600">
                  {selectedLocation[0].toFixed(4)}, {selectedLocation[1].toFixed(4)}
                </span>
                {airQualityData && (
                  <div className="mt-2 text-sm">
                    {airQualityData.station_name ? (
                      <>
                        <div><strong>{airQualityData.station_name}</strong></div>
                        <div>Distance: {airQualityData.distance_km} km</div>
                        {airQualityData.pm25 && (
                          <div>PM2.5: {airQualityData.pm25.toFixed(1)} μg/m³</div>
                        )}
                      </>
                    ) : (
                      <div className="text-orange-600">
                        {airQualityData.message || 'No air quality data available'}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </Popup>
          </Marker>
        )}
      </MapContainer>
    </div>
  );
};

export default MapView;