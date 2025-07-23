#!/usr/bin/env python3
"""
Test the unified scraper with real Amazon URLs to verify functionality
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from backend.scrapers.amazon.unified_scraper import UnifiedProductScraper, scrape_amazon_product_page
import json
from datetime import datetime

def test_scraper():
    """Test the unified scraper with various Amazon URLs"""
    
    # Test URLs - diverse product types
    test_urls = [
        "https://www.amazon.co.uk/dp/B0CL5KNB9M",  # Echo Dot
        "https://www.amazon.co.uk/dp/B0B1VQ1ZQY",  # Book
        "https://www.amazon.co.uk/dp/B0CH75LV73",  # Protein powder
    ]
    
    print("🧪 Testing Unified Scraper")
    print("=" * 60)
    
    # Test 1: Direct scraper usage
    scraper = UnifiedProductScraper()
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n📦 Test {i}: {url}")
        print("-" * 50)
        
        try:
            # Use the unified scraper
            result = scraper.scrape(url)
            
            print(f"✅ Title: {result.title}")
            print(f"✅ Origin: {result.origin}")
            print(f"✅ Weight: {result.weight_kg} kg")
            print(f"✅ Material: {result.material_type}")
            print(f"✅ Brand: {result.brand}")
            print(f"✅ ASIN: {result.asin}")
            print(f"✅ Quality Score: {result.quality_score}%")
            print(f"✅ Confidence: {result.confidence_level}")
            print(f"✅ Strategy Used: {result.strategy_used}")
            
            # Check for "Unknown" values
            unknown_count = sum(1 for field in [
                result.title, result.origin, result.brand, 
                result.material_type, result.asin
            ] if "unknown" in str(field).lower())
            
            if unknown_count > 2:
                print(f"⚠️  WARNING: {unknown_count} fields are 'Unknown'")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            print(f"   Type: {type(e).__name__}")
    
    # Test 2: Legacy function compatibility
    print("\n\n🔄 Testing Legacy Function Compatibility")
    print("=" * 60)
    
    try:
        legacy_result = scrape_amazon_product_page(test_urls[0])
        print(f"✅ Legacy function works!")
        print(f"   Keys returned: {', '.join(legacy_result.keys())}")
        print(f"   Title: {legacy_result.get('title', 'N/A')}")
        print(f"   Origin: {legacy_result.get('origin', 'N/A')}")
    except Exception as e:
        print(f"❌ Legacy function error: {str(e)}")
    
    # Test 3: Cache functionality
    print("\n\n💾 Testing Cache Functionality")
    print("=" * 60)
    
    start_time = datetime.now()
    result1 = scraper.scrape(test_urls[0])
    first_time = (datetime.now() - start_time).total_seconds()
    
    start_time = datetime.now()
    result2 = scraper.scrape(test_urls[0])  # Same URL
    cache_time = (datetime.now() - start_time).total_seconds()
    
    print(f"✅ First scrape: {first_time:.2f}s")
    print(f"✅ Cached scrape: {cache_time:.2f}s")
    print(f"✅ Speed improvement: {first_time/cache_time:.1f}x faster")
    
    # Summary
    cache_stats = scraper.get_cache_stats()
    print(f"\n📊 Cache Stats: {cache_stats}")

if __name__ == "__main__":
    test_scraper()