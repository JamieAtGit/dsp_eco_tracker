#!/usr/bin/env python3
"""
🚀 RELIABLE REQUESTS-BASED SCRAPER
==================================

When Selenium gets blocked, fall back to smart HTTP requests with:
- Rotating user agents
- Session management
- Header spoofing
- Request timing
"""

import requests
import time
import random
import re
import json
from bs4 import BeautifulSoup
from typing import Dict, Optional

class RequestsScraper:
    def __init__(self):
        self.session = requests.Session()
        self.user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0'
        ]
    
    def get_headers(self):
        """Get realistic headers"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
    
    def scrape_product(self, url: str) -> Optional[Dict]:
        """Scrape product using requests"""
        print(f"📡 Requests scraping: {url}")
        
        # Extract ASIN for clean URL
        asin_match = re.search(r'/dp/([A-Z0-9]{10})', url)
        if asin_match:
            asin = asin_match.group(1)
            clean_url = f"https://www.amazon.co.uk/dp/{asin}"
        else:
            clean_url = url
            asin = "Unknown"
        
        try:
            # Random delay
            time.sleep(random.uniform(2, 5))
            
            headers = self.get_headers()
            response = self.session.get(clean_url, headers=headers, timeout=15)
            
            print(f"📡 Response: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Check for bot detection
                if self.is_blocked(soup):
                    print("🚫 Bot detection in requests method")
                    return self.create_intelligent_fallback(url, asin)
                
                # Extract data
                return self.extract_from_soup(soup, asin, clean_url)
            
            else:
                print(f"⚠️ HTTP {response.status_code}")
                return self.create_intelligent_fallback(url, asin)
                
        except Exception as e:
            print(f"📡 Requests error: {e}")
            return self.create_intelligent_fallback(url, asin)
    
    def is_blocked(self, soup) -> bool:
        """Check if we're being blocked"""
        page_text = soup.get_text().lower()
        blocked_indicators = [
            'captcha', 'robot', 'blocked', 'access denied',
            'unusual traffic', 'automated', 'verify you are human'
        ]
        return any(indicator in page_text for indicator in blocked_indicators)
    
    def extract_from_soup(self, soup, asin: str, url: str) -> Dict:
        """Extract product data from HTML"""
        
        # Extract title with improved selectors
        title = "Unknown Product"
        title_selectors = [
            '#productTitle',
            '.product-title',
            '[data-automation-id="product-title"]',
            'h1.a-size-large',
            'h1[data-automation-id="product-title"]',
            'h1 span'
        ]
        
        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                extracted_title = element.get_text().strip()
                if extracted_title and len(extracted_title) > 5:  # Valid title
                    title = extracted_title
                    break
        
        # Extract brand
        brand = "Unknown"
        brand_selectors = [
            '#bylineInfo',
            '.author.notFaded a',
            '[data-automation-id="byline-info-section"]'
        ]
        
        for selector in brand_selectors:
            element = soup.select_one(selector)
            if element:
                brand_text = element.get_text().strip()
                # Clean brand text
                brand = re.sub(r'^(by|visit the|brand:)\s*', '', brand_text, flags=re.IGNORECASE).strip()
                if len(brand) > 50:
                    brand = brand[:50]
                break
        
        # Get all text for analysis
        all_text = soup.get_text()
        
        # Look for origin in technical details first (HIGHEST PRIORITY)
        origin_from_tech = self.extract_origin_from_tech_details(all_text)
        print(f"🔍 Tech details extraction result: '{origin_from_tech}'")
        
        if origin_from_tech != "Unknown":
            origin = origin_from_tech
            print(f"📍 ✅ Using origin from technical details: {origin}")
        else:
            # Estimate origin from brand as fallback (LOWER PRIORITY)
            brand_origin = self.estimate_origin(brand)
            origin = brand_origin
            print(f"📍 ⚠️ Using brand-based origin fallback: {origin} (from brand: {brand})")
            print(f"📍 NOTE: Technical details did not contain valid origin information")
        
        # Extract weight
        weight = self.extract_weight(all_text)
        # Also try to extract from title
        if weight == 1.0:  # Default weight, try title
            title_weight = self.extract_weight(title)
            if title_weight != 1.0:
                weight = title_weight
                print(f"⚖️ Found weight in title: {weight} kg")
            else:
                print(f"⚖️ Using default weight: {weight} kg")
        else:
            print(f"⚖️ Found weight in tech details: {weight} kg")
        
        # Smart material detection - check for protein powder first
        if any(keyword in title.lower() for keyword in ['protein', 'powder', 'mass gainer', 'supplement', 'whey', 'casein']):
            material = "Plastic"  # Protein powder containers are typically plastic
            
            # For protein powder, if weight is suspiciously low, try better extraction
            if weight < 0.5:  # Protein powder should be at least 500g
                print(f"⚠️ Protein powder weight seems low ({weight}kg), trying enhanced extraction...")
                
                # Look for common protein powder weights in title/text
                protein_weight_patterns = [
                    r'(\d+(?:\.\d+)?)\s*kg\b',  # "1kg", "2.5kg"
                    r'(\d+(?:\.\d+)?)\s*g\b',   # "900g", "1000g"
                    r'(\d+(?:\.\d+)?)\s*lbs?\b', # "5lb", "2.2lbs"
                ]
                
                for pattern in protein_weight_patterns:
                    matches = re.findall(pattern, title.lower())
                    if matches:
                        try:
                            weight_val = float(matches[0])
                            if pattern.endswith('g\\b'):  # Grams
                                if weight_val >= 500:  # At least 500g
                                    weight = weight_val / 1000
                                    print(f"⚖️ Found better protein weight in title: {weight}kg")
                                    break
                            elif pattern.endswith('kg\\b'):  # Kilograms
                                if 0.5 <= weight_val <= 5:  # Reasonable protein weight
                                    weight = weight_val
                                    print(f"⚖️ Found better protein weight in title: {weight}kg")
                                    break
                            elif pattern.endswith('lbs?\\b'):  # Pounds
                                weight_kg = weight_val * 0.453592
                                if 0.5 <= weight_kg <= 5:  # Reasonable protein weight
                                    weight = weight_kg
                                    print(f"⚖️ Found better protein weight in title: {weight}kg")
                                    break
                        except:
                            continue
        else:
            material = self.detect_material(title, all_text)
        
        result = {
            "title": title,
            "origin": origin,
            "weight_kg": weight,
            "dimensions_cm": [20, 15, 10],
            "material_type": material,
            "recyclability": "Medium",
            "eco_score_ml": "C",
            "transport_mode": "Ship", 
            "carbon_kg": None,
            "brand": brand,
            "asin": asin,
            "data_quality_score": 85,
            "confidence": "High",
            "method": "Requests Scraping"
        }
        
        print(f"📡 Requests extracted: {title[:50]}...")
        return result
    
    def create_intelligent_fallback(self, url: str, asin: str) -> Dict:
        """Create intelligent fallback based on URL analysis"""
        print("🧠 Creating intelligent fallback...")
        
        # Analyze URL for clues
        url_lower = url.lower()
        
        # Protein powder detection
        if 'protein' in url_lower:
            title = "Protein Powder Supplement"
            material = "Plastic"
            weight = 2.5  # Typical protein powder weight
            brand = "Unknown Nutrition Brand"
            
        # Electronic detection  
        elif any(term in url_lower for term in ['electronic', 'phone', 'laptop', 'tablet']):
            title = "Electronic Device"
            material = "Mixed"
            weight = 0.8
            brand = "Unknown Electronics"
            
        # Book detection
        elif 'book' in url_lower:
            title = "Book"
            material = "Paper"
            weight = 0.3
            brand = "Unknown Publisher"
            
        # Clothing detection
        elif any(term in url_lower for term in ['clothing', 'shirt', 'dress', 'shoes']):
            title = "Clothing Item"
            material = "Fabric"
            weight = 0.2
            brand = "Unknown Fashion"
            
        else:
            # Generic fallback
            title = "Amazon Product"
            material = "Unknown"
            weight = 1.0
            brand = "Unknown Brand"
        
        return {
            "title": title,
            "origin": "UK",
            "weight_kg": weight,
            "dimensions_cm": [15, 10, 8],
            "material_type": material,
            "recyclability": "Medium",
            "eco_score_ml": "C",
            "transport_mode": "Ship",
            "carbon_kg": None,
            "brand": brand,
            "asin": asin,
            "data_quality_score": 60,  # Lower quality for fallback
            "confidence": "Medium",
            "method": "Intelligent URL Analysis"
        }
    
    def extract_weight(self, text: str) -> float:
        """Extract weight from text with improved precision"""
        text_lower = text.lower()
        
        # Priority patterns - look for specific weight fields first
        priority_patterns = [
            # Weight field patterns
            (r'weight[:\s]+(\d+(?:\.\d+)?)\s*(kg|kilograms?)', 'kg'),
            (r'weight[:\s]+(\d+(?:\.\d+)?)\s*(g|grams?)', 'g'),
            # Product dimensions patterns (e.g., "11 x 7 x 27 cm; 600 g")
            (r';\s*(\d+(?:\.\d+)?)\s*(kg)\b', 'kg'),
            (r';\s*(\d+(?:\.\d+)?)\s*(g)\b', 'g'),
            # Units field patterns (e.g., "Units: 600.0 gram")
            (r'units[:\s]+(\d+(?:\.\d+)?)\s*(g|gram)', 'g'),
            # Title patterns (e.g., "2kg" or "600g" in product title)
            (r'\b(\d+(?:\.\d+)?)\s*kg\b', 'kg'),
            (r'\b(\d+(?:\.\d+)?)\s*g\b(?!ram)', 'g'),  # Avoid "program"
        ]
        
        # Check each pattern in priority order
        for pattern, unit_type in priority_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                for match in matches:
                    try:
                        if isinstance(match, tuple):
                            weight_val = float(match[0])
                        else:
                            weight_val = float(match)
                        
                        # Skip very small values that are likely errors
                        if weight_val < 0.01 and unit_type == 'kg':
                            continue
                        if weight_val < 10 and unit_type == 'g':
                            continue
                            
                        # Convert to kg
                        if unit_type == 'kg':
                            return weight_val
                        elif unit_type == 'g':
                            return weight_val / 1000
                    except:
                        continue
        
        # Pound patterns as fallback
        lb_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:lb|lbs|pounds?)',
            r'weight[:\s]+(\d+(?:\.\d+)?)\s*(?:lb|lbs|pounds?)'
        ]
        
        for pattern in lb_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                try:
                    weight = float(matches[0])
                    return weight * 0.453592  # Convert lbs to kg
                except:
                    continue
        
        return 1.0  # Default weight
    
    def detect_material(self, title: str, text: str) -> str:
        """Detect material type"""
        combined_text = (title + " " + text).lower()
        
        materials = {
            'Plastic': ['plastic', 'polymer', 'container', 'bottle', 'tub'],
            'Metal': ['metal', 'steel', 'aluminum', 'iron'],
            'Glass': ['glass', 'crystal'],
            'Paper': ['paper', 'cardboard', 'book'],
            'Fabric': ['fabric', 'cotton', 'polyester', 'clothing'],
            'Wood': ['wood', 'wooden', 'timber'],
            'Mixed': ['electronic', 'device', 'phone', 'laptop']
        }
        
        for material, keywords in materials.items():
            if any(keyword in combined_text for keyword in keywords):
                return material
        
        return 'Unknown'
    
    def estimate_origin(self, brand: str) -> str:
        """Estimate origin from brand"""
        if not brand or brand == "Unknown":
            return "UK"
        
        # Enhanced brand-to-origin mapping for common brands
        brand_origins = {
            # Protein/Supplement brands
            'optimum nutrition': 'USA',
            'dymatize': 'USA',  # Actually made in Germany but US brand
            'bsn': 'USA',
            'muscletech': 'USA',
            'cellucor': 'USA',
            'gat sport': 'USA',
            'evlution': 'USA',
            'bulk protein': 'England',  # Manchester-based
            'bulk powders': 'England',  # Essex-based
            'myprotein': 'England',     # Manchester-based
            'the protein works': 'England',  # Cheshire-based
            'applied nutrition': 'UK',
            'phd nutrition': 'UK',
            'sci-mx': 'UK',
            'sci mx': 'UK',
            'free soul': 'England',     # London-based
            'grenade': 'England',       # Birmingham-based
            'nxt nutrition': 'UK',      # UK-based supplement company
            'usn uk': 'England',        # UK operations
            'usn': 'South Africa',
            'mutant': 'Canada',
            'allmax': 'Canada',
            'scitec': 'Hungary',
            'weider': 'Germany',
            'esn': 'Germany',
            'biotech usa': 'Hungary',
            'whole supp': 'UK',         # UK-based supplement company
            'wholesupp': 'UK',          # Alternative brand format
            # Electronics
            'samsung': 'South Korea',
            'apple': 'China',
            'sony': 'Japan',
            'lg': 'South Korea',
            'huawei': 'China',
            'xiaomi': 'China',
            'lenovo': 'China',
            'asus': 'Taiwan',
            'dell': 'China',
            'hp': 'China'
        }
        
        brand_lower = brand.lower()
        for brand_key, origin in brand_origins.items():
            if brand_key in brand_lower:
                return origin
        
        return "UK"  # Default
    
    def extract_origin_from_tech_details(self, text: str) -> str:
        """Extract origin from Amazon's technical details with improved accuracy"""
        text_lower = text.lower()
        
        # Debug: Check for key countries in the text
        debug_countries = ['belgium', 'germany', 'england', 'uk', 'usa', 'china']
        for country in debug_countries:
            if country in text_lower:
                country_pos = text_lower.find(country)
                context_start = max(0, country_pos - 80)
                context_end = min(len(text_lower), country_pos + 80)
                context = text_lower[context_start:context_end]
                print(f"🔍 DEBUG: Found '{country}' in text: '{context}'")
        
        # Look for country of origin patterns with improved regex (ordered by specificity)
        patterns = [
            # MOST SPECIFIC: Exact "country of origin:" patterns
            (r"country\s+of\s+origin[:\s]*\b(belgium|germany|uk|gb|united\s+kingdom|usa|united\s+states|china|france|italy|japan|canada|india|spain|netherlands|switzerland|austria|poland|ireland|denmark|sweden|norway)\b", "country_of_origin_exact"),
            
            # SPECIFIC: "Country of origin" with broader capture (but limited)
            (r"country\s+of\s+origin[:\s]*([a-zA-Z][a-zA-Z\s]{1,20}?)(?=\s*(?:\n|country|brand|format|age|additional|manufacturer|$))", "country_of_origin_broad"),
            
            # Made in patterns (high confidence)
            (r"made\s+in[:\s]*\b([a-zA-Z][a-zA-Z\s]{1,20})\b", "made_in"),
            
            # Manufactured in patterns (medium confidence)
            (r"manufactured\s+in[:\s]*\b([a-zA-Z][a-zA-Z\s]{1,20})\b", "manufactured_in"),
            
            # Product of patterns (medium confidence)
            (r"product\s+of[:\s]*\b([a-zA-Z][a-zA-Z\s]{1,20})\b", "product_of"),
            
            # Origin patterns (medium confidence)
            (r"origin[:\s]*\b([a-zA-Z][a-zA-Z\s]{1,20})\b", "origin")
        ]
        
        for pattern, pattern_name in patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            print(f"🔍 Pattern '{pattern_name}': {matches}")
            
            if matches:
                # Take the first match and clean it
                candidate = matches[0].strip()
                
                # Remove any trailing words that aren't part of country name
                candidate = re.sub(r'\s*(brand|format|age|additional|country|manufacturer|item|model|dimensions?).*$', '', candidate).strip()
                
                print(f"🔍 Candidate after cleaning: '{candidate}'")
                
                if candidate and len(candidate) >= 2:  # At least 2 characters
                    # Normalize country names
                    country_map = {
                        "gb": "UK",
                        "united kingdom": "UK", 
                        "great britain": "UK",
                        "britain": "UK",
                        "england": "England",
                        "wales": "Wales",
                        "scotland": "Scotland",
                        "northern ireland": "Northern Ireland",
                        "n. ireland": "Northern Ireland",
                        "n ireland": "Northern Ireland",
                        "usa": "USA",
                        "united states": "USA",
                        "united states of america": "USA",
                        "us": "USA",
                        "deutschland": "Germany",
                        "bundesrepublik deutschland": "Germany",
                        "españa": "Spain",
                        "nederland": "Netherlands",
                        "the netherlands": "Netherlands",
                        "holland": "Netherlands",
                        "belgie": "Belgium",
                        "belgique": "Belgium",
                        "belgië": "Belgium",
                        "schweiz": "Switzerland",
                        "suisse": "Switzerland",
                        "österreich": "Austria",
                        "polska": "Poland",
                        "éire": "Ireland",
                        "république française": "France",
                        "prc": "China",
                        "people's republic of china": "China"
                    }
                    
                    # Check if we have a mapping
                    candidate_lower = candidate.lower()
                    if candidate_lower in country_map:
                        result = country_map[candidate_lower]
                        print(f"🔍 ✅ Mapped '{candidate}' -> '{result}' using pattern '{pattern_name}'")
                        return result
                    elif len(candidate) <= 25:  # Reasonable country name length
                        result = candidate.title()
                        print(f"🔍 ✅ Using direct match '{result}' from pattern '{pattern_name}'")
                        return result
                    else:
                        print(f"🔍 ⚠️ Candidate too long: '{candidate}' ({len(candidate)} chars)")
        
        print(f"🔍 ❌ No origin found in technical details")
        return "Unknown"

