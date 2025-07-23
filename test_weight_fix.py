#!/usr/bin/env python3
"""
Test the improved weight extraction function
"""

import re

def extract_weight_from_title(title: str) -> float:
    """
    Enhanced weight extraction that avoids nutritional content
    Works for ANY product type with category-specific intelligence
    """
    if not title:
        return 0.0
        
    import re
    title_lower = title.lower()
    
    print(f"🔍 Extracting weight from title: {title}")
    
    # STEP 1: Exclude nutritional content patterns to avoid false matches
    nutritional_exclusions = [
        r'\d+\s*g\s*protein\b',
        r'\d+\s*g\s*carbs?\b', 
        r'\d+\s*g\s*fat\b',
        r'\d+\s*mg\s*(?:sodium|caffeine)\b',
        r'\d+\s*(?:cal|kcal)\b',
        r'\d+\s*g\s*sugar\b',
        r'\d+\s*g\s*fiber\b',
        r'\d+\s*servings?\b',
        r'\d+\s*scoops?\b'
    ]
    
    # Remove nutritional info to avoid false matches
    cleaned_title = title_lower
    for exclusion in nutritional_exclusions:
        if re.search(exclusion, cleaned_title):
            print(f"⚠️ Removing nutritional info pattern: {exclusion}")
            cleaned_title = re.sub(exclusion, ' ', cleaned_title)
    
    print(f"🧹 Cleaned title: {cleaned_title}")
    
    # STEP 2: Look for container weight patterns (ordered by precision)
    container_weight_patterns = [
        # Most precise: explicit container weight
        (r'(\d+(?:\.\d+)?)\s*kg\b', 'kg', 1.0),
        (r'(\d+(?:\.\d+)?)\s*lb[s]?\b', 'lb', 0.453592),
        (r'(\d+(?:\.\d+)?)\s*pound[s]?\b', 'lb', 0.453592),
        
        # Medium precision: large gram amounts (likely containers)
        (r'(\d{3,4})\s*g\b', 'g_large', 0.001),  # 500g, 1000g, 2500g
        
        # Common Amazon formats  
        (r'(\d+(?:\.\d+)?)\s*kilograms?\b', 'kg', 1.0),
        (r'(\d+(?:\.\d+)?)\s*pounds?\b', 'lb', 0.453592),
        (r'(\d+(?:\.\d+)?)\s*ounces?\b', 'oz', 0.0283495),
        
        # Low precision: any gram amount (use with caution)
        (r'(\d+(?:\.\d+)?)\s*g\b(?!ram)', 'g', 0.001),
    ]
    
    for pattern, unit, multiplier in container_weight_patterns:
        matches = re.findall(pattern, cleaned_title)
        if matches:
            try:
                weight_val = float(matches[0])
                weight_kg = weight_val * multiplier
                
                # Category-specific validation
                is_protein_supplement = any(keyword in title_lower for keyword in ['protein', 'whey', 'casein', 'mass gainer', 'supplement'])
                
                if is_protein_supplement:
                    # For protein products, reject weights that are clearly nutritional content
                    if unit == 'g' and weight_val < 200:  # Less than 200g unlikely to be container
                        print(f"⚠️ Rejecting small gram value for protein: {weight_val}g (likely nutritional)")
                        continue
                    elif unit == 'g_large' and weight_val < 400:  # Even large gram pattern, be cautious
                        print(f"⚠️ Rejecting medium gram value for protein: {weight_val}g (likely nutritional)")
                        continue
                
                # General sanity check - reasonable product weights
                if 0.05 <= weight_kg <= 50:  # 50g to 50kg range
                    print(f"⚖️ ✅ Extracted weight: {weight_val}{unit} = {weight_kg:.3f}kg")
                    return weight_kg
                else:
                    print(f"⚠️ Weight out of range: {weight_kg:.3f}kg")
                    
            except (ValueError, IndexError):
                continue
    
    print("⚠️ No valid weight found in title")
    return 0.0

