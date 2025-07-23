#!/usr/bin/env python3
"""
🔍 DEBUG MUTANT PROTEIN POWDER WEIGHT EXTRACTION
==============================================

Debug why this specific product is getting 0.03kg instead of proper weight.
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

def test_weight_extraction():
    """Test weight extraction with the specific Mutant protein title"""
    
    # The exact title from your results
    title = "MUTANT ISO Surge | Whey Isolate Protein Powder | 25g Protein, Fast-digesting whey Protein Isolate &"
    
    print("🔍 DEBUGGING MUTANT PROTEIN WEIGHT EXTRACTION")
    print("=" * 60)
    print(f"Title: {title}")
    print(f"Length: {len(title)} characters")
    
    # Import your current weight extraction function
    try:
        from backend.api.app import extract_weight_from_title
        
        print(f"\n🧪 Testing current weight extraction...")
        weight = extract_weight_from_title(title)
        print(f"Result: {weight}kg")
        
        if weight == 0.025:  # 25g converted to kg
            print("❌ PROBLEM IDENTIFIED: Capturing '25g Protein' as product weight")
            print("💡 This is nutritional content per serving, not container weight")
        elif weight < 0.1:
            print("❌ PROBLEM: Weight too low for protein powder container")
            print("💡 Typical protein containers: 1-5kg (2.2-11 lbs)")
        else:
            print("✅ Weight seems reasonable for protein powder")
            
    except ImportError as e:
        print(f"❌ Cannot import weight extraction function: {e}")
        return False
    
    # Manual pattern testing
    print(f"\n🔍 MANUAL PATTERN ANALYSIS:")
    import re
    
    # Test the patterns that might be matching
    weight_patterns = [
        (r'(\d+(?:\.\d+)?)\s*kg\b', 'kg', 1.0),
        (r'(\d+(?:\.\d+)?)\s*g\b(?!ram)', 'g', 0.001),  # This is probably matching "25g"
        (r'(\d+(?:\.\d+)?)\s*lb\b', 'lb', 0.453592),
        (r'(\d+(?:\.\d+)?)\s*lbs\b', 'lb', 0.453592),
        (r'(\d+(?:\.\d+)?)\s*oz\b', 'oz', 0.0283495),
    ]
    
    title_lower = title.lower()
    
    for pattern, unit, multiplier in weight_patterns:
        matches = re.findall(pattern, title_lower)
        if matches:
            for match in matches:
                try:
                    weight_val = float(match)
                    weight_kg = weight_val * multiplier
                    print(f"   📊 Pattern '{pattern}' found: {weight_val}{unit} = {weight_kg:.3f}kg")
                    
                    # Check if this is the problematic match
                    if unit == 'g' and weight_val == 25:
                        print(f"      ❌ This is the problem! '25g Protein' being captured as weight")
                        print(f"      💡 This should be excluded as nutritional content")
                        
                except (ValueError, IndexError):
                    continue
    
    # Check for missing container weight indicators
    print(f"\n🔍 LOOKING FOR CONTAINER WEIGHT CLUES:")
    
    container_indicators = [
        'container', 'tub', 'jar', 'bottle', 'bag', 'packet', 'box',
        'lb', 'lbs', 'kg', 'pound', 'pounds', 'kilogram', 'kilograms'
    ]
    
    found_indicators = []
    for indicator in container_indicators:
        if indicator in title_lower:
            found_indicators.append(indicator)
    
    if found_indicators:
        print(f"   ✅ Found indicators: {', '.join(found_indicators)}")
    else:
        print(f"   ❌ No container weight indicators in title")
        print(f"   💡 Need to use product category fallback")
    
    # Suggest fixes
    print(f"\n💡 SUGGESTED FIXES:")
    print(f"1. Exclude '25g Protein' pattern before weight extraction")
    print(f"2. Use protein powder category fallback (typical: 2-5 lbs = 0.9-2.3kg)")
    print(f"3. Check if full title is being captured (seems truncated with '&')")
    print(f"4. Look for container size in Amazon product specifications")
    
    return True

def suggest_protein_powder_fix():
    """Suggest specific fix for protein powder weight detection"""
    
    print(f"\n🔧 PROTEIN POWDER WEIGHT FIX")
    print("=" * 40)
    
    print("Current title analysis:")
    print("• 'MUTANT ISO Surge | Whey Isolate Protein Powder | 25g Protein...'")
    print("• Contains '25g Protein' (nutritional info, not container weight)")
    print("• Title appears truncated (ends with '&')")
    print("• No container weight mentioned in visible title")
    
    print(f"\nRecommended solution:")
    print(f"1. Add protein powder to category fallbacks:")
    print(f"   - Small container: 0.9kg (2 lbs)")
    print(f"   - Standard container: 2.3kg (5 lbs)")  
    print(f"   - Large container: 4.5kg (10 lbs)")
    
    print(f"\n2. Enhance nutritional content exclusion:")
    print(f"   - Exclude: '25g Protein', '30g Carbs', etc.")
    print(f"   - Look for 'per serving' indicators")
    
    print(f"\n3. Check Amazon specifications section:")
    print(f"   - Product dimensions and weight often in specs")
    print(f"   - Shipping weight available")

if __name__ == "__main__":
    test_weight_extraction()
    suggest_protein_powder_fix()