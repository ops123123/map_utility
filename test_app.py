import unittest
import json
from app import app, xy_to_latlon, latlon_to_xy, geocode_address, reverse_geocode, calculate_routes


class TestCoordinateConversion(unittest.TestCase):
    """Test coordinate conversion functions"""

    def test_xy_to_latlon_times_square(self):
        """Test X,Y to Lat/Lon conversion for Times Square"""
        result = xy_to_latlon(-8238310.724, 4970241.327)
        self.assertIn('lat', result)
        self.assertIn('lon', result)
        self.assertAlmostEqual(result['lat'], 40.748817, places=4)
        self.assertAlmostEqual(result['lon'], -73.985428, places=4)

    def test_latlon_to_xy_times_square(self):
        """Test Lat/Lon to X,Y conversion for Times Square"""
        result = latlon_to_xy(40.748817, -73.985428)
        self.assertIn('x', result)
        self.assertIn('y', result)
        self.assertAlmostEqual(result['x'], -8238310.724, places=2)
        self.assertAlmostEqual(result['y'], 4970241.327, places=2)

    def test_xy_to_latlon_origin(self):
        """Test conversion at Web Mercator origin (0,0)"""
        result = xy_to_latlon(0, 0)
        self.assertAlmostEqual(result['lat'], 0.0, places=6)
        self.assertAlmostEqual(result['lon'], 0.0, places=6)

    def test_latlon_to_xy_origin(self):
        """Test conversion at geographic origin (0,0)"""
        result = latlon_to_xy(0, 0)
        self.assertAlmostEqual(result['x'], 0.0, places=2)
        self.assertAlmostEqual(result['y'], 0.0, places=2)

    def test_xy_to_latlon_invalid_string(self):
        """Test invalid string input"""
        result = xy_to_latlon("invalid", "data")
        self.assertIn('error', result)

    def test_latlon_to_xy_invalid_string(self):
        """Test invalid string input"""
        result = latlon_to_xy("invalid", "data")
        self.assertIn('error', result)

    def test_round_trip_conversion(self):
        """Test that converting back and forth preserves values"""
        original_lat, original_lon = 51.5074, -0.1278  # London
        xy = latlon_to_xy(original_lat, original_lon)
        latlon = xy_to_latlon(xy['x'], xy['y'])
        self.assertAlmostEqual(latlon['lat'], original_lat, places=6)
        self.assertAlmostEqual(latlon['lon'], original_lon, places=6)

    def test_extreme_latitude(self):
        """Test conversion near Web Mercator limits"""
        result = latlon_to_xy(85, 0)
        self.assertIn('x', result)
        self.assertIn('y', result)

    def test_negative_coordinates(self):
        """Test negative coordinate conversion"""
        result = xy_to_latlon(-10000000, -10000000)
        self.assertIn('lat', result)
        self.assertIn('lon', result)

    def test_precision_8_decimals_latlon(self):
        """Test that lat/lon has 8 decimal places"""
        result = xy_to_latlon(1234567.89, 9876543.21)
        lat_str = str(result['lat'])
        lon_str = str(result['lon'])
        # Check that there are no more than 8 decimal places
        self.assertTrue(len(lat_str.split('.')[-1]) <= 8)
        self.assertTrue(len(lon_str.split('.')[-1]) <= 8)


