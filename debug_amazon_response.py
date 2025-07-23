#!/usr/bin/env python3
"""
Debug what we're actually getting from Amazon
"""

import requests
import random
from bs4 import BeautifulSoup
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

def debug_amazon_response():
    """Debug Amazon response to see what we're getting"""
    
    test_url = "https://www.amazon.co.uk/dp/B0CL5KNB9M"  # Echo Dot
    
    user_agents = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]
    
    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0'
    }
    
    print(f"🧪 Testing Amazon response for: {test_url}")
    print("=" * 60)
    
    try:
        response = requests.get(test_url, headers=headers, timeout=15)
        print(f"📡 Status Code: {response.status_code}")
        print(f"📦 Content Length: {len(response.content)} bytes")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Check what we actually got
            page_text = soup.get_text()[:1000]  # First 1000 chars
            print(f"\n📄 First 1000 characters of response:")
            print("-" * 40)
            print(page_text)
            print("-" * 40)
            
            # Check for common Amazon elements
            title_selectors = [
                '#productTitle',
                'span#productTitle', 
                '.product-title',
                'h1',
                '[data-automation-id="product-title"]'
            ]
            
            print(f"\n🔍 Testing title extraction:")
            for selector in title_selectors:
                element = soup.select_one(selector)
                if element:
                    print(f"  ✅ {selector}: '{element.get_text().strip()[:100]}'")
                else:
                    print(f"  ❌ {selector}: Not found")
            
            # Check for technical details
            tech_selectors = [
                '#feature-bullets',
                '#featurebullets_feature_div',
                '.a-unordered-list.a-vertical.a-spacing-mini',
                '[data-feature-name="featurebullets"]',
                '.pdTab'
            ]
            
            print(f"\n🔧 Testing technical details extraction:")
            for selector in tech_selectors:
                elements = soup.select(selector)
                if elements:
                    text = elements[0].get_text()[:200]
                    print(f"  ✅ {selector}: '{text}...'")
                else:
                    print(f"  ❌ {selector}: Not found")
            
            # Check if we're blocked
            blocked_indicators = [
                'captcha', 'robot', 'blocked', 'access denied',
                'unusual traffic', 'automated', 'verify you are human',
                'click the button below to continue shopping'
            ]
            
            is_blocked = any(indicator in page_text.lower() for indicator in blocked_indicators)
            print(f"\n🚫 Blocked Status: {'BLOCKED' if is_blocked else 'NOT BLOCKED'}")
            
            if is_blocked:
                print("🔍 Blocking indicators found:")
                for indicator in blocked_indicators:
                    if indicator in page_text.lower():
                        print(f"  - '{indicator}'")
            
        else:
            print(f"❌ Failed to get page: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    debug_amazon_response()