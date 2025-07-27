#!/usr/bin/env python3
"""
Test the API endpoint to see what's causing the 500 error
"""
import requests
import json

# Test URLs
api_urls = {
    "local": "http://localhost:5000",
    "railway": "https://web-production-a62d7.up.railway.app"
}

def test_health(base_url):
    """Test if the API is running"""
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"✅ Health check: {response.status_code}")
        if response.ok:
            print(f"   Response: {response.json()}")
        return response.ok
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_estimate_emissions(base_url):
    """Test the estimate_emissions endpoint"""
    test_data = {
        "amazon_url": "https://www.amazon.com/dp/B000P0ZSHK",
        "postcode": "SW1A 1AA"
    }
    
    try:
        print(f"\n🔍 Testing {base_url}/estimate_emissions")
        print(f"   Payload: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(
            f"{base_url}/estimate_emissions",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.ok:
            data = response.json()
            print("   ✅ Success! Response structure:")
            print(f"   - Title: {data.get('title', 'N/A')}")
            print(f"   - Has data.attributes: {'attributes' in data.get('data', {})}")
            print(f"   - Has materials: {'materials' in data.get('data', {}).get('attributes', {})}")
            
            # Check materials data
            materials = data.get('data', {}).get('attributes', {}).get('materials', {})
            if materials:
                print(f"   - Materials tier: {materials.get('tier', 'N/A')}")
                print(f"   - Primary material: {materials.get('primary_material', 'N/A')}")
        else:
            print(f"   ❌ Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error message: {error_data}")
            except:
                print(f"   Error text: {response.text[:200]}...")
                
    except Exception as e:
        print(f"   ❌ Request failed: {e}")

def main():
    print("🧪 TESTING API ENDPOINTS")
    print("=" * 50)
    
    # Test Railway (production)
    print("\n📡 Testing Railway API...")
    base_url = api_urls["railway"]
    if test_health(base_url):
        test_estimate_emissions(base_url)
    else:
        print("⚠️  Railway API is not responding to health checks")
    
    print("\n" + "=" * 50)
    print("💡 If you see 500 errors, check Railway logs for the actual error")
    print("   The backend might be missing dependencies or environment variables")

if __name__ == "__main__":
    main()