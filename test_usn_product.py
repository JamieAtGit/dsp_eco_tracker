#!/usr/bin/env python3
"""
Test the USN product specifically
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from enhanced_scraper_fix import EnhancedAmazonScraper

def test_usn_product():
    """Test the specific USN product"""
    
    url = "https://www.amazon.co.uk/USN-Protein-Powder-Chocolate-Flavour/dp/B0DG5V9BWQ/ref=sr_1_99_sspa?crid=3S6H6H4OUAWJY&dib=eyJ2IjoiMSJ9.V26JEwSGUSMLcIuzm62ZW74v9ZSL3FxJXKBM3g_BcxF9cizjcZwH3RBmDprfJRsnh5RpxsYSLZQ8CBhjqugI3dF4ELXwWMlWHCHDtwOivh61tHxbXy17HXDtmtR8RvKgZCpi7m9ZtPAnq0dbv8IRgCd-u1fiSauvX-i2uHeTVakOSPmZwi6pyJY3vtVVN5Q6FHVzeIl_2ny-1EA4y0lRXU-02KdFFjOE3yom5MPydj1igvBZdCAtyTxLC7VDfZk9LtmWd3HFCca7F30eTWWFmnuSiLeQOWFpY0wlyj7CobM.5qJz9eOyy7FOeMK9BwEURV-sE5wh_t1zph-SNdn-1OQ&dib_tag=se&keywords=protein%2Bpowder&qid=1753273620&sprefix=protein%2Bpowed%2Caps%2C392&sr=8-99-spons&xpid=vurxvlNeBS5ml&sp_csd=d2lkZ2V0TmFtZT1zcF9tdGY&th=1"
    
    print("🧪 Testing USN Product Enhancement")
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
        
        # Check weight accuracy
        weight = result.get('weight_kg', 0)
        if 0.47 <= weight <= 0.48:
            print("✅ Weight: ACCURATE (476g detected)")
        elif weight == 1.0:
            print("❌ Weight: DEFAULT (1kg fallback - extraction failed)")
        else:
            print(f"⚠️  Weight: {weight}kg (check if reasonable)")
        
        # Check origin accuracy  
        origin = result.get('origin', 'Unknown')
        if origin == 'South Africa':
            print("✅ Origin: ACCURATE (USN brand → South Africa)")
        elif origin == 'Unknown':
            print("❌ Origin: FAILED (should detect South Africa for USN)")
        else:
            print(f"⚠️  Origin: {origin} (unexpected but may be correct)")
            
        # Check title accuracy
        title = result.get('title', '')
        if 'USN' in title and '476g' in title:
            print("✅ Title: EXCELLENT (includes brand and weight)")
        elif 'USN' in title:
            print("✅ Title: GOOD (brand detected)")
        else:
            print("❌ Title: POOR (missing key info)")
            
    else:
        print("❌ ALL SCRAPING STRATEGIES FAILED")
        print("   Amazon may be blocking all our methods")

if __name__ == "__main__":
    test_usn_product()