#!/usr/bin/env python3
"""
Test dual origin system through the API
"""

import requests
import json

def test_dual_origin_api():
    """Test dual origin system via API"""
    
    print("🌐 Testing Dual Origin System via API")
    print("=" * 60)
    
    # Test with a product that should show facility information
    url = "http://localhost:5000/estimate_emissions"
    
    # Use the NXT Nutrition product which we know works
    data = {
        "amazon_url": "https://www.amazon.co.uk/Nutrition-Beef-Protein-Isolate-1-8kg/dp/B07MCMTJWC/",
        "postcode": "SW1A 1AA",
        "include_packaging": True
    }
    
    try:
        print(f"🔍 Testing URL: {data['amazon_url']}")
        response = requests.post(url, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            if 'data' in result and 'attributes' in result['data']:
                attrs = result['data']['attributes']
                
                # Extract dual origin information
                origin = attrs.get('origin', 'Unknown')
                country_of_origin = attrs.get('country_of_origin', 'Unknown')
                facility_origin = attrs.get('facility_origin', 'Unknown')
                
                print("\n🔍 DUAL ORIGIN RESULTS:")
                print("-" * 40)
                print(f"Legacy Origin:       {origin}")
                print(f"Country of Origin:   {country_of_origin}")
                print(f"Facility Origin:     {facility_origin}")
                
                # Distance calculations
                origin_distance = attrs.get('distance_from_origin_km', 0)
                uk_distance = attrs.get('distance_from_uk_hub_km', 0)
                transport_mode = attrs.get('transport_mode', 'Unknown')
                
                print(f"\n📏 DISTANCE CALCULATIONS:")
                print("-" * 40)
                print(f"Origin Distance:     {origin_distance} km")
                print(f"UK Hub Distance:     {uk_distance} km")
                print(f"Transport Mode:      {transport_mode}")
                
                print(f"\n✅ VALIDATION:")
                print("-" * 40)
                
                if country_of_origin != 'Unknown':
                    print("✅ Country of Origin: Detected for distance calculation")
                else:
                    print("❌ Country of Origin: Not detected")
                    
                if facility_origin != 'Unknown':
                    print(f"✅ Facility Origin: Detailed info captured ({facility_origin})")
                else:
                    print("⚠️  Facility Origin: No detailed facility info")
                
                if origin_distance > 0:
                    print(f"✅ Distance Calc: Working ({origin_distance} km)")
                else:
                    print("❌ Distance Calc: Failed")
                    
                # Show full response for debugging
                print(f"\n📊 Key API Response Fields:")
                print("-" * 40)
                for key in ['origin', 'country_of_origin', 'facility_origin', 'distance_from_origin_km']:
                    if key in attrs:
                        print(f"{key:25}: {attrs[key]}")
                        
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
    test_dual_origin_api()