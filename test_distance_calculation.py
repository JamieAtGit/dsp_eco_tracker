#!/usr/bin/env python3
"""
Test distance calculation for South Africa
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

def test_distance_calculation():
    """Test the exact distance calculation logic"""
    
    # Import the functions
    from backend.scrapers.amazon.scrape_amazon_titles import haversine, origin_hubs, uk_hub
    import pgeocode
    
    print("🧪 Testing Distance Calculation")
    print("=" * 50)
    
    # Test postcode to coordinates conversion
    postcode = "SW1A 1AA"  # Westminster, London
    geo = pgeocode.Nominatim("gb")
    location = geo.query_postal_code(postcode)
    
    if location.empty or location.latitude is None:
        print(f"❌ Invalid postcode: {postcode}")
        return
    
    user_lat, user_lon = location.latitude, location.longitude
    print(f"📍 User location ({postcode}): {user_lat:.4f}, {user_lon:.4f}")
    
    # Test South Africa coordinates
    if "South Africa" in origin_hubs:
        sa_coords = origin_hubs["South Africa"]
        print(f"🇿🇦 South Africa: {sa_coords}")
        
        # Calculate distance
        distance_km = haversine(sa_coords["lat"], sa_coords["lon"], user_lat, user_lon)
        print(f"📏 Distance to South Africa: {distance_km:.1f} km")
        
        # Expected distance: London to Johannesburg is approximately 8,960 km
        if 8500 <= distance_km <= 9500:
            print("✅ Distance is accurate (expected ~8,960 km)")
        else:
            print(f"⚠️  Distance seems off (expected ~8,960 km, got {distance_km:.1f} km)")
            
        # Test transport mode determination
        if distance_km < 1500:
            transport = "truck"
        elif distance_km < 6000:
            transport = "ship" 
        else:
            transport = "air"
            
        print(f"✈️  Transport mode: {transport}")
        
        if transport == "air":
            print("✅ Correct transport mode for South Africa")
        else:
            print(f"❌ Wrong transport mode (should be 'air', got '{transport}')")
            
    else:
        print("❌ South Africa not found in origin_hubs")
    
    # Test UK hub distance (should be very small)
    uk_distance = haversine(uk_hub["lat"], uk_hub["lon"], user_lat, user_lon)
    print(f"🇬🇧 Distance to UK hub: {uk_distance:.1f} km")
    
    if uk_distance < 100:
        print("✅ UK hub distance is reasonable")
    else:
        print(f"⚠️  UK hub distance seems high: {uk_distance:.1f} km")

def test_api_endpoint():
    """Test the actual API endpoint"""
    import requests
    import json
    
    print("\n🌐 Testing API Endpoint")
    print("=" * 50)
    
    # Test the API endpoint
    url = "http://localhost:5000/estimate_emissions"
    data = {
        "amazon_url": "https://www.amazon.co.uk/USN-Protein-Powder-Chocolate-Flavour/dp/B0DG5V9BWQ/",
        "postcode": "SW1A 1AA",
        "include_packaging": True
    }
    
    try:
        response = requests.post(url, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            if 'data' in result and 'attributes' in result['data']:
                attrs = result['data']['attributes']
                origin_distance = attrs.get('distance_from_origin_km', 0)
                uk_distance = attrs.get('distance_from_uk_hub_km', 0)
                
                print(f"📏 Origin distance: {origin_distance} km")
                print(f"🇬🇧 UK hub distance: {uk_distance} km")
                
                if origin_distance > 8000:
                    print("✅ API returns correct South Africa distance")
                else:
                    print(f"❌ API distance still wrong: {origin_distance} km (should be ~9000km)")
                    
                # Print full response for debugging
                print(f"\n📊 Full API Response:")
                print(json.dumps(result, indent=2))
            else:
                print("❌ Unexpected API response structure")
                print(response.text)
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API (is Flask running on localhost:5000?)")
    except Exception as e:
        print(f"❌ API test failed: {e}")

if __name__ == "__main__":
    test_distance_calculation()
    test_api_endpoint()