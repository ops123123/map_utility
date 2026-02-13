# Coordinate Converter & Route Planner

A modern web application for coordinate conversion, geocoding, and route planning with traffic visualization.

## Features

- **Bidirectional Coordinate Conversion**: Convert between Web Mercator (X,Y) and WGS84 (Lat/Lon)
- **Interactive Map**: Leaflet.js powered map with OpenStreetMap tiles
- **Address Search**: Geocode addresses using Nominatim API (up to 5 results)
- **Distance Calculator**: Calculate routes with traffic simulation
- **Multiple Routes**: Get up to 3 alternative routes
- **Traffic Visualization**: Color-coded traffic congestion levels
- **Manual Location Picker**: Click on map to set exact locations
- **Modern UI**: Glassmorphism design with animated gradients
- **Comprehensive Documentation**: Built-in tabbed documentation page

## Tech Stack

- **Backend**: Flask (Python 3.x)
- **Frontend**: HTML5, CSS3, JavaScript
- **Mapping**: Leaflet.js
- **APIs**: OpenStreetMap Nominatim (geocoding), OSRM (routing)
- **Libraries**: pyproj, requests, urllib3

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup Steps

1. **Clone or download the project**

2. **Install Python dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```powershell
   python app.py
   ```

4. **Open your browser**:
   Navigate to `http://localhost:5000`

## Quick Start Commands

```powershell
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py

# Run tests (optional)
python test_app.py
```

## Usage

### Coordinate Conversion

1. **X,Y → Lat/Lon**: Enter X and Y values in meters, click Convert
2. **Lat/Lon → X,Y**: Enter latitude and longitude, click Convert
3. Results appear below with a colored marker on the map

### Address Search

1. Enter an address or place name
2. Click Search
3. View up to 5 results with coordinates
4. Click "Show on Map" to visualize

### Distance Calculator

1. Enter source and destination addresses
2. OR use "Pick on Map" buttons to click locations
3. Select traffic time period (optional)
4. Enable/disable traffic colors (optional)
5. Click "Calculate Routes"
6. View main route + alternatives with distances and times

### Map Features

- **Clear Markers**: Remove all markers
- **Reset View**: Return to world view
- **Fit to Markers**: Auto-zoom to show all markers
- Click markers or routes for popup details

## Traffic Time Periods

- **Current**: No adjustment (1.0x)
- **Morning Rush** (7-9 AM): +50% travel time (1.5x)
- **Mid-Day** (12-2 PM): +10% travel time (1.1x)
- **Evening Rush** (5-7 PM): +60% travel time (1.6x)
- **Night** (11 PM - 5 AM): -10% travel time (0.9x)
- **Weekend**: No adjustment (1.0x)

## Marker Colors

- 🔵 **Blue**: X,Y → Lat/Lon conversion result
- 🟢 **Green**: Lat/Lon → X,Y conversion result or route source
- 🔴 **Red**: Address search result or route destination

## Route Colors

- **Blue** (#2196F3): Main route
- **Light Blue** (#81D4FA): Alternative routes
- **Traffic Colors** (when enabled):
  - Blue: Clear traffic
  - Orange: Light traffic
  - Red-Orange: Heavy traffic
  - Red (dashed): Severe traffic

## API Endpoints

- `GET /` - Main application page
- `GET /docs` - Documentation page
- `POST /api/convert/xy-to-latlon` - Convert X,Y to Lat/Lon
- `POST /api/convert/latlon-to-xy` - Convert Lat/Lon to X,Y
- `POST /api/geocode` - Geocode an address
- `POST /api/reverse-geocode` - Reverse geocode coordinates
- `POST /api/route` - Calculate routes with traffic

## Testing

Run the comprehensive test suite:

```powershell
python test_app.py
```

The test suite includes 60+ tests covering:
- Coordinate conversion accuracy
- Flask endpoint functionality
- Geocoding services
- Route calculation
- Traffic multipliers
- Edge cases
- Integration workflows

## Project Structure

```
map_utility/
├── app.py                  # Flask backend
├── requirements.txt        # Python dependencies
├── test_app.py            # Test suite
├── summary_prompt.md      # Project specification
├── README.md              # This file
└── templates/
    ├── index.html         # Main UI page
    └── docs.html          # Documentation page
```

## Important Notes

- **Rate Limiting**: Nominatim API has a 1-second delay between requests
- **SSL Handling**: SSL verification is disabled for external APIs
- **Internet Required**: Application needs internet for map tiles and APIs
- **Traffic Simulation**: Traffic data is simulated, not real-time
- **Web Mercator Limits**: Works best between 85°N and 85°S latitude

## Troubleshooting

### Common Issues

1. **Import errors**: Make sure all dependencies are installed
   ```powershell
   pip install -r requirements.txt
   ```

2. **Port already in use**: Change port in app.py or stop other Flask apps

3. **Slow geocoding**: This is normal due to 1-second rate limit

4. **Route not found**: Ensure locations are accessible by road

5. **SSL warnings**: These are suppressed but harmless

## Browser Compatibility

- ✅ Chrome/Edge (recommended)
- ✅ Firefox
- ✅ Safari
- ❌ Internet Explorer (not supported)

## License

This project uses open-source services:
- OpenStreetMap data (ODbL)
- Nominatim API
- OSRM routing engine
- Leaflet.js (BSD 2-Clause)

## Contributing

To contribute:
1. Test your changes with `python test_app.py`
2. Maintain the existing code style
3. Update documentation as needed

## Credits

Built with:
- Flask web framework
- Leaflet.js mapping library
- OpenStreetMap contributors
- OSRM Project
- pyproj library

---

**Enjoy mapping! 🗺️**