def get_category_fallback_weight(title: str, brand: str = "") -> float:
    """
    Category-specific weight estimation when extraction fails
    Uses intelligent defaults based on product category
    """
    if not title:
        return 1.0
        
    title_lower = title.lower()
    
    print(f"🧠 Getting category fallback for: {title}")
    
    # Protein powder/supplement category
    if any(keyword in title_lower for keyword in ['protein', 'whey', 'casein', 'mass gainer', 'supplement']):
        # Estimate based on common protein powder sizes
        if any(size in title_lower for size in ['trial', 'sample', 'mini', 'small']):
            weight = 0.9  # ~900g trial size
            print(f"🏋️ Protein supplement (trial size): {weight}kg")
        elif any(size in title_lower for size in ['bulk', '10lb', '5kg', 'large', 'jumbo']):
            weight = 4.5  # ~4.5kg bulk size
            print(f"🏋️ Protein supplement (bulk size): {weight}kg")
        else:
            weight = 2.3  # ~2.3kg standard 5lb container
            print(f"🏋️ Protein supplement (standard size): {weight}kg")
        return weight
    
    # Electronics category
    elif any(keyword in title_lower for keyword in ['phone', 'smartphone', 'mobile', 'iphone']):
        weight = 0.2  # Phone weight
        print(f"📱 Smartphone: {weight}kg")
        return weight
    
    # Books and media
    elif any(keyword in title_lower for keyword in ['book', 'kindle', 'paperback', 'hardcover']):
        if 'hardcover' in title_lower:
            weight = 0.6  # Hardcover book
        else:
            weight = 0.3  # Paperback book
        print(f"📚 Book: {weight}kg")
        return weight
    
    # Default fallback
    weight = 1.0
    print(f"❓ Unknown category, using default: {weight}kg")
    return weight

def test_weight_extraction():
    """Test the improved weight extraction"""
    
    print("🧪 TESTING IMPROVED WEIGHT EXTRACTION")
    print("=" * 60)
    
    # Test cases
    test_cases = [
        {
            "title": "MUTANT ISO Surge | Whey Isolate Protein Powder | 25g Protein, Fast-digesting whey Protein Isolate &",
            "expected": "Should use category fallback (~2.3kg)",
            "description": "Original failing case - truncated title with nutritional content"
        },
        {
            "title": "Optimum Nutrition Gold Standard 100% Whey Protein Powder, 5lb Container",
            "expected": "Should extract 5lb = ~2.27kg",
            "description": "Clear container weight in pounds"
        },
        {
            "title": "MyProtein Impact Whey Protein 2.5kg - Vanilla",
            "expected": "Should extract 2.5kg",
            "description": "Clear container weight in kg"
        },
        {
            "title": "BSN True Mass Weight Gainer 2.64kg with 25g Protein per serving",
            "expected": "Should extract 2.64kg, ignore 25g protein",
            "description": "Both container weight and nutritional content"
        },
        {
            "title": "Apple iPhone 14 Pro Max 256GB",
            "expected": "Should use category fallback (~0.2kg)",
            "description": "Electronics with no weight info"
        },
        {
            "title": "The Great Gatsby Paperback Book",
            "expected": "Should use category fallback (~0.3kg)",
            "description": "Book with no weight info"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}: {test_case['description']}")
        print(f"Title: {test_case['title']}")
        print(f"Expected: {test_case['expected']}")
        print("-" * 40)
        
        # Test weight extraction
        extracted_weight = extract_weight_from_title(test_case["title"])
        
        if extracted_weight == 0.0:
            print("🔄 Weight extraction returned 0, testing category fallback...")
            fallback_weight = get_category_fallback_weight(test_case["title"])
            final_weight = fallback_weight
        else:
            final_weight = extracted_weight
        
        print(f"✅ Final weight: {final_weight}kg")
        print()

if __name__ == "__main__":
    test_weight_extraction()