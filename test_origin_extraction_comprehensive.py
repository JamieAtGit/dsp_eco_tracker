#!/usr/bin/env python3
"""
Comprehensive test of enhanced origin extraction across multiple product types
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from backend.scrapers.amazon.production_scraper import ProductionAmazonScraper

def test_comprehensive_origin_extraction():
    """Test origin extraction on diverse products"""
    
    scraper = ProductionAmazonScraper()
    
    test_products = [
        {
            'name': 'Warrior Protein Flapjack (UK)',
            'url': 'https://www.amazon.co.uk/Warrior-Supplements-Protein-Flapjack-Honey/dp/B07F6HGNQF',
            'expected_origin': 'UK',
            'expected_source': 'manufacturer_contact'
        },
        {
            'name': 'Mutant Protein Powder (Canada)',
            'url': 'https://www.amazon.co.uk/Isolate-Protein-Fast-digesting-hydrolysate-Gourmet/dp/B01H3O2AMG',
            'expected_origin': 'Canada',
            'expected_source': 'brand_mapping'
        },
        {
            'name': 'Random Phone Case (Generic)',
            'url': 'https://www.amazon.co.uk/Spigen-iPhone-Crystal-Hybrid-Clear/dp/B0CHWRXH8B',
            'expected_origin': 'Unknown or detected',
            'expected_source': 'any'
        }
    ]
    
    print("🧪 COMPREHENSIVE ORIGIN EXTRACTION TEST")
    print("=" * 70)
    
    success_count = 0
    
    for i, product in enumerate(test_products, 1):
        print(f"\n📦 TEST {i}/{len(test_products)}: {product['name']}")
        print(f"URL: {product['url'][:50]}...")
        print(f"Expected origin: {product['expected_origin']}")
        
        try:
            result = scraper.scrape_with_full_url(product['url'])
            
            if result:
                origin = result.get('origin', 'Unknown')
                title = result.get('title', 'N/A')
                brand = result.get('brand', 'N/A')
                confidence = result.get('confidence_score', 0)
                
                print(f"✅ SCRAPED SUCCESSFULLY:")
                print(f"   Title: {title[:60]}...")
                print(f"   Brand: {brand}")
                print(f"   Origin: {origin}")
                print(f"   Confidence: {confidence:.1%}")
                
                # Check if origin extraction improved
                if origin != "Unknown":
                    if product['expected_origin'] == 'Unknown or detected' or origin == product['expected_origin']:
                        print(f"✅ Origin extraction: SUCCESS")
                        success_count += 1
                    else:
                        print(f"⚠️  Origin extraction: Got '{origin}', expected '{product['expected_origin']}'")
                        success_count += 0.5  # Partial credit for detecting something
                else:
                    print(f"❌ Origin extraction: Still returning 'Unknown'")
                    
            else:
                print(f"❌ SCRAPING FAILED")
                
        except Exception as e:
            print(f"💥 ERROR: {str(e)}")
            
        print("-" * 50)
    
    print(f"\n📊 TEST SUMMARY")
    print(f"Success rate: {success_count}/{len(test_products)} ({success_count/len(test_products)*100:.1f}%)")
    
    if success_count >= len(test_products) * 0.8:
        print("🎉 Origin extraction fix is working well!")
    elif success_count >= len(test_products) * 0.5:
        print("⚠️  Origin extraction partially working - needs refinement")
    else:
        print("❌ Origin extraction still needs work")

if __name__ == "__main__":
    test_comprehensive_origin_extraction()