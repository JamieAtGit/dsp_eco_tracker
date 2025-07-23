#!/usr/bin/env python3
"""
🔍 DIRECT TEST OF ENHANCED SCRAPER
================================

Test the enhanced scraper directly on the problematic Whole Supp product
to verify it can extract correct weight and origin.
"""

import sys
import os

# Add project root to path
project_root = os.path.abspath('.')
sys.path.insert(0, project_root)

def test_enhanced_scraper_direct():
    """Test enhanced scraper directly"""
    
    url = "https://www.amazon.co.uk/Whole-Supp-Replacement-Gluten-Free-Superfoods/dp/B0F38V95VR/"
    
    print("🔍 TESTING ENHANCED SCRAPER DIRECTLY")
    print("=" * 60)
    print(f"URL: {url}")
    
    try:
        from enhanced_scraper_fix import EnhancedAmazonScraper
        
        print("✅ Enhanced scraper imported successfully")
        
        # Create scraper instance
        scraper = EnhancedAmazonScraper()
        print("✅ Enhanced scraper instantiated")
        
        # Scrape the product
        print("\n🔍 Scraping product...")
        result = scraper.scrape_product_enhanced(url)
        
        if result:
            print(f"\n📊 ENHANCED SCRAPER RESULTS:")
            print("-" * 40)
            
            # Key fields we're debugging
            key_fields = [
                'title', 'origin', 'country_of_origin', 'facility_origin',
                'weight_kg', 'material_type', 'brand', 'confidence'
            ]
            
            for field in key_fields:
                value = result.get(field, 'NOT_FOUND')
                print(f"{field:20}: {value}")
            
            print(f"\n📋 ALL FIELDS:")
            print("-" * 40)
            for key, value in result.items():
                print(f"{key:25}: {value}")
                
            # Analyze the results
            print(f"\n✅ ANALYSIS:")
            print("-" * 40)
            
            if result.get('weight_kg', 0) > 0.5:
                print("✅ Weight extraction: SUCCESS (>0.5kg)")
            else:
                print(f"❌ Weight extraction: FAILED ({result.get('weight_kg', 0)}kg)")
            
            if result.get('country_of_origin', 'Unknown') != 'Unknown':
                print(f"✅ Country origin: SUCCESS ({result.get('country_of_origin')})")
            else:
                print("❌ Country origin: FAILED (Unknown)")
            
            if result.get('facility_origin', 'Unknown') != 'Unknown':
                print(f"✅ Facility origin: SUCCESS ({result.get('facility_origin')})")
            else:
                print("❌ Facility origin: FAILED (Unknown)")
                
        else:
            print("❌ Enhanced scraper returned no result")
            
    except ImportError as e:
        print(f"❌ Failed to import enhanced scraper: {e}")
    except Exception as e:
        print(f"❌ Error testing enhanced scraper: {e}")
        import traceback
        traceback.print_exc()

def test_unified_scraper_comparison():
    """Test unified scraper for comparison"""
    
    url = "https://www.amazon.co.uk/Whole-Supp-Replacement-Gluten-Free-Superfoods/dp/B0F38V95VR/"
    
    print(f"\n🔄 TESTING UNIFIED SCRAPER (COMPARISON)")
    print("=" * 60)
    
    try:
        from backend.scrapers.amazon.unified_scraper import scrape_amazon_product_page
        
        print("✅ Unified scraper imported")
        
        result = scrape_amazon_product_page(url)
        
        if result:
            print(f"\n📊 UNIFIED SCRAPER RESULTS:")
            print("-" * 40)
            
            key_fields = ['title', 'origin', 'weight_kg', 'material_type', 'brand']
            
            for field in key_fields:
                value = result.get(field, 'NOT_FOUND')
                print(f"{field:20}: {value}")
                
        else:
            print("❌ Unified scraper returned no result")
            
    except Exception as e:
        print(f"❌ Error testing unified scraper: {e}")

if __name__ == "__main__":
    test_enhanced_scraper_direct()
    test_unified_scraper_comparison()
    
    print(f"\n🎯 SUMMARY:")
    print("=" * 60)
    print("This test shows whether the enhanced scraper can extract:")
    print("1. Correct weight (should be ~1kg for protein powder)")
    print("2. Valid country origin (should detect brand origin)")
    print("3. Facility information (manufacturing details)")
    print("\nIf enhanced scraper works but API doesn't, it's an import issue.")