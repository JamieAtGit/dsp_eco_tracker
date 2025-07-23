#!/usr/bin/env python3
"""
🔍 QUICK SCRAPER TEST
===================

Test which scraper is actually being used by the API
"""

import sys
import os

# Add paths
sys.path.insert(0, os.path.abspath('.'))

def test_scrapers():
    """Test different scrapers directly"""
    
    url = "https://www.amazon.co.uk/Whole-Supp-Replacement-Gluten-Free-Superfoods/dp/B0F38V95VR/"
    
    print("🔍 TESTING DIFFERENT SCRAPERS")
    print("=" * 50)
    
    # Test 1: Try requests_scraper directly
    print("\n1️⃣ TESTING REQUESTS SCRAPER DIRECTLY:")
    try:
        from backend.scrapers.amazon.requests_scraper import scrape_with_requests
        result = scrape_with_requests(url)
        if result:
            print(f"✅ Title: {result.get('title', 'Unknown')[:50]}...")
            print(f"✅ Weight: {result.get('weight_kg', 'Unknown')} kg")
            print(f"✅ Origin: {result.get('origin', 'Unknown')}")
            print(f"✅ Brand: {result.get('brand', 'Unknown')}")
        else:
            print("❌ No result from requests scraper")
    except Exception as e:
        print(f"❌ Requests scraper failed: {e}")
    
    # Test 2: Try unified_scraper  
    print("\n2️⃣ TESTING UNIFIED SCRAPER:")
    try:
        from backend.scrapers.amazon.unified_scraper import scrape_amazon_product_page
        result = scrape_amazon_product_page(url)
        if result:
            print(f"✅ Title: {result.get('title', 'Unknown')[:50]}...")
            print(f"✅ Weight: {result.get('weight_kg', 'Unknown')} kg")
            print(f"✅ Origin: {result.get('origin', 'Unknown')}")
            print(f"✅ Brand: {result.get('brand', 'Unknown')}")
        else:
            print("❌ No result from unified scraper")
    except Exception as e:
        print(f"❌ Unified scraper failed: {e}")
    
    # Test 3: Try integrated_scraper
    print("\n3️⃣ TESTING INTEGRATED SCRAPER:")
    try:
        from backend.scrapers.amazon.integrated_scraper import scrape_amazon_product_page as integrated_scrape
        result = integrated_scrape(url)
        if result:
            print(f"✅ Title: {result.get('title', 'Unknown')[:50]}...")
            print(f"✅ Weight: {result.get('weight_kg', 'Unknown')} kg")
            print(f"✅ Origin: {result.get('origin', 'Unknown')}")
            print(f"✅ Brand: {result.get('brand', 'Unknown')}")
        else:
            print("❌ No result from integrated scraper")
    except Exception as e:
        print(f"❌ Integrated scraper failed: {e}")

if __name__ == "__main__":
    test_scrapers()