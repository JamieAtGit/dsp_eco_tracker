#!/usr/bin/env python3
"""
Comprehensive test of scraping accuracy across 10 diverse Amazon products
Compares scraped data with actual product details to identify gaps and improvements
"""

import sys
import os
import time
import json
from enhanced_scraper_fix import EnhancedAmazonScraper

class ScraperAccuracyTest:
    def __init__(self):
        self.scraper = EnhancedAmazonScraper()
        self.test_results = []
        
    def run_comprehensive_test(self):
        """Test scraper against 10 diverse Amazon products"""
        
        print("🧪 COMPREHENSIVE SCRAPER ACCURACY TEST")
        print("=" * 70)
        print("Testing across 10 diverse product categories to validate extraction accuracy")
        print("=" * 70)
        
        # Define test products with expected data for validation
        test_products = [
            {
                'category': 'Electronics',
                'url': 'https://www.amazon.co.uk/dp/B0CHWRXH8B',  # iPhone 15 case
                'expected': {
                    'title_contains': ['iphone', 'case'],
                    'weight_range': (0.02, 0.2),  # 20g - 200g typical for phone case
                    'brand_expected': True,
                    'material_likely': ['plastic', 'silicone', 'leather', 'metal']
                }
            },
            {
                'category': 'Home & Kitchen',
                'url': 'https://www.amazon.co.uk/dp/B087LBQZPX',  # Coffee machine
                'expected': {
                    'title_contains': ['coffee', 'machine'],
                    'weight_range': (2.0, 15.0),  # 2kg - 15kg typical for coffee machine
                    'brand_expected': True,
                    'material_likely': ['plastic', 'metal', 'mixed']
                }
            },
            {
                'category': 'Books',
                'url': 'https://www.amazon.co.uk/dp/0241988462',  # Popular book
                'expected': {
                    'title_contains': ['book'],
                    'weight_range': (0.2, 1.0),  # 200g - 1kg typical for books
                    'brand_expected': False,  # Books don't usually have brands
                    'material_likely': ['paper']
                }
            },
            {
                'category': 'Clothing',
                'url': 'https://www.amazon.co.uk/dp/B07H8QCZPX',  # T-shirt
                'expected': {
                    'title_contains': ['shirt', 't-shirt', 'tee'],
                    'weight_range': (0.1, 0.5),  # 100g - 500g typical for t-shirt
                    'brand_expected': True,
                    'material_likely': ['fabric', 'cotton', 'mixed']
                }
            },
            {
                'category': 'Health & Personal Care',
                'url': 'https://www.amazon.co.uk/dp/B08FMNXX8L',  # Vitamin supplements
                'expected': {
                    'title_contains': ['vitamin', 'supplement'],
                    'weight_range': (0.05, 0.5),  # 50g - 500g typical for vitamins
                    'brand_expected': True,
                    'material_likely': ['plastic', 'mixed']
                }
            },
            {
                'category': 'Tools & Home Improvement',
                'url': 'https://www.amazon.co.uk/dp/B01LXQBSSJ',  # Drill
                'expected': {
                    'title_contains': ['drill', 'tool'],
                    'weight_range': (0.5, 5.0),  # 500g - 5kg typical for power drill
                    'brand_expected': True,
                    'material_likely': ['plastic', 'metal', 'mixed']
                }
            },
            {
                'category': 'Beauty',
                'url': 'https://www.amazon.co.uk/dp/B00NR1YQMO',  # Skincare product
                'expected': {
                    'title_contains': ['cream', 'moisturizer', 'serum'],
                    'weight_range': (0.03, 0.3),  # 30g - 300g typical for skincare
                    'brand_expected': True,
                    'material_likely': ['plastic', 'glass', 'mixed']
                }
            },
            {
                'category': 'Food & Beverages',
                'url': 'https://www.amazon.co.uk/dp/B07QHQK7B2',  # Snacks
                'expected': {
                    'title_contains': ['snack', 'bar', 'food'],
                    'weight_range': (0.2, 2.0),  # 200g - 2kg typical for food package
                    'brand_expected': True,
                    'material_likely': ['plastic', 'paper', 'mixed']
                }
            },
            {
                'category': 'Sports & Outdoors',
                'url': 'https://www.amazon.co.uk/dp/B08T9BHNJ4',  # Yoga mat
                'expected': {
                    'title_contains': ['yoga', 'mat', 'exercise'],
                    'weight_range': (0.5, 3.0),  # 500g - 3kg typical for yoga mat
                    'brand_expected': True,
                    'material_likely': ['plastic', 'rubber', 'mixed']
                }
            },
            {
                'category': 'Toys & Games',
                'url': 'https://www.amazon.co.uk/dp/B07KZQX8NL',  # LEGO set
                'expected': {
                    'title_contains': ['lego', 'blocks', 'building'],
                    'weight_range': (0.2, 3.0),  # 200g - 3kg typical for LEGO sets
                    'brand_expected': True,
                    'material_likely': ['plastic']
                }
            }
        ]
        
        # Test each product
        for i, product in enumerate(test_products, 1):
            print(f"\n📦 TEST {i}/10: {product['category']}")
            print(f"URL: {product['url']}")
            print("-" * 50)
            
            result = self.test_single_product(product)
            self.test_results.append(result)
            
            # Brief pause between requests to be respectful
            time.sleep(2)
        
        # Generate summary report
        self.generate_accuracy_report()
    
    def test_single_product(self, product):
        """Test scraping accuracy for a single product"""
        
        url = product['url']
        category = product['category']
        expected = product['expected']
        
        try:
            # Scrape the product
            scraped_data = self.scraper.scrape_product_enhanced(url)
            
            if not scraped_data:
                print("❌ SCRAPING FAILED - No data returned")
                return {
                    'category': category,
                    'url': url,
                    'status': 'FAILED',
                    'scraped_data': None,
                    'accuracy_scores': {
                        'title': 0, 'weight': 0, 'brand': 0, 'material': 0, 'overall': 0
                    },
                    'issues': ['Scraping failed completely']
                }
            
            # Analyze accuracy
            accuracy_scores = self.analyze_accuracy(scraped_data, expected)
            issues = self.identify_issues(scraped_data, expected)
            
            # Display results
            print(f"✅ SCRAPED DATA:")
            print(f"   Title: {scraped_data.get('title', 'N/A')}")
            print(f"   Brand: {scraped_data.get('brand', 'N/A')}")
            print(f"   Weight: {scraped_data.get('weight_kg', 'N/A')}kg")
            print(f"   Origin: {scraped_data.get('origin', 'N/A')}")
            print(f"   Material: {scraped_data.get('material_type', 'N/A')}")
            
            print(f"\n📊 ACCURACY SCORES:")
            for metric, score in accuracy_scores.items():
                status = "✅" if score >= 0.8 else "⚠️" if score >= 0.5 else "❌"
                print(f"   {metric.title()}: {status} {score:.1%}")
            
            if issues:
                print(f"\n⚠️ ISSUES IDENTIFIED:")
                for issue in issues:
                    print(f"   - {issue}")
            
            return {
                'category': category,
                'url': url,
                'status': 'SUCCESS',
                'scraped_data': scraped_data,
                'accuracy_scores': accuracy_scores,
                'issues': issues
            }
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            return {
                'category': category,
                'url': url,
                'status': 'ERROR',
                'scraped_data': None,
                'accuracy_scores': {
                    'title': 0, 'weight': 0, 'brand': 0, 'material': 0, 'overall': 0
                },
                'issues': [f'Exception: {str(e)}']
            }
    
    def analyze_accuracy(self, scraped_data, expected):
        """Analyze accuracy of scraped data against expectations"""
        
        scores = {}
        
        # Title accuracy
        title = scraped_data.get('title', '').lower()
        title_matches = sum(1 for keyword in expected['title_contains'] 
                          if keyword.lower() in title)
        scores['title'] = title_matches / len(expected['title_contains']) if expected['title_contains'] else 0
        
        # Weight accuracy
        weight = scraped_data.get('weight_kg', 0)
        min_weight, max_weight = expected['weight_range']
        if min_weight <= weight <= max_weight:
            scores['weight'] = 1.0
        elif weight > 0:
            # Partial credit if weight is extracted but outside expected range
            scores['weight'] = 0.5
        else:
            scores['weight'] = 0.0
        
        # Brand accuracy
        brand = scraped_data.get('brand', '')
        if expected['brand_expected']:
            scores['brand'] = 1.0 if brand and brand.lower() not in ['unknown', 'n/a'] else 0.0
        else:
            scores['brand'] = 1.0  # Not expecting brand, so no penalty
        
        # Material accuracy
        material = scraped_data.get('material_type', '').lower()
        if material.lower() in [m.lower() for m in expected['material_likely']]:
            scores['material'] = 1.0
        elif material and material != 'unknown':
            scores['material'] = 0.5  # Partial credit for any material guess
        else:
            scores['material'] = 0.0
        
        # Overall accuracy
        scores['overall'] = sum(scores.values()) / len(scores)
        
        return scores
    
    def identify_issues(self, scraped_data, expected):
        """Identify specific issues with scraped data"""
        
        issues = []
        
        # Check for missing title
        title = scraped_data.get('title', '')
        if not title or title == 'Unknown Product':
            issues.append("Title extraction failed")
        elif len(title) < 10:
            issues.append("Title seems too short/incomplete")
        
        # Check weight issues
        weight = scraped_data.get('weight_kg', 0)
        min_weight, max_weight = expected['weight_range']
        if weight <= 0:
            issues.append("Weight extraction failed (0 or negative)")
        elif weight < min_weight:
            issues.append(f"Weight too low ({weight}kg < {min_weight}kg expected)")
        elif weight > max_weight:
            issues.append(f"Weight too high ({weight}kg > {max_weight}kg expected)")
        
        # Check brand issues
        brand = scraped_data.get('brand', '')
        if expected['brand_expected'] and (not brand or brand.lower() in ['unknown', 'n/a']):
            issues.append("Brand extraction failed but brand expected")
        
        # Check material issues
        material = scraped_data.get('material_type', '')
        if not material or material.lower() == 'unknown':
            issues.append("Material type detection failed")
        
        # Check origin issues
        origin = scraped_data.get('origin', '')
        if not origin or origin.lower() == 'unknown':
            issues.append("Origin detection failed")
        
        return issues
    
    def generate_accuracy_report(self):
        """Generate comprehensive accuracy report"""
        
        print(f"\n" + "=" * 70)
        print("📊 COMPREHENSIVE SCRAPER ACCURACY REPORT")
        print("=" * 70)
        
        # Overall statistics
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r['status'] == 'SUCCESS')
        failed_tests = total_tests - successful_tests
        
        print(f"📈 OVERALL STATISTICS:")
        print(f"   Total Products Tested: {total_tests}")
        print(f"   Successful Scrapes: {successful_tests} ({successful_tests/total_tests:.1%})")
        print(f"   Failed Scrapes: {failed_tests} ({failed_tests/total_tests:.1%})")
        
        # Calculate average accuracy scores
        successful_results = [r for r in self.test_results if r['status'] == 'SUCCESS']
        if successful_results:
            avg_scores = {}
            for metric in ['title', 'weight', 'brand', 'material', 'overall']:
                avg_scores[metric] = sum(r['accuracy_scores'][metric] for r in successful_results) / len(successful_results)
            
            print(f"\n📊 AVERAGE ACCURACY SCORES:")
            for metric, score in avg_scores.items():
                status = "✅" if score >= 0.8 else "⚠️" if score >= 0.5 else "❌"
                print(f"   {metric.title()}: {status} {score:.1%}")
        
        # Category performance breakdown
        print(f"\n📦 PERFORMANCE BY CATEGORY:")
        for result in self.test_results:
            status_icon = "✅" if result['status'] == 'SUCCESS' else "❌"
            if result['status'] == 'SUCCESS':
                overall_score = result['accuracy_scores']['overall']
                score_icon = "🎯" if overall_score >= 0.8 else "⚠️" if overall_score >= 0.5 else "💥"
                print(f"   {status_icon} {result['category']}: {score_icon} {overall_score:.1%}")
            else:
                print(f"   {status_icon} {result['category']}: FAILED")
        
        # Most common issues
        all_issues = []
        for result in self.test_results:
            all_issues.extend(result['issues'])
        
        if all_issues:
            issue_counts = {}
            for issue in all_issues:
                issue_counts[issue] = issue_counts.get(issue, 0) + 1
            
            print(f"\n⚠️ MOST COMMON ISSUES:")
            sorted_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)
            for issue, count in sorted_issues[:5]:  # Top 5 issues
                print(f"   {count}x - {issue}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        
        if successful_results:
            title_avg = avg_scores['title']
            weight_avg = avg_scores['weight']
            brand_avg = avg_scores['brand']
            material_avg = avg_scores['material']
            
            if title_avg < 0.8:
                print("   📝 Improve title extraction - add more selectors")
            if weight_avg < 0.8:
                print("   ⚖️ Enhance weight extraction - check more specification sections")
            if brand_avg < 0.8:
                print("   🏷️ Improve brand detection - expand brand selectors")
            if material_avg < 0.8:
                print("   🧬 Enhance material detection - add more keyword patterns")
        
        if failed_tests > 0:
            print("   🛡️ Add better error handling and retry mechanisms")
            print("   🕐 Implement rate limiting to avoid being blocked")
        
        print(f"\n✅ TEST COMPLETED - Check results above for detailed analysis")
        
        # Save detailed results to file
        self.save_results_to_file()
    
    def save_results_to_file(self):
        """Save detailed test results to JSON file"""
        
        output_file = 'scraper_accuracy_test_results.json'
        with open(output_file, 'w') as f:
            json.dump(self.test_results, f, indent=2, default=str)
        
        print(f"\n💾 Detailed results saved to: {output_file}")

def main():
    """Run the comprehensive scraper accuracy test"""
    
    # Check if required dependencies are available
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError as e:
        print(f"❌ Missing required dependency: {e}")
        print("Please install with: pip install requests beautifulsoup4")
        return
    
    # Run the test
    tester = ScraperAccuracyTest()
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main()