#!/usr/bin/env python3
"""
Test the current scraper with the failing protein powder URL
"""

import sys
import os

# Add project root to Python path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.append(BASE_DIR)

# Test both scrapers
try:
    from enhanced_scraper_fix import EnhancedAmazonScraper
    ENHANCED_AVAILABLE = True
    print("✅ Enhanced scraper available")
except ImportError as e:
    ENHANCED_AVAILABLE = False
    print(f"⚠️ Enhanced scraper not available: {e}")

try:
    from backend.scrapers.amazon.unified_scraper import scrape_amazon_product_page
    UNIFIED_AVAILABLE = True
    print("✅ Unified scraper available")
except ImportError as e:
    UNIFIED_AVAILABLE = False
    print(f"⚠️ Unified scraper not available: {e}")

def test_scrapers():
    """Test both scrapers with the failing URL"""
    
    url = "https://www.amazon.co.uk/Isolate-Protein-Fast-digesting-hydrolysate-Gourmet/dp/B01H3O2AMG/ref=sr_1_172?crid=3S6H6H4OUAWJY&dib=eyJ2IjoiMSJ9.7RD_6hAFW5DiqpEG4cAMGdXT3EQjmPbrpjNpKyFebRX1qRd3ORuokjRg3Mvha2D27FeXOra2gOapb3JPIz4N9MaYHTRYqaGhsIc5thDIhy7XQFC5apDfKn0zFgT5Bfqphjozb2AmhPQ9uaWYAw0DlGtq6p72frqDkUPWmhe2qY2eTT91wWKZfPIUjMC8_1U7iKjtUzZYqf28gSvgBY1LsoMfl8UK0HLoxxV4oqAwIfI8rs-i5cnhN7tl2uT2wd0mwYhPteacU7NDWmatNqUcDyVf50wKGqJlpGGfF09f0Eg.PBz3LF0s62vRhw1oI_3ilGdJMml97siSL7rJhvGJU-M&dib_tag=se&keywords=protein%2Bpowder&qid=1753282871&sprefix=protein%2Bpowed%2Caps%2C392&sr=8-172&xpid=vurxvlNeBS5ml&th=1"
    
    print(f"\n🧪 TESTING SCRAPERS")
    print("=" * 80)
    print(f"URL: {url}")
    print()
    
    if ENHANCED_AVAILABLE:
        print("🚀 Testing Enhanced Scraper:")
        print("-" * 40)
        try:
            scraper = EnhancedAmazonScraper()
            result = scraper.scrape_product_enhanced(url)
            
            if result:
                print("✅ Enhanced scraper succeeded!")
                for key, value in result.items():
                    print(f"   {key}: {value}")
            else:
                print("❌ Enhanced scraper failed")
                
        except Exception as e:
            print(f"❌ Enhanced scraper exception: {e}")
        print()
    
    if UNIFIED_AVAILABLE:
        print("🔧 Testing Unified Scraper:")
        print("-" * 40)
        try:
            result = scrape_amazon_product_page(url)
            
            if result:
                print("✅ Unified scraper succeeded!")
                for key, value in result.items():
                    print(f"   {key}: {value}")
            else:
                print("❌ Unified scraper failed")
                
        except Exception as e:
            print(f"❌ Unified scraper exception: {e}")
        print()
    
    print("🔍 ANALYSIS:")
    print("  - Check if title is truncated")
    print("  - Look for actual container weight vs protein content")
    print("  - Verify if weight_kg field has correct value")
    print("  - See if scraper accesses product specifications")

if __name__ == "__main__":
    test_scrapers()