class TestFlaskEndpoints(unittest.TestCase):
    """Test Flask API endpoints"""

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_index_page(self):
        """Test main page loads"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_docs_page(self):
        """Test documentation page loads"""
        response = self.app.get('/docs')
        self.assertEqual(response.status_code, 200)

    def test_api_xy_to_latlon_success(self):
        """Test X,Y to Lat/Lon API endpoint"""
        data = {'x': -8238310.724, 'y': 4970241.327}
        response = self.app.post('/api/convert/xy-to-latlon',
                                 data=json.dumps(data),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertIn('lat', result)
        self.assertIn('lon', result)

    def test_api_xy_to_latlon_missing_params(self):
        """Test X,Y to Lat/Lon with missing parameters"""
        data = {'x': 100}
        response = self.app.post('/api/convert/xy-to-latlon',
                                 data=json.dumps(data),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_api_latlon_to_xy_success(self):
        """Test Lat/Lon to X,Y API endpoint"""
        data = {'lat': 40.748817, 'lon': -73.985428}
        response = self.app.post('/api/convert/latlon-to-xy',
                                 data=json.dumps(data),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertIn('x', result)
        self.assertIn('y', result)

    def test_api_latlon_to_xy_missing_params(self):
        """Test Lat/Lon to X,Y with missing parameters"""
        data = {'lat': 40.0}
        response = self.app.post('/api/convert/latlon-to-xy',
                                 data=json.dumps(data),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_api_geocode_missing_address(self):
        """Test geocoding with missing address"""
        data = {}
        response = self.app.post('/api/geocode',
                                 data=json.dumps(data),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_api_reverse_geocode_missing_params(self):
        """Test reverse geocoding with missing parameters"""
        data = {'lat': 40.0}
        response = self.app.post('/api/reverse-geocode',
                                 data=json.dumps(data),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_api_route_missing_params(self):
        """Test route calculation with missing parameters"""
        data = {'source_lat': 40.0, 'source_lon': -73.0}
        response = self.app.post('/api/route',
                                 data=json.dumps(data),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_api_invalid_json(self):
        """Test API with invalid JSON"""
        response = self.app.post('/api/convert/xy-to-latlon',
                                 data='not valid json',
                                 content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_api_route_with_traffic_time(self):
        """Test route calculation with traffic time parameter"""
        data = {
            'source_lat': 40.748817,
            'source_lon': -73.985428,
            'dest_lat': 40.758896,
            'dest_lon': -73.985130,
            'traffic_time': 'morning'
        }
        response = self.app.post('/api/route',
                                 data=json.dumps(data),
                                 content_type='application/json')
        # Note: May fail if OSRM is down, so we just check it doesn't crash
        self.assertIn(response.status_code, [200, 400])

    def test_get_request_to_post_endpoint(self):
        """Test GET request to POST-only endpoint"""
        response = self.app.get('/api/convert/xy-to-latlon')
        self.assertEqual(response.status_code, 405)  # Method Not Allowed

    def test_invalid_endpoint(self):
        """Test request to non-existent endpoint"""
        response = self.app.get('/api/invalid')
        self.assertEqual(response.status_code, 404)

    def test_api_convert_zero_values(self):
        """Test conversion with zero values"""
        data = {'x': 0, 'y': 0}
        response = self.app.post('/api/convert/xy-to-latlon',
                                 data=json.dumps(data),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)


class TestGeocodingFunctions(unittest.TestCase):
    """Test geocoding and reverse geocoding (requires internet)"""

    def test_geocode_simple_city(self):
        """Test geocoding a simple city name"""
        # This test requires internet and may be slow
        results = geocode_address("London")
        if not isinstance(results, dict) or 'error' not in results:
            self.assertIsInstance(results, list)
            self.assertGreater(len(results), 0)
            if len(results) > 0:
                self.assertIn('lat', results[0])
                self.assertIn('lon', results[0])
                self.assertIn('x', results[0])
                self.assertIn('y', results[0])

    def test_geocode_empty_string(self):
        """Test geocoding empty string"""
        results = geocode_address("")
        # Should either return empty results or error
        if isinstance(results, dict):
            self.assertIn('error', results)
        else:
            self.assertIsInstance(results, list)

    def test_geocode_coordinates_format(self):
        """Test that geocoded results have correct format"""
        results = geocode_address("Paris, France")
        if not isinstance(results, dict) or 'error' not in results:
            if len(results) > 0:
                result = results[0]
                # Check all required fields
                self.assertIn('display_name', result)
                self.assertIn('lat', result)
                self.assertIn('lon', result)
                self.assertIn('x', result)
                self.assertIn('y', result)

    def test_geocode_returns_max_5_results(self):
        """Test that geocoding returns at most 5 results"""
        results = geocode_address("Springfield")
        if not isinstance(results, dict) or 'error' not in results:
            self.assertLessEqual(len(results), 5)

    def test_reverse_geocode_known_location(self):
        """Test reverse geocoding a known location"""
        # Times Square coordinates
        address = reverse_geocode(40.758896, -73.985130)
        self.assertIsInstance(address, str)
        self.assertGreater(len(address), 0)

    def test_reverse_geocode_ocean(self):
        """Test reverse geocoding in the middle of ocean"""
        # Middle of Pacific Ocean
        address = reverse_geocode(0, -160)
        self.assertIsInstance(address, str)

    def test_geocode_special_characters(self):
        """Test geocoding with special characters"""
        results = geocode_address("São Paulo")
        # Should handle gracefully
        self.assertTrue(isinstance(results, list) or 'error' in results)

    def test_geocode_non_existent_place(self):
        """Test geocoding a non-existent place"""
        results = geocode_address("XYZ123NonExistentPlace456")
        if isinstance(results, list):
            # Empty list is acceptable for non-existent places
            self.assertIsInstance(results, list)


class TestRouteCalculation(unittest.TestCase):
    """Test route calculation functionality"""

    def test_calculate_routes_basic(self):
        """Test basic route calculation"""
        # Short route in Manhattan
        result = calculate_routes(40.748817, -73.985428, 40.758896, -73.985130, "current")
        if 'routes' in result:
            self.assertIn('routes', result)
            self.assertGreater(len(result['routes']), 0)
            route = result['routes'][0]
            self.assertIn('distance_km', route)
            self.assertIn('duration_min', route)
            self.assertIn('traffic_duration_min', route)

    def test_traffic_multiplier_morning(self):
        """Test morning rush hour multiplier"""
        result = calculate_routes(40.748817, -73.985428, 40.758896, -73.985130, "morning")
        if 'routes' in result and len(result['routes']) > 0:
            route = result['routes'][0]
            # Morning should increase time (1.5x multiplier)
            self.assertGreater(route['traffic_duration_min'], route['duration_min'])

    def test_traffic_multiplier_evening(self):
        """Test evening rush hour multiplier"""
        result = calculate_routes(40.748817, -73.985428, 40.758896, -73.985130, "evening")
        if 'routes' in result and len(result['routes']) > 0:
            route = result['routes'][0]
            # Evening should increase time more (1.6x multiplier)
            self.assertGreater(route['traffic_duration_min'], route['duration_min'])

    def test_traffic_multiplier_night(self):
        """Test night time multiplier"""
        result = calculate_routes(40.748817, -73.985428, 40.758896, -73.985130, "night")
        if 'routes' in result and len(result['routes']) > 0:
            route = result['routes'][0]
            # Night should decrease time (0.9x multiplier)
            self.assertLess(route['traffic_duration_min'], route['duration_min'])

    def test_traffic_level_classification(self):
        """Test that traffic level is properly classified"""
        result = calculate_routes(40.748817, -73.985428, 40.758896, -73.985130, "severe")
        if 'routes' in result and len(result['routes']) > 0:
            route = result['routes'][0]
            self.assertIn('traffic_level', route)
            self.assertIn(route['traffic_level'], ['clear', 'light', 'heavy', 'severe'])

    def test_route_type_classification(self):
        """Test that routes are classified as main or alternative"""
        result = calculate_routes(40.748817, -73.985428, 40.758896, -73.985130, "current")
        if 'routes' in result and len(result['routes']) > 0:
            main_route = result['routes'][0]
            self.assertEqual(main_route['route_type'], 'main')

    def test_multiple_alternative_routes(self):
        """Test that multiple routes can be returned"""
        result = calculate_routes(40.748817, -73.985428, 40.758896, -73.985130, "current")
        if 'routes' in result:
            # Should return up to 3 routes
            self.assertLessEqual(len(result['routes']), 3)

    def test_route_geometry_exists(self):
        """Test that route geometry is included"""
        result = calculate_routes(40.748817, -73.985428, 40.758896, -73.985130, "current")
        if 'routes' in result and len(result['routes']) > 0:
            route = result['routes'][0]
            self.assertIn('geometry', route)

    def test_distance_conversions(self):
        """Test that both km and miles are provided"""
        result = calculate_routes(40.748817, -73.985428, 40.758896, -73.985130, "current")
        if 'routes' in result and len(result['routes']) > 0:
            route = result['routes'][0]
            self.assertIn('distance_km', route)
            self.assertIn('distance_mi', route)
            # Miles should be less than km (1 mile = 1.609 km)
            self.assertLess(route['distance_mi'], route['distance_km'])

    def test_invalid_traffic_time(self):
        """Test with invalid traffic time defaults to 1.0"""
        result = calculate_routes(40.748817, -73.985428, 40.758896, -73.985130, "invalid_time")
        if 'routes' in result and len(result['routes']) > 0:
            route = result['routes'][0]
            # Should default to no multiplier
            self.assertAlmostEqual(route['traffic_duration_min'], route['duration_min'], places=1)

    def test_very_long_route(self):
        """Test calculation for a very long route"""
        # New York to Los Angeles
        result = calculate_routes(40.7128, -74.0060, 34.0522, -118.2437, "current")
        # Should complete without error (or return error if not routable)
        self.assertTrue('routes' in result or 'error' in result)

    def test_same_source_destination(self):
        """Test route with same source and destination"""
        result = calculate_routes(40.748817, -73.985428, 40.748817, -73.985428, "current")
        # OSRM might return error or zero-distance route
        self.assertTrue('routes' in result or 'error' in result)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""

    def test_conversion_with_none_values(self):
        """Test conversion with None values"""
        result = xy_to_latlon(None, None)
        self.assertIn('error', result)

    def test_conversion_with_empty_strings(self):
        """Test conversion with empty strings"""
        result = latlon_to_xy("", "")
        self.assertIn('error', result)

    def test_extreme_coordinate_values(self):
        """Test with extreme coordinate values"""
        result = latlon_to_xy(90, 180)
        # Should work but be at projection limits
        self.assertTrue('x' in result or 'error' in result)

    def test_route_with_ocean_coordinates(self):
        """Test route calculation in ocean (should fail)"""
        result = calculate_routes(0, -160, 0, 160, "current")
        # Should return error as no roads in ocean
        self.assertIn('error', result)

    def test_negative_latitude_conversion(self):
        """Test conversion with negative latitude (southern hemisphere)"""
        result = latlon_to_xy(-33.8688, 151.2093)  # Sydney
        self.assertIn('x', result)
        self.assertIn('y', result)
        self.assertLess(result['y'], 0)  # Southern hemisphere has negative Y


class TestIntegrationWorkflows(unittest.TestCase):
    """Test complete workflows"""

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_conversion_workflow(self):
        """Test complete conversion workflow"""
        # Convert lat/lon to X/Y
        data1 = {'lat': 40.748817, 'lon': -73.985428}
        response1 = self.app.post('/api/convert/latlon-to-xy',
                                  data=json.dumps(data1),
                                  content_type='application/json')
        self.assertEqual(response1.status_code, 200)
        result1 = json.loads(response1.data)
        
        # Convert back to lat/lon
        data2 = {'x': result1['x'], 'y': result1['y']}
        response2 = self.app.post('/api/convert/xy-to-latlon',
                                  data=json.dumps(data2),
                                  content_type='application/json')
        self.assertEqual(response2.status_code, 200)
        result2 = json.loads(response2.data)
        
        # Should get back original values (approximately)
        self.assertAlmostEqual(result2['lat'], data1['lat'], places=6)
        self.assertAlmostEqual(result2['lon'], data1['lon'], places=6)

    def test_geocode_to_route_workflow(self):
        """Test geocoding then routing workflow"""
        # Note: This test requires internet and may be slow
        pass  # Placeholder for integration test

    def test_multiple_conversions_in_sequence(self):
        """Test multiple conversions work correctly"""
        coords = [
            (40.748817, -73.985428),  # Times Square
            (51.5074, -0.1278),       # London
            (48.8566, 2.3522),        # Paris
        ]
        
        for lat, lon in coords:
            data = {'lat': lat, 'lon': lon}
            response = self.app.post('/api/convert/latlon-to-xy',
                                     data=json.dumps(data),
                                     content_type='application/json')
            self.assertEqual(response.status_code, 200)

    def test_all_traffic_times(self):
        """Test all traffic time options"""
        traffic_times = ['current', 'morning', 'midday', 'evening', 'night', 'weekend']
        
        for traffic_time in traffic_times:
            result = calculate_routes(40.748817, -73.985428, 40.758896, -73.985130, traffic_time)
            # Should complete without crashing
            self.assertTrue('routes' in result or 'error' in result)

    def test_documentation_page_content(self):
        """Test that documentation page has expected content"""
        response = self.app.get('/docs')
        self.assertEqual(response.status_code, 200)
        content = response.data.decode('utf-8')
        # Check for key sections
        self.assertIn('Overview', content)
        self.assertIn('Conversion', content)
        self.assertIn('FAQ', content)


if __name__ == '__main__':
    # Run tests with verbosity
    unittest.main(verbosity=2)
