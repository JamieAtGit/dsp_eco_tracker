#!/usr/bin/env python3
"""
Test the NXT Nutrition product specifically
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from enhanced_scraper_fix import EnhancedAmazonScraper

def test_nxt_product():
    """Test the specific NXT Nutrition product"""
    
    url = "https://www.amazon.co.uk/Nutrition-Beef-Protein-Isolate-1-8kg/dp/B07MCMTJWC/"
    
    print("🧪 Testing NXT Nutrition Product")
    print("=" * 60)
    print(f"URL: {url}")
    print()
    
    scraper = EnhancedAmazonScraper()
    result = scraper.scrape_product_enhanced(url)
    
    if result:
        print("✅ ENHANCED SCRAPER RESULTS:")
        print("-" * 40)
        for key, value in result.items():
            print(f"{key:15}: {value}")
        
        print("\n🔍 ACCURACY CHECK:")
        print("-" * 40)
        
        # Check origin accuracy
        origin = result.get('origin', 'Unknown')
        if origin == 'UK':
            print("✅ Origin: ACCURATE (NXT Nutrition → UK)")
        elif origin == 'Unknown':
            print("❌ Origin: FAILED (should detect UK for NXT Nutrition)")
        elif origin == 'Of Primary Ingredien':
            print("❌ Origin: CORRUPTED TEXT (regex pattern issue)")
        else:
            print(f"⚠️  Origin: {origin} (unexpected)")
            
        # Check brand detection
        title = result.get('title', '')
        if 'NXT' in title.upper():
            print("✅ Brand: DETECTED (NXT in title)")
        else:
            print("❌ Brand: NOT DETECTED")
            
    else:
        print("❌ ALL SCRAPING STRATEGIES FAILED")

if __name__ == "__main__":
    test_nxt_product()