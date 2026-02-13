from flask import Flask, render_template, request, jsonify
from pyproj import Transformer
import requests
import urllib3
import time

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# Initialize transformer for coordinate conversion
# EPSG:4326 (WGS84 lat/lon) <-> EPSG:3857 (Web Mercator x/y)
transformer_to_xy = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
transformer_to_latlon = Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True)


def xy_to_latlon(x, y):
    """Convert Web Mercator (x, y) to WGS84 (lat, lon)"""
    try:
        lon, lat = transformer_to_latlon.transform(float(x), float(y))
        return {"lat": round(lat, 8), "lon": round(lon, 8)}
    except Exception as e:
        return {"error": str(e)}


def latlon_to_xy(lat, lon):
    """Convert WGS84 (lat, lon) to Web Mercator (x, y)"""
    try:
        x, y = transformer_to_xy.transform(float(lon), float(lat))
        return {"x": round(x, 6), "y": round(y, 6)}
    except Exception as e:
        return {"error": str(e)}


def geocode_address(address):
    """Geocode an address using Nominatim API"""
    try:
        url = "https://nominatim.openstreetmap.org/search"
        headers = {
            "User-Agent": "MapUtility/1.0 (coordinate-converter-app)"
        }
        params = {
            "q": address,
            "format": "json",
            "limit": 5
        }
        
        response = requests.get(url, params=params, headers=headers, verify=False, timeout=10)
        response.raise_for_status()
        
        results = response.json()
        formatted_results = []
        
        for result in results:
            lat = float(result['lat'])
            lon = float(result['lon'])
            xy = latlon_to_xy(lat, lon)
            
            formatted_results.append({
                "display_name": result.get('display_name', 'Unknown'),
                "lat": round(lat, 8),
                "lon": round(lon, 8),
                "x": xy.get('x'),
                "y": xy.get('y')
            })
        
        # Rate limiting - 1 second delay
        time.sleep(1)
        
        return formatted_results
    except Exception as e:
        return {"error": str(e)}


def reverse_geocode(lat, lon):
    """Reverse geocode coordinates to get address"""
    try:
        url = "https://nominatim.openstreetmap.org/reverse"
        headers = {
            "User-Agent": "MapUtility/1.0 (coordinate-converter-app)"
        }
        params = {
            "lat": lat,
            "lon": lon,
            "format": "json"
        }
        
        response = requests.get(url, params=params, headers=headers, verify=False, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        
        # Rate limiting
        time.sleep(1)
        
        return result.get('display_name', 'Unknown location')
    except Exception as e:
        return "Unknown location"


def calculate_routes(source_lat, source_lon, dest_lat, dest_lon, traffic_time="current"):
    """Calculate routes using OSRM API with traffic adjustment"""
    try:
        # Traffic multipliers
        traffic_multipliers = {
            "current": 1.0,
            "morning": 1.5,  # +50%
            "midday": 1.1,   # +10%
            "evening": 1.6,  # +60%
            "night": 0.9,    # -10%
            "weekend": 1.0
        }
        
        multiplier = traffic_multipliers.get(traffic_time, 1.0)
        
        # Retry logic for SSL errors
        max_retries = 3
        retry_delay = 0.5
        
        for attempt in range(max_retries):
            try:
                url = f"http://router.project-osrm.org/route/v1/driving/{source_lon},{source_lat};{dest_lon},{dest_lat}"
                params = {
                    "alternatives": "true",
                    "steps": "false",
                    "geometries": "geojson",
                    "overview": "full"
                }
                
                response = requests.get(url, params=params, timeout=15)
                response.raise_for_status()
                
                data = response.json()
                
                if data.get('code') != 'Ok':
                    return {"error": "No route found"}
                
                routes = []
                for idx, route in enumerate(data.get('routes', [])[:3]):
                    distance_km = route['distance'] / 1000
                    distance_mi = distance_km * 0.621371
                    duration_sec = route['duration']
                    duration_min = duration_sec / 60
                    traffic_duration_min = duration_min * multiplier
                    
                    # Determine traffic level based on multiplier
                    if multiplier <= 1.0:
                        traffic_level = "clear"
                    elif multiplier <= 1.2:
                        traffic_level = "light"
                    elif multiplier <= 1.5:
                        traffic_level = "heavy"
                    else:
                        traffic_level = "severe"
                    
                    routes.append({
                        "geometry": route['geometry'],
                        "distance_km": round(distance_km, 2),
                        "distance_mi": round(distance_mi, 2),
                        "duration_min": round(duration_min, 1),
                        "traffic_duration_min": round(traffic_duration_min, 1),
                        "traffic_level": traffic_level,
                        "route_type": "main" if idx == 0 else "alternative"
                    })
                
                return {"routes": routes}
                
            except requests.exceptions.SSLError:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    raise
        
        return {"error": "Failed after retries"}
        
    except Exception as e:
        return {"error": str(e)}


# Flask Routes

@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')


@app.route('/docs')
def docs():
    """Render documentation page"""
    return render_template('docs.html')


@app.route('/api/convert/xy-to-latlon', methods=['POST'])
def api_xy_to_latlon():
    """API endpoint for X,Y to Lat/Lon conversion"""
    data = request.json
    x = data.get('x')
    y = data.get('y')
    
    if x is None or y is None:
        return jsonify({"error": "Missing x or y parameter"}), 400
    
    result = xy_to_latlon(x, y)
    
    if "error" in result:
        return jsonify(result), 400
    
    return jsonify(result)


@app.route('/api/convert/latlon-to-xy', methods=['POST'])
def api_latlon_to_xy():
    """API endpoint for Lat/Lon to X,Y conversion"""
    data = request.json
    lat = data.get('lat')
    lon = data.get('lon')
    
    if lat is None or lon is None:
        return jsonify({"error": "Missing lat or lon parameter"}), 400
    
    result = latlon_to_xy(lat, lon)
    
    if "error" in result:
        return jsonify(result), 400
    
    return jsonify(result)


@app.route('/api/geocode', methods=['POST'])
def api_geocode():
    """API endpoint for address geocoding"""
    data = request.json
    address = data.get('address')
    
    if not address:
        return jsonify({"error": "Missing address parameter"}), 400
    
    results = geocode_address(address)
    
    if isinstance(results, dict) and "error" in results:
        return jsonify(results), 400
    
    return jsonify({"results": results})


@app.route('/api/reverse-geocode', methods=['POST'])
def api_reverse_geocode():
    """API endpoint for reverse geocoding"""
    data = request.json
    lat = data.get('lat')
    lon = data.get('lon')
    
    if lat is None or lon is None:
        return jsonify({"error": "Missing lat or lon parameter"}), 400
    
    address = reverse_geocode(lat, lon)
    
    return jsonify({"address": address})


@app.route('/api/route', methods=['POST'])
def api_route():
    """API endpoint for route calculation"""
    data = request.json
    source_lat = data.get('source_lat')
    source_lon = data.get('source_lon')
    dest_lat = data.get('dest_lat')
    dest_lon = data.get('dest_lon')
    traffic_time = data.get('traffic_time', 'current')
    
    if None in [source_lat, source_lon, dest_lat, dest_lon]:
        return jsonify({"error": "Missing coordinate parameters"}), 400
    
    result = calculate_routes(source_lat, source_lon, dest_lat, dest_lon, traffic_time)
    
    if "error" in result:
        return jsonify(result), 400
    
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
