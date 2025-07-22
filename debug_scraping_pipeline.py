#!/usr/bin/env python3
"""
🔍 SCRAPING PIPELINE DEBUGGER
============================

Emergency diagnostic tool to identify why scraping is returning
zero/unknown values instead of actual product data.

This will trace through the entire pipeline to find the failure point.
"""

import sys
import os

# Add project paths
project_root = os.path.abspath('.')
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'backend'))
sys.path.insert(0, os.path.join(project_root, 'backend', 'scrapers', 'amazon'))

def debug_scraping_pipeline(test_url: str = None):
    """Debug the entire scraping pipeline step by step"""
    
    if not test_url:
        test_url = "https://www.amazon.co.uk/Grenade-Protein-Powder-Serving-Servings/dp/B0CKFK6716"
    
    print("🔍 EMERGENCY SCRAPING PIPELINE DIAGNOSTIC")
    print("=" * 60)
    print(f"📍 Testing URL: {test_url}")
    print("=" * 60)
    
    # STEP 1: Test unified scraper directly
    print("\n🧪 STEP 1: Testing Unified Scraper")
    print("-" * 40)
    
    try:
        from backend.scrapers.amazon.unified_scraper import UnifiedProductScraper
        
        scraper = UnifiedProductScraper()
        result = scraper.scrape(test_url)
        
        print(f"✅ Unified Scraper Result:")
        print(f"   Title: {result.title}")
        print(f"   Origin: {result.origin}")
        print(f"   Weight: {result.weight_kg} kg")
        print(f"   Material: {result.material_type}")
        print(f"   Quality Score: {result.quality_score}%")
        print(f"   Strategy Used: {result.strategy_used}")
        print(f"   Confidence: {result.confidence_level}")
        
    except Exception as e:
        print(f"❌ Unified Scraper Error: {e}")
    
    # STEP 2: Test requests scraper directly
    print("\n🌐 STEP 2: Testing Requests Scraper")
    print("-" * 40)
    
    try:
        from backend.scrapers.amazon.requests_scraper import scrape_with_requests
        
        result = scrape_with_requests(test_url)
        
        if result:
            print(f"✅ Requests Scraper Result:")
            print(f"   Title: {result.get('title', 'N/A')}")
            print(f"   Origin: {result.get('origin', 'N/A')}")
            print(f"   Weight: {result.get('weight_kg', 'N/A')} kg")
            print(f"   Material: {result.get('material_type', 'N/A')}")
            print(f"   Brand: {result.get('brand', 'N/A')}")
            print(f"   Method: {result.get('method', 'N/A')}")
        else:
            print("❌ Requests scraper returned None")
            
    except Exception as e:
        print(f"❌ Requests Scraper Error: {e}")
    
    # STEP 3: Test API endpoint 
    print("\n🔗 STEP 3: Testing API Endpoint")
    print("-" * 40)
    
    try:
        # Try to import and test the API directly
        from backend.api.app import app
        
        with app.test_client() as client:
            # Test the main estimation endpoint
            response = client.post('/estimate_emissions', json={
                'amazon_url': test_url,
                'postcode': 'SW1A 1AA'  # Test postcode
            })
            
            print(f"✅ API Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.get_json()
                print(f"   Scraped Weight: {data.get('scraped_data', {}).get('weight_kg', 'N/A')} kg")
                print(f"   Scraped Origin: {data.get('scraped_data', {}).get('origin', 'N/A')}")
                print(f"   Carbon Prediction: {data.get('carbon_prediction', 'N/A')} kg CO₂")
                print(f"   Distance: {data.get('distance_km', 'N/A')} km")
            else:
                print(f"❌ API Error Response: {response.get_data(as_text=True)}")
                
    except Exception as e:
        print(f"❌ API Test Error: {e}")
    
    # STEP 4: Test the original scraper being used by API
    print("\n📜 STEP 4: Testing Original API Scraper")  
    print("-" * 40)
    
    try:
        from backend.scrapers.amazon.scrape_amazon_titles import scrape_amazon_product_page
        
        result = scrape_amazon_product_page(test_url, fallback=False)
        
        if result:
            print(f"✅ Original Scraper Result:")
            print(f"   Title: {result.get('title', 'N/A')}")
            print(f"   Origin: {result.get('origin', 'N/A')}")
            print(f"   Weight: {result.get('weight_kg', 'N/A')} kg")
            print(f"   Material: {result.get('material_type', 'N/A')}")
        else:
            print("❌ Original scraper returned None")
            
    except Exception as e:
        print(f"❌ Original Scraper Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 DIAGNOSIS COMPLETE")
    print("=" * 60)
    
    print("""
🔧 NEXT STEPS TO FIX:
1. Check which scraper the API is actually using
2. Update API to use the new unified scraper
3. Ensure proper error handling and fallbacks
4. Test with real product URLs
5. Verify data pipeline from scraping → ML → frontend
    """)

if __name__ == "__main__":
    debug_scraping_pipeline()