#!/usr/bin/env python3
"""
Test the universal weight extraction function
"""

import re

def extract_weight_from_title(title: str) -> float:
    """
    Universal weight extraction from Amazon product titles
    Works for ANY product type - no hardcoding
    """
    if not title:
        return 0.0
        
    import re
    title_lower = title.lower()
    
    # Comprehensive weight patterns (ordered by precision)
    weight_patterns = [
        # Most precise: explicit weight mentions
        (r'(\d+(?:\.\d+)?)\s*kg\b', 'kg', 1.0),
        (r'(\d+(?:\.\d+)?)\s*g\b(?!ram)', 'g', 0.001),  # Avoid "program"
        (r'(\d+(?:\.\d+)?)\s*lb\b', 'lb', 0.453592),
        (r'(\d+(?:\.\d+)?)\s*lbs\b', 'lb', 0.453592),
        (r'(\d+(?:\.\d+)?)\s*oz\b', 'oz', 0.0283495),
        
        # Common Amazon formats
        (r'(\d+(?:\.\d+)?)\s*kilograms?\b', 'kg', 1.0),
        (r'(\d+(?:\.\d+)?)\s*grams?\b', 'g', 0.001),
        (r'(\d+(?:\.\d+)?)\s*pounds?\b', 'lb', 0.453592),
        (r'(\d+(?:\.\d+)?)\s*ounces?\b', 'oz', 0.0283495),
    ]
    
    for pattern, unit, multiplier in weight_patterns:
        matches = re.findall(pattern, title_lower)
        if matches:
            try:
                weight_val = float(matches[0])
                weight_kg = weight_val * multiplier
                
                # Sanity check - reasonable product weights
                if 0.001 <= weight_kg <= 100:  # 1g to 100kg range
                    print(f"⚖️ Extracted weight: {weight_val}{unit} = {weight_kg:.3f}kg")
                    return weight_kg
            except (ValueError, IndexError):
                continue
    
    return 0.0

# Test cases
test_cases = [
    "Whole Supp Chocolate Meal Shake, Vegan Protein Meal Replacement Powder, High Fibre, 31g Plant Protei",
    "Product with 1.5kg weight",
    "Item weighing 900g", 
    "Heavy item 2.2lbs",
    "Light product 500 grams",
    "Nothing here",
    "Book about programming"
]

print("🧪 TESTING UNIVERSAL WEIGHT EXTRACTION")
print("=" * 50)

for i, title in enumerate(test_cases, 1):
    print(f"\n{i}. Testing: '{title}'")
    weight = extract_weight_from_title(title)
    print(f"   Result: {weight}kg")