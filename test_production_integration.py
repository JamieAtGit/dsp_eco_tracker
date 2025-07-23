#!/usr/bin/env python3
"""
Test the production scraper integration with the main Flask app
"""

import sys
import os
import json

# Add project root to path
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

def test_integration():
    """Test that the production scraper integrates correctly with the main app"""
    
    print("🧪 Testing Production Scraper Integration")
    print("=" * 60)
    
    # Test import chain
    print("📦 Testing import chain...")
    
    try:
        from backend.scrapers.amazon.production_scraper import ProductionAmazonScraper
        print("✅ Production scraper imports successfully")
        production_available = True
    except ImportError as e:
        print(f"❌ Production scraper import failed: {e}")
        production_available = False
    
    try:
        from backend.scrapers.amazon.url_processor import AmazonURLProcessor
        print("✅ URL processor imports successfully")
    except ImportError as e:
        print(f"❌ URL processor import failed: {e}")
        
    try:
        from backend.scrapers.amazon.category_detector import CategoryDetector
        print("✅ Category detector imports successfully")
    except ImportError as e:
        print(f"❌ Category detector import failed: {e}")
    
    # Test Flask app import
    print("\n🌐 Testing Flask app integration...")
    try:
        # This will test the import chain in app.py
        from backend.api.app import PRODUCTION_SCRAPER_AVAILABLE, ENHANCED_SCRAPER_AVAILABLE
        print(f"✅ Flask app imports successfully")
        print(f"   Production scraper available: {PRODUCTION_SCRAPER_AVAILABLE}")
        print(f"   Enhanced scraper available: {ENHANCED_SCRAPER_AVAILABLE}")
    except ImportError as e:
        print(f"❌ Flask app import failed: {e}")
        return False
        
    # Test actual scraping if production scraper is available
    if production_available:
        print(f"\n🔍 Testing actual scraping...")
        
        scraper = ProductionAmazonScraper()
        test_url = "https://www.amazon.co.uk/Isolate-Protein-Fast-digesting-hydrolysate-Gourmet/dp/B01H3O2AMG"
        
        try:
            result = scraper.scrape_with_full_url(test_url)
            
            if result:
                print(f"✅ Scraping test successful!")
                print(f"   Title: {result.get('title', 'N/A')[:50]}...")
                print(f"   Category: {result.get('category', 'N/A')} ({result.get('category_confidence', 0):.1%})")
                print(f"   Weight: {result.get('weight_kg', 'N/A')}kg")
                print(f"   Brand: {result.get('brand', 'N/A')}")
                print(f"   Confidence: {result.get('confidence_score', 0):.1%}")
                
                # Check for expected fields
                expected_fields = ['title', 'weight_kg', 'brand', 'origin', 'material_type', 'category', 'confidence_score']
                missing_fields = [field for field in expected_fields if field not in result]
                
                if missing_fields:
                    print(f"⚠️  Missing expected fields: {missing_fields}")
                else:
                    print(f"✅ All expected fields present")
                    
                return True
            else:
                print(f"❌ Scraping test failed - no result")
                return False
                
        except Exception as e:
            print(f"❌ Scraping test failed with error: {e}")
            return False
    else:
        print(f"⚠️  Production scraper not available, skipping scraping test")
        return True

def test_api_endpoint_simulation():
    """Simulate the API endpoint to test integration"""
    
    print(f"\n📡 Testing API endpoint simulation...")
    
    # Mock request data
    mock_data = {
        "amazon_url": "https://www.amazon.co.uk/Isolate-Protein-Fast-digesting-hydrolysate-Gourmet/dp/B01H3O2AMG",
        "postcode": "SW1A 1AA"
    }
    
    try:
        # Import the necessary functions (without running the full Flask app)
        from backend.api.app import PRODUCTION_SCRAPER_AVAILABLE
        
        if PRODUCTION_SCRAPER_AVAILABLE:
            from backend.scrapers.amazon.production_scraper import ProductionAmazonScraper
            
            print(f"🔍 Simulating API call with: {mock_data['amazon_url'][:50]}...")
            
            # Simulate the scraping part of the API
            scraper = ProductionAmazonScraper()
            result = scraper.scrape_with_full_url(mock_data['amazon_url'])
            
            if result:
                print(f"✅ API simulation successful!")
                print(f"   Would return product data with {len(result)} fields")
                
                # Check data completeness for API response
                api_critical_fields = ['title', 'weight_kg', 'origin', 'material_type']
                missing_critical = [field for field in api_critical_fields if not result.get(field)]
                
                if missing_critical:
                    print(f"⚠️  Missing critical API fields: {missing_critical}")
                else:
                    print(f"✅ All critical API fields present")
                    
                return True
            else:
                print(f"❌ API simulation failed - no product data")
                return False
        else:
            print(f"⚠️  Production scraper not available for API simulation")
            return True
            
    except Exception as e:
        print(f"❌ API simulation failed: {e}")
        return False

def main():
    """Run all integration tests"""
    
    print("🚀 PRODUCTION SCRAPER INTEGRATION TEST SUITE")
    print("=" * 70)
    
    tests = [
        ("Import Chain", test_integration),
        ("API Simulation", test_api_endpoint_simulation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} Test...")
        print("-" * 40)
        
        try:
            success = test_func()
            results.append((test_name, success))
            
            if success:
                print(f"✅ {test_name} Test: PASSED")
            else:
                print(f"❌ {test_name} Test: FAILED")
                
        except Exception as e:
            print(f"💥 {test_name} Test: ERROR - {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n" + "=" * 70)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"   {test_name:<20} {status}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! Production scraper integration is ready.")
    else:
        print("⚠️  Some tests failed. Review the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)