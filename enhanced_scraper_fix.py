#!/usr/bin/env python3
"""
Enhanced Amazon scraper that bypasses bot detection
"""

import requests
import time
import random
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import quote, urlencode

class EnhancedAmazonScraper:
    def __init__(self):
        self.session = requests.Session()
        
        # More diverse user agents
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/119.0'
        ]
        
        # Set persistent cookies
        self.session.cookies.update({
            'session-id': f'123-{random.randint(1000000, 9999999)}-{random.randint(1000000, 9999999)}',
            'ubid-acbuk': f'{random.randint(100, 999)}-{random.randint(1000000, 9999999)}-{random.randint(1000000, 9999999)}',
            'i18n-prefs': 'GBP',
            'lc-acbuk': 'en_GB'
        })

    def get_realistic_headers(self, url: str):
        """Get headers that look like a real browser"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-GB,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-CH-UA': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
            'Sec-CH-UA-Mobile': '?0',
            'Sec-CH-UA-Platform': '"Windows"',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://www.google.com/'
        }

    def scrape_product_enhanced(self, url: str):
        """Enhanced scraping with multiple strategies"""
        
        # Extract ASIN
        asin_match = re.search(r'/dp/([A-Z0-9]{10})', url)
        if not asin_match:
            return None
        
        asin = asin_match.group(1)
        print(f"🎯 Extracted ASIN: {asin}")
        
        # Strategy 1: Direct product page
        result = self.try_direct_page(asin)
        if result and result.get('title') != 'Unknown Product':
            return result
        
        # Strategy 2: Search-based approach
        result = self.try_search_approach(asin)
        if result and result.get('title') != 'Unknown Product':
            return result
        
        # Strategy 3: Mobile version
        result = self.try_mobile_version(asin)
        if result:
            return result
        
        return None

    def try_direct_page(self, asin: str):
        """Try direct product page access"""
        clean_url = f"https://www.amazon.co.uk/dp/{asin}"
        
        print(f"📱 Strategy 1: Direct page - {clean_url}")
        
        try:
            # Simulate browsing behavior
            time.sleep(random.uniform(3, 7))
            
            headers = self.get_realistic_headers(clean_url)
            response = self.session.get(clean_url, headers=headers, timeout=20)
            
            print(f"📊 Response: {response.status_code} ({len(response.content)} bytes)")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Check if blocked
                if self.is_blocked(soup):
                    print("🚫 Strategy 1 blocked")
                    return None
                
                return self.extract_product_data(soup, asin)
                
        except Exception as e:
            print(f"❌ Strategy 1 failed: {e}")
            return None

    def try_search_approach(self, asin: str):
        """Try searching for the ASIN"""
        search_url = f"https://www.amazon.co.uk/s?k={asin}"
        
        print(f"🔍 Strategy 2: Search approach - {search_url}")
        
        try:
            time.sleep(random.uniform(2, 5))
            
            headers = self.get_realistic_headers(search_url)
            response = self.session.get(search_url, headers=headers, timeout=20)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                if self.is_blocked(soup):
                    print("🚫 Strategy 2 blocked")
                    return None
                
                # Find the product link in search results
                product_links = soup.select('h2 a[href*="/dp/"]')
                if product_links:
                    # Get the first result
                    title_element = product_links[0]
                    title = title_element.get_text().strip()
                    
                    # Try to extract more data from search results
                    return {
                        'title': title,
                        'asin': asin,
                        'origin': 'Unknown',
                        'weight_kg': 1.0,
                        'material_type': 'Unknown',
                        'brand': 'Unknown'
                    }
                
        except Exception as e:
            print(f"❌ Strategy 2 failed: {e}")
            return None

    def try_mobile_version(self, asin: str):
        """Try mobile Amazon version"""
        mobile_url = f"https://www.amazon.co.uk/gp/aw/d/{asin}"
        
        print(f"📱 Strategy 3: Mobile version - {mobile_url}")
        
        try:
            time.sleep(random.uniform(2, 4))
            
            # Mobile headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-GB,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive'
            }
            
            response = self.session.get(mobile_url, headers=headers, timeout=20)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                if self.is_blocked(soup):
                    print("🚫 Strategy 3 blocked")
                    return None
                
                return self.extract_mobile_data(soup, asin)
                
        except Exception as e:
            print(f"❌ Strategy 3 failed: {e}")
            return None

    def is_blocked(self, soup):
        """Enhanced blocking detection"""
        page_text = soup.get_text().lower()
        
        blocking_phrases = [
            'click the button below to continue shopping',
            'continue shopping',
            'captcha',
            'robot or automated',
            'unusual traffic',
            'verify you are human',
            'access denied',
            'blocked'
        ]
        
        return any(phrase in page_text for phrase in blocking_phrases)

    def extract_product_data(self, soup, asin: str):
        """Extract data from full page"""
        data = {'asin': asin}
        
        # Enhanced title extraction
        title_selectors = [
            '#productTitle',
            'span#productTitle', 
            '.product-title',
            'h1.a-spacing-none',
            '[data-automation-id="product-title"]',
            '.pdTab h1'
        ]
        
        title = self.find_text_by_selectors(soup, title_selectors, "Unknown Product")
        data['title'] = title[:100] if title else "Unknown Product"
        
        # Brand extraction
        brand_selectors = [
            '#bylineInfo',
            '.po-brand .po-break-word',
            'a#bylineInfo',
            '.brand'
        ]
        
        brand = self.find_text_by_selectors(soup, brand_selectors, "Unknown")
        data['brand'] = brand
        
        # Weight extraction from various places
        weight = self.extract_weight_enhanced(soup)
        data['weight_kg'] = weight
        
        # Origin extraction
        origin = self.extract_origin_enhanced(soup)
        data['origin'] = origin
        
        # Material guessing based on title
        data['material_type'] = self.guess_material_from_title(title)
        
        print(f"✅ Extracted: {title[:50]}... | Brand: {brand} | Weight: {weight}kg")
        
        return data

    def extract_mobile_data(self, soup, asin: str):
        """Extract data from mobile page"""
        data = {'asin': asin}
        
        # Mobile selectors are different
        title_element = soup.select_one('h1') or soup.select_one('.product-title')
        data['title'] = title_element.get_text().strip() if title_element else "Mobile Product"
        
        data['brand'] = "Unknown"
        data['weight_kg'] = 1.0
        data['origin'] = "Unknown"
        data['material_type'] = self.guess_material_from_title(data['title'])
        
        return data

    def find_text_by_selectors(self, soup, selectors, default="Unknown"):
        """Try multiple selectors to find text"""
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text().strip()
                if text and text.lower() not in ['', 'unknown']:
                    return text
        return default

    def extract_weight_enhanced(self, soup):
        """Enhanced weight extraction with better pattern matching"""
        
        page_text = soup.get_text()
        title_text = soup.select_one('#productTitle')
        title_text = title_text.get_text() if title_text else ""
        
        # Prioritize title extraction first (most accurate)
        title_weight_patterns = [
            r'(\d+(?:\.\d+)?)\s*g\b',  # 476g
            r'(\d+(?:\.\d+)?)\s*kg\b', # 2.5kg
            r'(\d+(?:\.\d+)?)\s*oz\b', # 16oz
            r'(\d+(?:\.\d+)?)\s*lb[s]?\b', # 2lbs
        ]
        
        # Check title first (highest priority)
        for pattern in title_weight_patterns:
            matches = re.findall(pattern, title_text, re.IGNORECASE)
            if matches:
                try:
                    weight = float(matches[0])
                    
                    # Convert to kg based on unit
                    if 'g' in pattern and 'kg' not in pattern:
                        weight = weight / 1000  # grams to kg
                        print(f"🔍 Found weight in title: {matches[0]}g = {weight}kg")
                    elif 'oz' in pattern:
                        weight = weight * 0.0283495  # oz to kg
                        print(f"🔍 Found weight in title: {matches[0]}oz = {weight}kg")
                    elif 'lb' in pattern:
                        weight = weight * 0.453592  # lbs to kg
                        print(f"🔍 Found weight in title: {matches[0]}lbs = {weight}kg")
                    else:
                        print(f"🔍 Found weight in title: {matches[0]}kg")
                    
                    if 0.01 <= weight <= 100:  # Reasonable weight range
                        return weight
                except ValueError:
                    continue
        
        # Extended patterns for body text
        body_weight_patterns = [
            r'net\s+weight[:\s]*(\d+(?:\.\d+)?)\s*(?:kg|g|oz|lbs?)',
            r'product\s+weight[:\s]*(\d+(?:\.\d+)?)\s*(?:kg|g|oz|lbs?)',
            r'weight[:\s]*(\d+(?:\.\d+)?)\s*(?:kg|g|oz|lbs?)',
            r'(\d+(?:\.\d+)?)\s*(?:kg|kilograms?|g|grams?|oz|ounces?|lbs?|pounds?)',
        ]
        
        for pattern in body_weight_patterns:
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            if matches:
                try:
                    weight = float(matches[0])
                    
                    # Smart unit detection from context
                    context = page_text[max(0, page_text.find(matches[0])-50):page_text.find(matches[0])+50].lower()
                    
                    if any(unit in context for unit in ['gram', 'g ']):
                        weight = weight / 1000
                        print(f"🔍 Found weight in body: {matches[0]}g = {weight}kg")
                    elif any(unit in context for unit in ['oz', 'ounce']):
                        weight = weight * 0.0283495
                        print(f"🔍 Found weight in body: {matches[0]}oz = {weight}kg")
                    elif any(unit in context for unit in ['lb', 'pound']):
                        weight = weight * 0.453592
                        print(f"🔍 Found weight in body: {matches[0]}lbs = {weight}kg")
                    elif any(unit in context for unit in ['kg', 'kilogram']):
                        print(f"🔍 Found weight in body: {matches[0]}kg")
                    
                    if 0.01 <= weight <= 100:
                        return weight
                except ValueError:
                    continue
        
        print("⚠️ No weight found, using default 1.0kg")
        return 1.0  # Default

    def extract_origin_enhanced(self, soup):
        """Enhanced origin extraction with multiple strategies"""
        
        page_text = soup.get_text()
        
        # Strategy 1: Brand-based origin guessing (most reliable for known brands)
        brand_origins = {
            'usn': 'South Africa',
            'optimum nutrition': 'USA',
            'myprotein': 'UK', 
            'prozis': 'Portugal',
            'biotech': 'Hungary',
            'scitec': 'Hungary',
            'dymatize': 'USA',
            'bsn': 'USA',
            'mutant': 'Canada',
            'kinetica': 'Ireland'
        }
        
        title_text = soup.select_one('#productTitle')
        title_text = title_text.get_text().lower() if title_text else ""
        
        for brand, origin in brand_origins.items():
            if brand in title_text:
                print(f"🌍 Inferred origin from brand '{brand}': {origin}")
                return origin
        
        # Strategy 2: Look for explicit origin statements
        origin_patterns = [
            r'(?:made|manufactured|produced|imported)\s+in\s+([a-zA-Z\s]{3,20})',
            r'country\s+of\s+origin[:\s]*([a-zA-Z\s]{3,20})',
            r'origin[:\s]*([a-zA-Z\s]{3,20})',
            r'from\s+([a-zA-Z\s]{3,20})(?:\s|$)',
        ]
        
        for pattern in origin_patterns:
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            if matches:
                origin = matches[0].strip().title()
                # Filter out common false positives
                false_positives = ['unknown', 'n/a', 'the', 'and', 'with', 'for', 'this', 'that', 'size', 'colour', 'pack', 
                                 'this brand', 'brand', 'item', 'product', 'description', 'details', 'information']
                if (len(origin) > 2 and 
                    origin.lower() not in false_positives and
                    not any(char.isdigit() for char in origin)):
                    print(f"🌍 Found origin: {origin}")
                    return origin
        
        # Strategy 2: Look in product details section
        details_sections = soup.select('.a-section, .pdTab, #detailBullets_feature_div')
        for section in details_sections:
            section_text = section.get_text()
            for pattern in origin_patterns:
                matches = re.findall(pattern, section_text, re.IGNORECASE)
                if matches:
                    origin = matches[0].strip().title()
                    if len(origin) > 2 and origin.lower() not in ['unknown', 'n/a']:
                        print(f"🌍 Found origin in details: {origin}")
                        return origin
        
        print("🌍 No origin found, using Unknown")
        return "Unknown"

    def guess_material_from_title(self, title: str):
        """Guess material from product title"""
        if not title or title == "Unknown Product":
            return "Unknown"
        
        title_lower = title.lower()
        
        material_keywords = {
            'plastic': ['plastic', 'polymer', 'acrylic'],
            'metal': ['metal', 'steel', 'aluminum', 'iron', 'copper'],
            'wood': ['wood', 'wooden', 'timber', 'oak', 'pine'],
            'glass': ['glass', 'crystal'],
            'paper': ['paper', 'cardboard', 'book'],
            'fabric': ['fabric', 'cotton', 'cloth', 'textile'],
            'leather': ['leather'],
            'ceramic': ['ceramic', 'porcelain']
        }
        
        for material, keywords in material_keywords.items():
            if any(keyword in title_lower for keyword in keywords):
                return material.title()
        
        return "Mixed"

# Test the enhanced scraper
def test_enhanced_scraper():
    scraper = EnhancedAmazonScraper()
    test_urls = [
        "https://www.amazon.co.uk/dp/B0CL5KNB9M",  # Echo Dot
        "https://www.amazon.co.uk/dp/B0892LY8PL",  # Protein powder
    ]
    
    for url in test_urls:
        print(f"\n🧪 Testing enhanced scraper on: {url}")
        print("=" * 60)
        
        result = scraper.scrape_product_enhanced(url)
        
        if result:
            print("✅ SUCCESS!")
            for key, value in result.items():
                print(f"   {key}: {value}")
        else:
            print("❌ All strategies failed")

if __name__ == "__main__":
    test_enhanced_scraper()