Coordinate Converter & Route Planner - Quick Build Prompt
Tech Stack
Backend: Flask (Python 3.x)
Frontend: HTML/CSS/JavaScript with Leaflet.js
APIs: OpenStreetMap Nominatim (geocoding), OSRM (routing)
Libraries: pyproj, requests, urllib3
Core Features Summary
1. Bidirectional Coordinate Conversion
X,Y ↔ Lat/Lon using Web Mercator (EPSG:3857)
Two side-by-side converters with Convert/Clear buttons
Display results with 8 decimal (lat/lon) and 6 decimal (x/y) precision
Add color-coded markers to map (blue for X,Y→Lat/Lon, green for Lat/Lon→X,Y)
2. Interactive Leaflet Map (450px height, top of page)
OpenStreetMap tiles, default world view
Clear Markers and Reset View buttons
Auto-zoom to fit all markers/routes
Popup details on click
3. Address Search
Single input field with search button
Geocode via Nominatim API (up to 5 results)
Display results with lat/lon and x/y coordinates
"Show on Map" button for each result
Handle SSL with verify=False
4. Distance Calculator with Traffic
Source and destination address inputs
Swap button (🔄) to reverse addresses/coordinates
Traffic time dropdown: Current/Morning Rush/Mid-Day/Evening Rush/Night/Weekend
Traffic multipliers: +50% (morning), +60% (evening), +10% (mid-day), -10% (night)
"Show Traffic Congestion Colors" checkbox (default: checked)
Manual location picker buttons - click map to set exact source/destination
Calculate 1 main + 2 alternative routes via OSRM API
Display distance (km/miles), duration, traffic-adjusted time
5. Route Visualization
Main route: Blue (#2196F3), 6px
Alternatives: Light blue (#81D4FA), 4px
Traffic colors: Blue (clear) → Orange (light) → Red-Orange (heavy) → Red with pulsing dash (severe)
Click routes for popup with details
6. Modern UI Design
Animated gradient background (purple-pink-purple)
Glassmorphism containers with backdrop blur
Gradient text on title
Button shimmer effects on hover
Floating animations, smooth transitions (0.3s)
Responsive: two-column on desktop, stacked on mobile
7. Documentation Page (/docs)
7 tabbed sections: Overview, Conversion, Address Search, Distance Calculator, Map Features, Tips, FAQ
Color-coded info boxes, tables, examples
Opens in new tab from purple button on main page
Backend Implementation (app.py)
Functions to Create:
Flask Routes:
Key Implementation Details:
Add User-Agent header to all Nominatim requests
Use verify=False for SSL, suppress urllib3 warnings
1-second delay between geocoding requests (rate limit)
Retry OSRM calls 3 times with 500ms delay on SSL errors
Apply traffic multipliers based on time selection
Return up to 5 geocoding results, up to 3 route alternatives
Frontend Implementation (templates/index.html)
Page Layout (Top to Bottom):
Header with title and "View Documentation" button
Interactive Map View (Leaflet map)
Address Search section
Distance Calculator with swap button and manual pickers
Coordinate Converters (two columns)
Info box about Web Mercator
JavaScript Functions to Create:
Styling Highlights:
Animated gradient: @keyframes gradientShift
Glassmorphism: background: rgba(255,255,255,0.95); backdrop-filter: blur(10px)
Button shimmer: @keyframes shimmer
Traffic colors: .route-clear, .route-light, .route-heavy, .route-severe
Testing (test_app.py)
Test Coverage (60+ tests):
Conversion functions (10 tests)
Flask endpoints (15 tests)
Geocoding (8 tests)
Route calculation (12 tests)
UI pages (5 tests)
Edge cases (5 tests)
Integration workflows (5 tests)
Quick Start Commands
Critical Implementation Notes
SSL Handling: Add verify=False to all external API calls, suppress warnings
Rate Limiting: 1-second delay between Nominatim requests
Traffic Logic: Multiply base duration by time-specific factor
Map Order: Map at top, converters at bottom (user requested)
Swap Function: Exchange both text fields AND manual coordinates, update markers
Traffic Colors: Change route stroke color dynamically based on congestion level
Alternative Routes: Request with alternatives=true, draw with lighter blue
Manual Picker: Use map.once('click') to capture coordinates, then reverse geocode
Expected Result
A polished, full-featured web app with coordinate conversion, geocoding, route planning with traffic visualization, manual location selection, and comprehensive documentation - all with a modern animated UI.