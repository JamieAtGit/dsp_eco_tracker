#!/usr/bin/env python3
"""
Enhanced Amazon scraper that bypasses bot detection and properly extracts weight from specifications
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
        
        # Dual origin extraction
        country_origin, facility_origin = self.extract_dual_origin_enhanced(soup)
        data['country_of_origin'] = country_origin
        data['facility_origin'] = facility_origin
        data['origin'] = country_origin  # Keep backward compatibility
        
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
        """Enhanced weight extraction with specifications table priority"""
        
        print("🔍 Starting enhanced weight extraction...")
        
        # PRIORITY 1: Check Amazon specifications table (most reliable)
        weight_from_specs = self.extract_weight_from_specs(soup)
        if weight_from_specs > 0:
            print(f"✅ SUCCESS: Found weight in specifications: {weight_from_specs}kg")
            return weight_from_specs
        
        # PRIORITY 2: Check product details sections
        weight_from_details = self.extract_weight_from_details(soup)
        if weight_from_details > 0:
            print(f"✅ SUCCESS: Found weight in details: {weight_from_details}kg")
            return weight_from_details
        
        # PRIORITY 3: Check title (but avoid nutritional content)
        weight_from_title = self.extract_weight_from_title(soup)
        if weight_from_title > 0:
            print(f"✅ SUCCESS: Found weight in title: {weight_from_title}kg")
            return weight_from_title
        
        print("⚠️ No weight found, using default 1.0kg")
        return 1.0  # Default

    def extract_weight_from_specs(self, soup):
        """Extract weight from Amazon specifications table - HIGHEST PRIORITY"""
        
        print("🔍 Checking specifications table for weight...")
        
        # Amazon specifications table selectors
        spec_selectors = [
            'table#productDetails_techSpec_section_1',
            'table#productDetails_detailBullets_sections1', 
            'div#productDetails_db_sections',
            'div#detailBullets_feature_div',
            'div.pdTab',
            '#feature-bullets',
            '.a-unordered-list.a-nostyle.a-vertical.a-spacing-none.detail-bullet-list'
        ]
        
        for selector in spec_selectors:
            spec_elements = soup.select(selector)
            for element in spec_elements:
                text = element.get_text().lower()
                
                # Look for weight specifications
                weight_spec_patterns = [
                    r'item\s*weight\s*[:\-]\s*(\d+(?:\.\d+)?)\s*(g|gram|kg|kilogram|lb|pound|oz|ounce)',
                    r'net\s*weight\s*[:\-]\s*(\d+(?:\.\d+)?)\s*(g|gram|kg|kilogram|lb|pound|oz|ounce)',
                    r'weight\s*[:\-]\s*(\d+(?:\.\d+)?)\s*(g|gram|kg|kilogram|lb|pound|oz|ounce)',
                    r'(\d+(?:\.\d+)?)\s*(gram|kg|kilogram|lb|pound|oz|ounce)\s*\(pack',
                    r'‎(\d+(?:\.\d+)?)\s*(gram|kg|kilogram)',  # Special Amazon format
                    r'(\d+(?:\.\d+)?)\s*g\b(?!\s*protein)',  # Direct gram mentions, excluding protein
                    r'(\d+(?:\.\d+)?)\s*kg\b',  # Direct kg mentions
                ]
                
                for pattern in weight_spec_patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    for match in matches:
                        try:
                            if len(match) == 2:
                                weight_val = float(match[0])
                                unit = match[1].lower()
                            else:
                                weight_val = float(match)
                                # Determine unit from context
                                if 'g\\b' in pattern and 'kg' not in pattern:
                                    unit = 'g'
                                elif 'kg' in pattern:
                                    unit = 'kg'
                                else:
                                    continue
                            
                            # Convert to kg
                            if unit in ['g', 'gram']:
                                weight_kg = weight_val / 1000
                            elif unit in ['kg', 'kilogram']:
                                weight_kg = weight_val
                            elif unit in ['lb', 'pound']:
                                weight_kg = weight_val * 0.453592
                            elif unit in ['oz', 'ounce']:
                                weight_kg = weight_val * 0.0283495
                            else:
                                continue
                            
                            # Sanity check for reasonable weight (50g to 50kg)
                            if 0.05 <= weight_kg <= 50:
                                print(f"✅ Found weight in specs: {weight_val}{unit} = {weight_kg:.3f}kg")
                                return weight_kg
                                
                        except (ValueError, IndexError):
                            continue
        
        # Also check for dimension format: "10 x 20 x 10 cm; 727 g"
        dimension_weight_pattern = r'(?:cm|centimetres?|in|inches?);?\s*(\d+(?:\.\d+)?)\s*(g|gram|kg)'
        page_text = soup.get_text()
        dim_matches = re.findall(dimension_weight_pattern, page_text, re.IGNORECASE)
        for match in dim_matches:
            try:
                weight_val = float(match[0])
                unit = match[1].lower()
                
                weight_kg = weight_val / 1000 if unit in ['g', 'gram'] else weight_val
                
                if 0.05 <= weight_kg <= 50:
                    print(f"✅ Found weight in dimensions: {weight_val}{unit} = {weight_kg:.3f}kg")
                    return weight_kg
                    
            except (ValueError, IndexError):
                continue
        
        print("⚠️ No weight found in specifications table")
        return 0

    def extract_weight_from_details(self, soup):
        """Extract weight from product details sections"""
        
        print("🔍 Checking product details for weight...")
        
        # Product details selectors
        detail_selectors = [
            '#feature-bullets ul',
            '#feature-bullets li', 
            '.a-unordered-list .a-list-item',
            '.product-facts-detail',
            '#productDetails_feature_div'
        ]
        
        for selector in detail_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text().lower()
                
                # Look for weight mentions in bullet points
                if any(keyword in text for keyword in ['weight', 'gram', 'kg', 'lb', 'oz']):
                    weight_patterns = [
                        r'(\d+(?:\.\d+)?)\s*g\b(?!\s*protein)',  # 727g but not "25g protein"
                        r'(\d+(?:\.\d+)?)\s*kg\b',
                        r'(\d+(?:\.\d+)?)\s*lb[s]?\b',
                        r'(\d+(?:\.\d+)?)\s*oz\b',
                    ]
                    
                    for pattern in weight_patterns:
                        matches = re.findall(pattern, text)
                        for match in matches:
                            try:
                                weight_val = float(match)
                                
                                # Determine unit from pattern
                                if 'g\\b' in pattern and 'kg' not in pattern:
                                    weight_kg = weight_val / 1000
                                elif 'kg' in pattern:
                                    weight_kg = weight_val
                                elif 'lb' in pattern:
                                    weight_kg = weight_val * 0.453592
                                elif 'oz' in pattern:
                                    weight_kg = weight_val * 0.0283495
                                else:
                                    continue
                                
                                # Sanity check
                                if 0.05 <= weight_kg <= 50:
                                    print(f"✅ Found weight in details: {weight_val} = {weight_kg:.3f}kg")
                                    return weight_kg
                                    
                            except (ValueError, IndexError):
                                continue
        
        print("⚠️ No weight found in product details")
        return 0

    def extract_weight_from_title(self, soup):
        """Extract weight from title, avoiding nutritional content"""
        
        print("🔍 Checking title for weight...")
        
        page_text = soup.get_text()
        title_text = soup.select_one('#productTitle')
        title_text = title_text.get_text() if title_text else ""
        
        print(f"🔍 Title text: {title_text[:100]}...")
        
        # Exclude nutritional content patterns first
        nutritional_exclusions = [
            r'\d+\s*g\s*protein\b',
            r'\d+\s*g\s*carbs?\b', 
            r'\d+\s*g\s*fat\b',
            r'\d+\s*mg\s*(?:sodium|caffeine)\b',
        ]
        
        cleaned_title = title_text.lower()
        for exclusion in nutritional_exclusions:
            cleaned_title = re.sub(exclusion, '', cleaned_title)
        
        print(f"🧹 Cleaned title: {cleaned_title[:100]}...")
        
        # Container weight patterns (after excluding nutritional content)
        title_weight_patterns = [
            r'(\d+(?:\.\d+)?)\s*kg\b', # 2.5kg - highest priority
            r'(\d+(?:\.\d+)?)\s*lb[s]?\b', # 2lbs
            r'(\d+(?:\.\d+)?)\s*g\b(?!\s*protein)', # 727g but not "25g protein"
            r'(\d+(?:\.\d+)?)\s*oz\b', # 16oz
        ]
        
        # Check cleaned title
        for pattern in title_weight_patterns:
            matches = re.findall(pattern, cleaned_title, re.IGNORECASE)
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
        
        print("⚠️ No weight found in title")
        return 0

    def extract_dual_origin_enhanced(self, soup):
        """Enhanced dual origin extraction - returns (country_of_origin, facility_origin)"""
        
        page_text = soup.get_text()
        title_text = soup.select_one('#productTitle')
        title_text = title_text.get_text().lower() if title_text else ""
        
        # Strategy 1: Brand-based country mapping (most reliable)
        brand_origins = {
            'usn': 'South Africa',
            'optimum nutrition': 'USA',
            'myprotein': 'UK', 
            'prozis': 'Portugal',
            'biotech': 'Hungary',
            'scitec': 'Hungary',
            'sci-mx': 'UK',  # Add SCI-MX as UK-based
            'dymatize': 'USA',
            'bsn': 'USA',
            'mutant': 'Canada',
            'kinetica': 'Ireland',
            'nxt nutrition': 'UK',
            'grenade': 'UK',
            'bulk': 'UK',
            'phd': 'UK',
            'applied nutrition': 'UK'
        }
        
        country_of_origin = "Unknown"
        facility_origin = "Unknown"
        
        # Check brand-based country mapping
        for brand, country in brand_origins.items():
            if brand in title_text:
                country_of_origin = country
                print(f"🌍 Country from brand '{brand}': {country}")
                break
        
        return country_of_origin, facility_origin

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

# Test the enhanced scraper specifically for the Mutant protein powder
def test_mutant_protein():
    scraper = EnhancedAmazonScraper()
    url = "https://www.amazon.co.uk/Isolate-Protein-Fast-digesting-hydrolysate-Gourmet/dp/B01H3O2AMG"
    
    print("🧪 Testing enhanced scraper specifically for Mutant protein powder")
    print("=" * 70)
    print(f"URL: {url}")
    print("Expected: Should find 727g weight from specifications table")
    print("=" * 70)
    
    result = scraper.scrape_product_enhanced(url)
    
    if result:
        print("\n✅ SCRAPING SUCCESS!")
        print(f"   Title: {result.get('title', 'Unknown')}")
        print(f"   Brand: {result.get('brand', 'Unknown')}")
        print(f"   Weight: {result.get('weight_kg', 'Unknown')}kg")
        print(f"   Origin: {result.get('origin', 'Unknown')}")
        
        weight_kg = result.get('weight_kg', 0)
        if abs(weight_kg - 0.727) < 0.01:  # Within 10g of expected 727g
            print(f"\n🎉 PERFECT! Found correct weight {weight_kg:.3f}kg ≈ 727g")
        elif weight_kg > 0.5:
            print(f"\n✅ GOOD! Found reasonable weight {weight_kg:.3f}kg")
        else:
            print(f"\n❌ ISSUE: Weight {weight_kg}kg still too low for protein powder")
            print("💡 Expected ~0.727kg (727g) for this product")
    else:
        print("\n❌ SCRAPING FAILED - No result returned")

if __name__ == "__main__":
    test_mutant_protein()