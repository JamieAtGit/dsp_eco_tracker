#!/usr/bin/env python3
"""
Test the SCI-MX product specifically to check dual origin extraction
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from enhanced_scraper_fix import EnhancedAmazonScraper

def test_sci_mx_product():
    """Test SCI-MX dual origin extraction"""
    
    print("🧪 Testing SCI-MX Dual Origin Extraction")
    print("=" * 60)
    
    # Try a few SCI-MX products to test the functionality
    test_urls = [
        # SCI-MX product example (you can add the actual URL if you have it)
        "https://www.amazon.co.uk/dp/B0EXAMPLE1",  # Replace with actual SCI-MX URL
    ]
    
    # For now, let's test the extraction logic with mock HTML
    scraper = EnhancedAmazonScraper()
    
    # Create mock HTML content that would trigger "A Facility" extraction
    mock_html = """
    <html>
        <head><title>SCI-MX Total Protein</title></head>
        <body>
            <span id="productTitle">SCI-MX Total Protein - Dual Concentrate & Isolate Powder - Lean Muscle Development - Strawberry</span>
            <div class="product-details">
                <p>Country of origin: United Kingdom</p>
                <p>Manufactured at: A Facility in Birmingham</p>
                <p>Net Weight: 900g</p>
            </div>
        </body>
    </html>
    """
    
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(mock_html, 'html.parser')
    
    # Test dual origin extraction
    country_origin, facility_origin = scraper.extract_dual_origin_enhanced(soup)
    
    print("🔍 DUAL ORIGIN EXTRACTION RESULTS:")
    print("-" * 40)
    print(f"Country of Origin: {country_origin}")
    print(f"Facility Origin:   {facility_origin}")
    
    print("\n🔍 EXPECTED BEHAVIOR:")
    print("-" * 40)
    print("✅ Country should be: UK (from SCI-MX brand)")
    print("✅ Facility should be: A Facility In Birmingham (from text)")
    print("✅ This enables accurate distance calculation while preserving detail")
    
    # Test the problematic case where we get "A Facility" as origin
    mock_problematic_html = """
    <html>
        <body>
            <span id="productTitle">SCI-MX Total Protein - Dual Concentrate & Isolate Powder</span>
            <div>Origin: A Facility</div>
        </body>
    </html>
    """
    
    soup2 = BeautifulSoup(mock_problematic_html, 'html.parser')
    country_origin2, facility_origin2 = scraper.extract_dual_origin_enhanced(soup2)
    
    print("\n🔍 PROBLEMATIC CASE TEST:")
    print("-" * 40)
    print(f"Country of Origin: {country_origin2}")
    print(f"Facility Origin:   {facility_origin2}")
    
    if country_origin2 == "UK":
        print("✅ Country correctly detected from SCI-MX brand")
    else:
        print("❌ Country detection failed")
        
    if facility_origin2 == "A Facility":
        print("✅ Facility correctly captured detailed info")
    else:
        print(f"⚠️  Facility: {facility_origin2}")

if __name__ == "__main__":
    test_sci_mx_product()