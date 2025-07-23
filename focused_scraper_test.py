#!/usr/bin/env python3
"""
Focused scraper test on 4 representative Amazon products to validate accuracy
"""

import sys
import os
import time
from enhanced_scraper_fix import EnhancedAmazonScraper

def run_focused_accuracy_test():
    """Test scraper accuracy on 4 representative products"""
    
    print("🧪 FOCUSED SCRAPER ACCURACY TEST")
    print("=" * 70)
    print("Testing 4 representative products to validate extraction accuracy")
    print("=" * 70)
    
    scraper = EnhancedAmazonScraper()
    
    # Define 4 diverse test products with expected validation criteria
    test_products = [
        {
            'name': 'Protein Powder (Known working)',
            'url': 'https://www.amazon.co.uk/Isolate-Protein-Fast-digesting-hydrolysate-Gourmet/dp/B01H3O2AMG',
            'expected_title_keywords': ['mutant', 'protein', 'whey'],
            'expected_weight_range': (0.6, 0.8),  # ~727g
            'expected_brand': 'mutant',
            'expected_origin': 'canada',
            'category': 'Health & Fitness'
        },
        {
            'name': 'Electronics - Phone Case',
            'url': 'https://www.amazon.co.uk/dp/B0CHWRXH8B',
            'expected_title_keywords': ['case', 'phone', 'iphone'],
            'expected_weight_range': (0.02, 0.3),  # 20g-300g typical
            'expected_brand': True,  # Should have some brand
            'expected_origin': 'unknown',  # May not be detected
            'category': 'Electronics'
        },
        {
            'name': 'Home & Kitchen - Coffee',
            'url': 'https://www.amazon.co.uk/dp/B087LBQZPX',
            'expected_title_keywords': ['coffee'],
            'expected_weight_range': (0.5, 10.0),  # 500g-10kg typical
            'expected_brand': True,
            'expected_origin': 'unknown',
            'category': 'Home & Kitchen'
        },
        {
            'name': 'Book - Literature',
            'url': 'https://www.amazon.co.uk/dp/0241988462',
            'expected_title_keywords': ['book', 'story'],
            'expected_weight_range': (0.1, 1.0),  # 100g-1kg typical
            'expected_brand': False,  # Books usually don't have brand
            'expected_origin': 'unknown',
            'category': 'Books'
        }
    ]
    
    results = []
    
    for i, product in enumerate(test_products, 1):
        print(f"\n📦 TEST {i}/4: {product['name']}")
        print(f"Category: {product['category']}")
        print(f"URL: {product['url']}")
        print("-" * 50)
        
        try:
            # Scrape the product
            scraped_data = scraper.scrape_product_enhanced(product['url'])
            
            if scraped_data:
                # Display scraped results
                print(f"✅ SCRAPED SUCCESSFULLY:")
                print(f"   Title: {scraped_data.get('title', 'N/A')}")
                print(f"   Brand: {scraped_data.get('brand', 'N/A')}")
                print(f"   Weight: {scraped_data.get('weight_kg', 'N/A')}kg")
                print(f"   Origin: {scraped_data.get('origin', 'N/A')}")
                print(f"   Material: {scraped_data.get('material_type', 'N/A')}")
                
                # Validate against expectations
                validation = validate_scraped_data(scraped_data, product)
                print(f"\n📊 VALIDATION RESULTS:")
                for check, result in validation.items():
                    status = "✅" if result['passed'] else "❌"
                    print(f"   {status} {check}: {result['message']}")
                
                results.append({
                    'product': product['name'],
                    'status': 'SUCCESS',
                    'data': scraped_data,
                    'validation': validation
                })
                
            else:
                print("❌ SCRAPING FAILED - No data returned")
                results.append({
                    'product': product['name'], 
                    'status': 'FAILED',
                    'data': None,
                    'validation': {}
                })
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            results.append({
                'product': product['name'],
                'status': 'ERROR', 
                'data': None,
                'validation': {}
            })
        
        # Brief pause between requests
        if i < len(test_products):
            print("\n⏳ Waiting 3 seconds before next test...")
            time.sleep(3)
    
    # Generate summary report
    generate_summary_report(results)
    return results

