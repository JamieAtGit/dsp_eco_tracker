#!/usr/bin/env python3
"""
Test NXT Nutrition product through the API
"""

import requests
import json

def test_nxt_api():
    """Test the NXT Nutrition product through the API"""
    
    print("🌐 Testing NXT Nutrition Product via API")
    print("=" * 60)
    
    url = "http://localhost:5000/estimate_emissions"
    data = {
        "amazon_url": "https://www.amazon.co.uk/Nutrition-Beef-Protein-Isolate-1-8kg/dp/B07MCMTJWC/",
        "postcode": "SW1A 1AA",
        "include_packaging": True
    }
    
    try:
        response = requests.post(url, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            if 'data' in result and 'attributes' in result['data']:
                attrs = result['data']['attributes']
                
                origin = attrs.get('origin', 'Unknown')
                origin_distance = attrs.get('distance_from_origin_km', 0)
                uk_distance = attrs.get('distance_from_uk_hub_km', 0)
                transport_mode = attrs.get('transport_mode', 'Unknown')
                carbon_kg = attrs.get('carbon_kg', 0)
                
                print(f"📍 Origin: {origin}")
                print(f"📏 Origin distance: {origin_distance} km")
                print(f"🇬🇧 UK hub distance: {uk_distance} km")
                print(f"🚚 Transport mode: {transport_mode}")
                print(f"💨 Carbon emissions: {carbon_kg} kg CO₂")
                
                print("\n🔍 VALIDATION:")
                print("-" * 40)
                
                if origin == 'UK':
                    print("✅ Origin: CORRECT (UK detected)")
                else:
                    print(f"❌ Origin: WRONG (got {origin}, expected UK)")
                
                if origin_distance < 100:  # UK should be very close
                    print(f"✅ Distance: REASONABLE for UK ({origin_distance} km)")
                else:
                    print(f"❌ Distance: TOO HIGH for UK ({origin_distance} km)")
                    
                if transport_mode in ['Truck', 'truck']:
                    print("✅ Transport: CORRECT (truck for UK)")
                else:
                    print(f"⚠️  Transport: {transport_mode} (may be correct)")
                    
                if carbon_kg < 1.0:  # UK should have low emissions
                    print(f"✅ Emissions: LOW for UK product ({carbon_kg} kg CO₂)")
                else:
                    print(f"⚠️  Emissions: {carbon_kg} kg CO₂ (check if reasonable)")
                    
            else:
                print("❌ Unexpected API response structure")
                print(json.dumps(result, indent=2))
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API (is Flask running on localhost:5000?)")
    except Exception as e:
        print(f"❌ API test failed: {e}")

if __name__ == "__main__":
    test_nxt_api()