#!/usr/bin/env python3
"""
🔍 DEBUG WHOLE SUPP PRODUCT EXTRACTION
====================================

Debug the specific product that's showing incorrect data:
- Weight: 0.03kg (should be ~1kg)
- Origin: Unknown (should be detected)
- Carbon: 0 kg CO₂ (should be calculated)
"""

import sys
import os

# Add project root to path
project_root = os.path.abspath('.')
sys.path.insert(0, project_root)

def debug_whole_supp_product():
    """Debug the Whole Supp product extraction"""
    
    url = "https://www.amazon.co.uk/Whole-Supp-Replacement-Gluten-Free-Superfoods/dp/B0F38V95VR/"
    
    print("🔍 DEBUGGING WHOLE SUPP PRODUCT")
    print("=" * 50)
    print(f"URL: {url}")
    
    try:
        # Import the enhanced scraper
        from enhanced_scraper_fix import EnhancedAmazonScraper
        
        scraper = EnhancedAmazonScraper()
        result = scraper.scrape_product_enhanced(url)
        
        print(f"\n📊 SCRAPER RESULTS:")
        print("-" * 30)
        
        if result:
            for key, value in result.items():
                print(f"{key:20}: {value}")
        else:
            print("❌ No result returned")
            
        # Test specific extraction methods
        print(f"\n🔬 DETAILED EXTRACTION ANALYSIS:")
        print("-" * 40)
        
        # Try to get the page content for analysis
        import requests
        import time
        from bs4 import BeautifulSoup
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        time.sleep(2)  # Be respectful
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Check for title
            title_elem = soup.find('span', {'id': 'productTitle'})
            if title_elem:
                title = title_elem.get_text().strip()
                print(f"Title found: {title[:100]}...")
            else:
                print("❌ Title not found")
            
            # Check for weight in text
            all_text = soup.get_text()
            weight_indicators = ['1kg', '1000g', '900g', 'kg', 'gram']
            found_weights = []
            for indicator in weight_indicators:
                if indicator.lower() in all_text.lower():
                    # Find context around weight
                    pos = all_text.lower().find(indicator.lower())
                    if pos > 0:
                        context_start = max(0, pos - 50)
                        context_end = min(len(all_text), pos + 50)
                        context = all_text[context_start:context_end].replace('\n', ' ')
                        found_weights.append(f"{indicator}: {context}")
            
            print(f"\n⚖️ WEIGHT ANALYSIS:")
            if found_weights:
                for weight_context in found_weights[:3]:  # Show first 3
                    print(f"  {weight_context}")
            else:
                print("  ❌ No weight indicators found")
            
            # Check for origin indicators
            origin_indicators = ['made in', 'origin', 'country', 'manufactured', 'uk', 'england']
            found_origins = []
            for indicator in origin_indicators:
                if indicator.lower() in all_text.lower():
                    pos = all_text.lower().find(indicator.lower())
                    if pos > 0:
                        context_start = max(0, pos - 50)
                        context_end = min(len(all_text), pos + 50)
                        context = all_text[context_start:context_end].replace('\n', ' ')
                        found_origins.append(f"{indicator}: {context}")
            
            print(f"\n🌍 ORIGIN ANALYSIS:")
            if found_origins:
                for origin_context in found_origins[:3]:  # Show first 3
                    print(f"  {origin_context}")
            else:
                print("  ❌ No origin indicators found")
                
        else:
            print(f"❌ Failed to fetch page: {response.status_code}")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Enhanced scraper not available")
    except Exception as e:
        print(f"❌ Error: {e}")
        
    # Test the API call
    print(f"\n🌐 API TEST:")
    print("-" * 30)
    
    try:
        import requests
        import json
        
        api_data = {
            "amazon_url": url,
            "postcode": "SW1A 1AA",
            "include_packaging": True
        }
        
        api_response = requests.post(
            "http://localhost:5000/estimate_emissions", 
            json=api_data, 
            timeout=30
        )
        
        if api_response.status_code == 200:
            api_result = api_response.json()
            if 'data' in api_result and 'attributes' in api_result['data']:
                attrs = api_result['data']['attributes']
                print(f"API Weight: {attrs.get('weight_kg', 'Unknown')}")
                print(f"API Origin: {attrs.get('origin', 'Unknown')}")
                print(f"API Country: {attrs.get('country_of_origin', 'Unknown')}")
                print(f"API Carbon: {attrs.get('carbon_kg', 'Unknown')}")
                print(f"API Distance: {attrs.get('distance_from_origin_km', 'Unknown')}")
            else:
                print("❌ Unexpected API response structure")
        else:
            print(f"❌ API call failed: {api_response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ API not running (start with: python backend/api/app.py)")
    except Exception as e:
        print(f"❌ API test failed: {e}")

if __name__ == "__main__":
    debug_whole_supp_product()