def validate_scraped_data(scraped_data, expected):
    """Validate scraped data against expected criteria"""
    
    validation = {}
    
    # Title validation
    title = scraped_data.get('title', '').lower()
    title_matches = sum(1 for keyword in expected['expected_title_keywords'] 
                       if keyword.lower() in title)
    validation['Title Keywords'] = {
        'passed': title_matches >= len(expected['expected_title_keywords']) * 0.5,
        'message': f"Found {title_matches}/{len(expected['expected_title_keywords'])} expected keywords"
    }
    
    # Weight validation
    weight = scraped_data.get('weight_kg', 0)
    min_weight, max_weight = expected['expected_weight_range']
    weight_valid = min_weight <= weight <= max_weight
    validation['Weight Range'] = {
        'passed': weight_valid,
        'message': f"{weight}kg ({'within' if weight_valid else 'outside'} expected {min_weight}-{max_weight}kg)"
    }
    
    # Brand validation
    brand = scraped_data.get('brand', '').lower()
    if isinstance(expected['expected_brand'], bool):
        brand_valid = bool(brand and brand != 'unknown') == expected['expected_brand']
        validation['Brand Detection'] = {
            'passed': brand_valid,
            'message': f"Brand {'detected' if brand and brand != 'unknown' else 'not detected'} ({'expected' if expected['expected_brand'] else 'not expected'})"
        }
    else:
        brand_valid = expected['expected_brand'].lower() in brand
        validation['Brand Match'] = {
            'passed': brand_valid,
            'message': f"Expected '{expected['expected_brand']}', got '{brand}'"
        }
    
    # Origin validation (lenient since this is often unknown)
    origin = scraped_data.get('origin', '').lower()
    if expected['expected_origin'] == 'unknown':
        validation['Origin Detection'] = {
            'passed': True,  # No penalty for unknown origin when not expected
            'message': f"Origin: {origin} (not expected to be detected)"
        }
    else:
        origin_valid = expected['expected_origin'].lower() in origin
        validation['Origin Match'] = {
            'passed': origin_valid,
            'message': f"Expected '{expected['expected_origin']}', got '{origin}'"
        }
    
    return validation

def generate_summary_report(results):
    """Generate a summary report of all test results"""
    
    print(f"\n" + "=" * 70)
    print("📊 SCRAPER ACCURACY TEST SUMMARY")
    print("=" * 70)
    
    total_tests = len(results)
    successful_scrapes = sum(1 for r in results if r['status'] == 'SUCCESS')
    failed_scrapes = total_tests - successful_scrapes
    
    print(f"📈 OVERALL PERFORMANCE:")
    print(f"   Total Products Tested: {total_tests}")
    print(f"   Successful Scrapes: {successful_scrapes}/{total_tests} ({successful_scrapes/total_tests:.1%})")
    print(f"   Failed Scrapes: {failed_scrapes}/{total_tests} ({failed_scrapes/total_tests:.1%})")
    
    # Analyze validation results
    if successful_scrapes > 0:
        successful_results = [r for r in results if r['status'] == 'SUCCESS']
        
        # Count validation passes
        validation_stats = {}
        for result in successful_results:
            for check, validation in result['validation'].items():
                if check not in validation_stats:
                    validation_stats[check] = {'passed': 0, 'total': 0}
                validation_stats[check]['total'] += 1
                if validation['passed']:
                    validation_stats[check]['passed'] += 1
        
        print(f"\n📊 VALIDATION ACCURACY:")
        for check, stats in validation_stats.items():
            accuracy = stats['passed'] / stats['total']
            status = "✅" if accuracy >= 0.8 else "⚠️" if accuracy >= 0.5 else "❌"
            print(f"   {status} {check}: {stats['passed']}/{stats['total']} ({accuracy:.1%})")
        
        # Calculate overall accuracy
        total_checks = sum(stats['total'] for stats in validation_stats.values())
        total_passed = sum(stats['passed'] for stats in validation_stats.values())
        overall_accuracy = total_passed / total_checks if total_checks > 0 else 0
        
        print(f"\n🎯 OVERALL ACCURACY: {overall_accuracy:.1%}")
        
        # Performance by category
        print(f"\n📦 PERFORMANCE BY PRODUCT:")
        for result in results:
            if result['status'] == 'SUCCESS':
                validations = result['validation']
                passed_checks = sum(1 for v in validations.values() if v['passed'])
                total_checks = len(validations)
                accuracy = passed_checks / total_checks if total_checks > 0 else 0
                status = "🎯" if accuracy >= 0.8 else "⚠️" if accuracy >= 0.5 else "💥"
                print(f"   {status} {result['product']}: {passed_checks}/{total_checks} ({accuracy:.1%})")
            else:
                print(f"   ❌ {result['product']}: {result['status']}")
    
    # Recommendations
    print(f"\n💡 KEY FINDINGS & RECOMMENDATIONS:")
    
    if successful_scrapes == total_tests:
        print("   ✅ Excellent! All products scraped successfully")
    elif successful_scrapes >= total_tests * 0.8:
        print("   ⚠️ Good scraping rate, but some products failed")
        print("   💡 Consider adding fallback strategies for failed products")
    else:
        print("   ❌ Poor scraping success rate")
        print("   💡 Review scraping strategies and error handling")
    
    if successful_scrapes > 0:
        if overall_accuracy >= 0.8:
            print("   ✅ High data accuracy - scraper performing well!")
        elif overall_accuracy >= 0.6:
            print("   ⚠️ Moderate accuracy - room for improvement")
            print("   💡 Focus on weight extraction and brand detection")
        else:
            print("   ❌ Low data accuracy - significant improvements needed")
            print("   💡 Review extraction patterns and validation logic")
    
    print(f"\n✅ FOCUSED TEST COMPLETED")
    
if __name__ == "__main__":
    run_focused_accuracy_test()