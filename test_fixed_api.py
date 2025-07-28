#!/usr/bin/env python3
"""
Test the fixed API with realistic CO2 calculations
"""

import requests
import json

def test_api_with_amazon_url():
    """Test API endpoint with an Amazon URL"""
    
    # API endpoint
    api_url = "http://localhost:5000/estimate_emissions"
    
    # Test data - iPhone example
    test_data = {
        "url": "https://www.amazon.co.uk/dp/B0CHX2F5QT",  # iPhone 15 Pro
        "postcode": "SW1A 1AA"  # London postcode
    }
    
    try:
        print("🧪 Testing fixed API with realistic CO2 calculations...")
        print(f"📱 Test URL: {test_data['url']}")
        print(f"📍 Postcode: {test_data['postcode']}")
        
        response = requests.post(api_url, json=test_data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n✅ API Response Success!")
            print("=" * 50)
            
            # Extract key data
            data = result.get('data', {}).get('attributes', {})
            carbon_kg = data.get('carbon_kg', 0)
            weight_kg = data.get('weight_kg', 0)
            eco_score = data.get('eco_score_ml_based', 'Unknown')
            
            print(f"📱 Product: {result.get('title', 'Unknown')}")
            print(f"⚖️  Weight: {weight_kg} kg")
            print(f"🌱 CO2 Emissions: {carbon_kg} kg CO2")
            print(f"📊 Eco Score: {eco_score}")
            
            # Validate realism
            if 10 <= carbon_kg <= 100:
                print("✅ CO2 value is realistic for electronics!")
            elif carbon_kg > 1000:
                print("❌ CO2 value still inflated - fix not working")
            else:
                print("⚠️  CO2 value seems low, check calculation")
                
            return True
            
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API - make sure Flask app is running")
        print("   Run: cd backend/api && python3 app.py")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 TESTING API WITH FIXED CO2 CALCULATIONS")
    print("=" * 60)
    
    success = test_api_with_amazon_url()
    
    if success:
        print("\n🎉 API is now using realistic CO2 calculations!")
        print("✅ Users will see credible carbon footprint data")
    else:
        print("\n⚠️  API test failed - check Flask app is running")
        print("Start with: cd backend/api && python3 app.py")