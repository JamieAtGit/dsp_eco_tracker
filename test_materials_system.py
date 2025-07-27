#!/usr/bin/env python3
"""
Test the materials detection system across different product types
"""
import requests
import json
import time

# Test products across different categories
TEST_PRODUCTS = [
    # Electronics
    ("https://www.amazon.com/dp/B0BDHWDR12", "iPhone case - should detect silicone/plastic"),
    ("https://www.amazon.com/dp/B08N5WRWNW", "Echo Dot - should detect plastic/fabric"),
    
    # Kitchen
    ("https://www.amazon.com/dp/B00004OCNS", "Kitchen knife - should detect stainless steel"),
    ("https://www.amazon.com/dp/B00FLYWNYQ", "Instant Pot - should detect stainless steel/plastic"),
    
    # Fitness
    ("https://www.amazon.com/dp/B000P0ZSHK", "Whey protein - should detect plastic container"),
    ("https://www.amazon.com/dp/B01NCWF2RJ", "Yoga mat - should detect PVC/rubber"),
    
    # Furniture
    ("https://www.amazon.com/dp/B073W8NPYD", "Office chair - should detect mesh/plastic/metal"),
    
    # Clothing
    ("https://www.amazon.com/dp/B07XQXQWVY", "T-shirt - should detect cotton/polyester"),
    
    # Books
    ("https://www.amazon.com/dp/0134580990", "Textbook - should detect paper"),
    
    # Toys
    ("https://www.amazon.com/dp/B00T0BUKW8", "LEGO - should detect ABS plastic"),
]

def test_materials_detection(api_url="https://web-production-a62d7.up.railway.app"):
    """Test materials detection for various products"""
    
    print("🧪 TESTING MATERIALS DETECTION SYSTEM")
    print("=" * 70)
    print(f"API: {api_url}")
    print("=" * 70)
    
    results = []
    
    for i, (url, description) in enumerate(TEST_PRODUCTS, 1):
        print(f"\n📦 Test {i}/{len(TEST_PRODUCTS)}: {description}")
        print(f"   URL: {url}")
        
        try:
            response = requests.post(
                f"{api_url}/estimate_emissions",
                json={
                    "amazon_url": url,
                    "postcode": "SW1A 1AA"
                },
                timeout=30
            )
            
            if response.ok:
                data = response.json()
                materials = data.get('data', {}).get('attributes', {}).get('materials', {})
                
                if materials:
                    print(f"   ✅ SUCCESS - Tier {materials.get('tier', 'N/A')}: {materials.get('tier_name', 'Unknown')}")
                    print(f"   Primary: {materials.get('primary_material', 'Unknown')}", end="")
                    if materials.get('primary_percentage'):
                        print(f" ({materials['primary_percentage']}%)")
                    else:
                        print()
                    
                    secondary = materials.get('secondary_materials', [])
                    if secondary:
                        print(f"   Secondary: {', '.join([m['name'] + (f' ({m["percentage"]}%)' if m.get('percentage') else '') for m in secondary])}")
                    
                    print(f"   Confidence: {materials.get('confidence', 0) * 100:.0f}%")
                    
                    results.append({
                        'product': description,
                        'tier': materials.get('tier'),
                        'primary': materials.get('primary_material'),
                        'success': True
                    })
                else:
                    print("   ❌ No materials data in response")
                    results.append({
                        'product': description,
                        'success': False
                    })
            else:
                print(f"   ❌ API Error: {response.status_code}")
                results.append({
                    'product': description,
                    'success': False,
                    'error': response.status_code
                })
                
        except Exception as e:
            print(f"   ❌ Request failed: {e}")
            results.append({
                'product': description,
                'success': False,
                'error': str(e)
            })
        
        # Small delay between requests
        time.sleep(1)
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    
    successful = sum(1 for r in results if r.get('success'))
    print(f"Success rate: {successful}/{len(results)} ({successful/len(results)*100:.0f}%)")
    
    # Tier breakdown
    tier_counts = {}
    for r in results:
        if r.get('success') and r.get('tier'):
            tier = r['tier']
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
    
    if tier_counts:
        print("\nTier Distribution:")
        for tier in sorted(tier_counts.keys()):
            print(f"  Tier {tier}: {tier_counts[tier]} products")
    
    # Failed products
    failed = [r for r in results if not r.get('success')]
    if failed:
        print("\nFailed Products:")
        for f in failed:
            print(f"  - {f['product']}: {f.get('error', 'No materials data')}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "local":
        print("Testing LOCAL API...")
        test_materials_detection("http://localhost:5000")
    else:
        print("Testing PRODUCTION API...")
        print("⏳ Waiting 30 seconds for Railway deployment to complete...")
        time.sleep(30)
        test_materials_detection()