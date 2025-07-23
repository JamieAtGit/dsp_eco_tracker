#!/usr/bin/env python3
"""
Debug the Whole Supp URL to understand where 1.5kg is mentioned
"""

import re
from urllib.parse import unquote

def analyze_url_for_weight(url: str):
    """Analyze the full URL for weight information"""
    
    print("🔍 ANALYZING WHOLE SUPP URL FOR WEIGHT CLUES")
    print("=" * 60)
    print(f"URL: {url}")
    
    # Decode URL parameters
    decoded_url = unquote(url)
    print(f"\n📝 Decoded URL: {decoded_url}")
    
    # Extract all numbers that could be weights
    weight_patterns = [
        (r'(\d+(?:\.\d+)?)\s*kg\b', 'kg'),
        (r'(\d+(?:\.\d+)?)\s*g\b', 'g'),  
        (r'(\d+(?:\.\d+)?)\s*lb\b', 'lb'),
        (r'(\d+(?:\.\d+)?)\s*lbs\b', 'lb'),
    ]
    
    print(f"\n⚖️ WEIGHT PATTERN SEARCH:")
    print("-" * 30)
    
    for pattern, unit in weight_patterns:
        matches = re.findall(pattern, decoded_url.lower())
        if matches:
            print(f"Found {unit} values: {matches}")
            for match in matches:
                try:
                    val = float(match)
                    if unit == 'kg':
                        print(f"  -> {val}kg")
                    elif unit == 'g':
                        print(f"  -> {val}g = {val/1000}kg")
                    elif unit in ['lb', 'lbs']:
                        print(f"  -> {val}lb = {val*0.453592:.3f}kg")
                except:
                    pass
    
    # Look for any numbers that might be weights
    all_numbers = re.findall(r'(\d+(?:\.\d+)?)', decoded_url)
    print(f"\n🔢 ALL NUMBERS IN URL: {all_numbers}")
    
    # Check if 1.5 or 1500 appears anywhere
    if '1.5' in decoded_url:
        print("✅ Found '1.5' in URL!")
        context_match = re.search(r'(.{0,20})1\.5(.{0,20})', decoded_url, re.IGNORECASE)
        if context_match:
            print(f"   Context: '{context_match.group()}'")
    
    if '1500' in decoded_url:
        print("✅ Found '1500' in URL!")
        context_match = re.search(r'(.{0,20})1500(.{0,20})', decoded_url, re.IGNORECASE)
        if context_match:
            print(f"   Context: '{context_match.group()}'")
    
    # Analysis of URL structure
    print(f"\n🏗️ URL STRUCTURE ANALYSIS:")
    print("-" * 30)
    
    parts = decoded_url.split('/')
    for i, part in enumerate(parts):
        if any(char.isdigit() for char in part):
            print(f"Part {i}: {part}")
    
    # Check query parameters
    if '?' in decoded_url:
        query_part = decoded_url.split('?')[1]
        params = query_part.split('&')
        print(f"\n📋 QUERY PARAMETERS:")
        for param in params:
            if '=' in param:
                key, value = param.split('=', 1)
                print(f"  {key}: {value}")

if __name__ == "__main__":
    url = "https://www.amazon.co.uk/Whole-Supp-Replacement-Gluten-Free-Superfoods/dp/B0F38V95VR/ref=sr_1_145_sspa?crid=3S6H6H4OUAWJY&dib=eyJ2IjoiMSJ9.19a17faH86mbqJKhfvmYka8NQhb3SAKgz8ejP8VUxwDYuHdeTiCRS_Rh_6swPSe0gdITaNrlt5Xrb6PwGgtFJAwrL9QHbWaHHwu23Mi9pxDU7hQTWA7WA2x765WRsyiY5U7m2jwrM_g0WCxD90gDqmf3H_bvdStFEQG5V9YTOpFKvH08wN6CiUVfUw8nbPENDop5kYYUPR0IXiWfXlsedmeoUA7zjftele2zSDipzbJZxC9ANqi8cu7sJ4mUhGo-kU8SSTkuOQ35vcVhYi47Yy1C4iDQFmHJsKO_yfRrKiA.uD-cwtMs_P0c4T1z0jbjt8tX2xkqYmRzQPladsfxQO0&dib_tag=se&keywords=protein%2Bpowder&qid=1753280825&sprefix=protein%2Bpowed%2Caps%2C392&sr=8-145-spons&xpid=vurxvlNeBS5ml&sp_csd=d2lkZ2V0TmFtZT1zcF9tdGY&th=1"
    
    analyze_url_for_weight(url)