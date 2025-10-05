# 🌍 AirWatch - Real-time Air Quality Monitor

A comprehensive web application for monitoring real-time air quality data and generating PM2.5 predictions using machine learning. Built with React frontend and FastAPI backend.

![AirWatch Demo](https://img.shields.io/badge/Status-Active-green) ![Python](https://img.shields.io/badge/Python-3.11+-blue) ![React](https://img.shields.io/badge/React-19.1+-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green)

## ✨ Features

### 🗺️ Interactive Map
- **Real-time Location Selection**: Click anywhere on the map to get air quality data
- **Visual Markers**: Clear indicators showing selected locations
- **Responsive Design**: Works seamlessly on desktop and mobile devices

### 📊 Air Quality Monitoring
- **Real-time Data**: Fetches current air quality data from OpenAQ API
- **Multiple Metrics**: PM2.5, temperature, humidity, and wind speed
- **Quality Categories**: Color-coded air quality status (Good, Moderate, Unhealthy, etc.)
- **Nearest Station**: Automatically finds the closest monitoring station

### 🔮 PM2.5 Predictions
- **Machine Learning Powered**: Advanced ML models for accurate predictions
- **Multiple Time Horizons**: 1-hour, 6-hour, 12-hour, and 24-hour forecasts
- **Separate Generation**: Generate predictions on-demand with dedicated button
- **Visual Indicators**: Color-coded prediction categories

### 🎨 Modern UI/UX
- **Dark Theme**: Beautiful gradient background with modern design
- **Responsive Layout**: Optimized for all screen sizes
- **Loading States**: Smooth loading indicators and error handling
- **Scrollable Content**: Efficient layout that prevents overflow issues

## 🏗️ Architecture

### Frontend (`/frontend`)
- **Framework**: React 19.1+ with Vite
- **Styling**: Tailwind CSS 4.1+ for modern, responsive design
- **Maps**: Leaflet with React-Leaflet for interactive mapping
- **State Management**: React hooks for efficient state handling

### Backend (`/backend`)
- **Framework**: FastAPI for high-performance API
- **Data Sources**: OpenAQ API for real-time air quality data
- **Machine Learning**: Scikit-learn for PM2.5 predictions
- **Data Processing**: Pandas and NumPy for data manipulation

## 🚀 Quick Start

### Prerequisites
- **Node.js** 18+ and npm
- **Python** 3.11+
- **OpenAQ API Key** (optional, for higher rate limits)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd final_attempt
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your OpenAQ API key (optional)

# Start the backend server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

### 4. Access the Application
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📁 Project Structure

```
final_attempt/
├── backend/                 # FastAPI backend
│   ├── data/               # Air quality data cache
│   ├── forecast/           # ML models and utilities
│   ├── routers/            # API route handlers
│   ├── services/           # Business logic services
│   ├── main.py            # FastAPI application entry point
│   ├── requirements.txt   # Python dependencies
│   └── .env.example      # Environment variables template
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── api/          # API integration
│   │   ├── App.jsx       # Main application component
│   │   └── index.css     # Global styles
│   ├── package.json      # Node.js dependencies
│   └── vite.config.js    # Vite configuration
└── README.md             # This file
```

## 🔧 API Endpoints

### Air Quality Data
- `GET /air-quality?lat={lat}&lon={lon}` - Get air quality data for coordinates
- `GET /predictions?lat={lat}&lon={lon}` - Generate PM2.5 predictions

### Health Check
- `GET /` - API health check

## 🤖 Machine Learning Models

The application uses trained scikit-learn models for PM2.5 predictions:
- **1-hour forecast**: Short-term predictions
- **6-hour forecast**: Medium-term predictions  
- **12-hour forecast**: Extended predictions
- **24-hour forecast**: Long-term predictions

Models are trained on historical air quality data and consider multiple environmental factors.

## 🌐 Data Sources

- **OpenAQ**: Real-time air quality data from global monitoring stations
- **Open-Meteo**: Weather data for enhanced predictions
- **Local Cache**: Efficient data storage for improved performance

## 🎯 Usage

1. **Select Location**: Click anywhere on the map to select a location
2. **View Air Quality**: Instantly see current air quality metrics
3. **Generate Predictions**: Click "Generate PM2.5 Predictions" for forecasts
4. **Explore Data**: Scroll through detailed air quality information

## 🔒 Environment Variables

Create a `.env` file in the backend directory:

```env
OPENAQ_API_KEY=your_openaq_api_key_here  # Optional but recommended
```

## 🛠️ Development

### Backend Development
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
cd frontend
npm run dev
```

### Building for Production
```bash
# Frontend
cd frontend
npm run build

# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 📊 Features in Detail

### Air Quality Categories
- **Good** (0-15 μg/m³): Air quality is satisfactory
- **Moderate** (15-25 μg/m³): Acceptable for most people
- **Unhealthy for Sensitive** (25-37.5 μg/m³): Sensitive groups may experience symptoms
- **Unhealthy** (37.5-75 μg/m³): Everyone may experience health effects
- **Very Unhealthy** (75+ μg/m³): Health alert for everyone

### Responsive Design
- **Desktop**: Full-featured layout with side-by-side map and data
- **Mobile**: Stacked layout optimized for touch interaction
- **Tablet**: Adaptive layout that works on all screen sizes

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAQ** for providing free air quality data
- **Open-Meteo** for weather data
- **Leaflet** for the mapping library
- **FastAPI** for the excellent Python web framework
- **React** and **Tailwind CSS** for the modern frontend stack

## 📞 Support

If you have any questions or need help with the project, please:
1. Check the [API documentation](http://localhost:8000/docs) when running locally
2. Review the code comments and structure
3. Open an issue for bugs or feature requests

---

**Built with ❤️ for better air quality awareness**