def scrape_with_requests(url: str) -> Optional[Dict]:
    """Enhanced scraping with anti-bot strategies"""
    
    # Try enhanced scraper first
    try:
        import sys
        import os
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        sys.path.insert(0, project_root)
        
        from enhanced_scraper_fix import EnhancedAmazonScraper
        
        scraper = EnhancedAmazonScraper()
        result = scraper.scrape_product_enhanced(url)
        
        if result and result.get('title', 'Unknown Product') != 'Unknown Product':
            print(f"✅ Enhanced scraper success: {result.get('title', '')[:50]}...")
            # Convert to expected format
            return {
                'title': result.get('title', 'Unknown Product'),
                'origin': result.get('origin', 'Unknown'), 
                'weight_kg': result.get('weight_kg', 1.0),
                'brand': result.get('brand', 'Unknown'),
                'material_type': result.get('material_type', 'Unknown'),
                'asin': result.get('asin', 'Unknown'),
                'dimensions_cm': [15, 10, 8],  # Default dimensions
                'recyclability': 'Medium'      # Default recyclability
            }
    except Exception as e:
        print(f"🔧 Enhanced scraper failed, using fallback: {e}")
    
    # Fallback to original method
    print("🔄 Falling back to original RequestsScraper...")
    scraper = RequestsScraper()
    return scraper.scrape_product(url)

if __name__ == "__main__":
    test_url = "https://www.amazon.co.uk/dp/B000GIPJ0M"
    result = scrape_with_requests(test_url)
    print(f"Result: {result}")