#!/usr/bin/env python3
"""
🧪 TEST CATEGORY FALLBACK WEIGHT
===============================

Test the category fallback weight function specifically for Mutant protein.
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

def test_category_fallback():
    """Test the category fallback function directly"""
    
    title = "MUTANT ISO Surge | Whey Isolate Protein Powder | 25g Protein, Fast-digesting whey Protein Isolate &"
    brand = "MUTANT"
    
    print("🧪 TESTING CATEGORY FALLBACK WEIGHT")
    print("=" * 50)
    print(f"Title: {title}")
    print(f"Brand: {brand}")
    
    try:
        from backend.api.app import get_category_fallback_weight
        
        print(f"\n🔧 Testing category fallback...")
        fallback_weight = get_category_fallback_weight(title, brand)
        
        print(f"✅ Fallback weight result: {fallback_weight}kg")
        
        if fallback_weight > 0:
            print(f"✅ SUCCESS: Category fallback working properly")
            print(f"💡 This should be used when extract_weight_from_title returns 0.0")
        else:
            print(f"❌ PROBLEM: Category fallback also returning 0")
            
        return fallback_weight
        
    except ImportError as e:
        print(f"❌ Cannot import function: {e}")
        return 0
    except Exception as e:
        print(f"❌ Function failed: {e}")
        return 0

def test_full_weight_enhancement():
    """Test the full weight enhancement logic"""
    
    print(f"\n🔬 TESTING FULL WEIGHT ENHANCEMENT LOGIC")
    print("=" * 50)
    
    # Simulate what happens in the main app
    title = "MUTANT ISO Surge | Whey Isolate Protein Powder | 25g Protein, Fast-digesting whey Protein Isolate &"
    current_weight = 0.03  # What's currently being returned
    
    print(f"Current weight from scraper: {current_weight}kg")
    print(f"Threshold check: {current_weight} <= 0.1? {current_weight <= 0.1}")
    
    if current_weight <= 0.1:
        print(f"✅ Threshold met - should trigger enhancement")
        
        # Test extract_weight_from_title
        try:
            from backend.api.app import extract_weight_from_title
            enhanced_weight = extract_weight_from_title(title)
            print(f"Enhanced extraction result: {enhanced_weight}kg")
            
            if enhanced_weight > 0:
                print(f"✅ Should use enhanced weight: {enhanced_weight}kg")
                final_weight = enhanced_weight
            else:
                print(f"⚠️ Enhanced extraction failed, testing fallback...")
                
                from backend.api.app import get_category_fallback_weight
                fallback_weight = get_category_fallback_weight(title, "MUTANT")
                print(f"Fallback result: {fallback_weight}kg")
                final_weight = fallback_weight
                
            print(f"\n🎯 FINAL WEIGHT SHOULD BE: {final_weight}kg")
            
            if final_weight > 1.0:
                print(f"✅ SUCCESS: Reasonable weight for protein powder")
            else:
                print(f"❌ PROBLEM: Weight still too low")
                
        except Exception as e:
            print(f"❌ Enhancement logic failed: {e}")
    else:
        print(f"❌ Threshold not met - no enhancement triggered")

def debug_why_not_working():
    """Debug why the weight is still showing as 0.03kg"""
    
    print(f"\n🔍 DEBUGGING WHY WEIGHT STILL 0.03KG")
    print("=" * 50)
    
    print("Possible reasons:")
    print("1. extract_weight_from_title is returning 0.025kg (25g), not 0.0")
    print("2. The 0.025kg > 0 so it's not triggering fallback")  
    print("3. The threshold is 0.1kg, but 0.025kg < 0.1kg should trigger it")
    print("4. Something else is overriding the weight after enhancement")
    
    # Check if 0.025 triggers the threshold
    test_weight = 0.025
    print(f"\nTesting: {test_weight} <= 0.1? {test_weight <= 0.1}")
    
    if test_weight <= 0.1:
        print("✅ Should trigger enhancement")
        
        # Check what extract_weight_from_title returns
        title = "MUTANT ISO Surge | Whey Isolate Protein Powder | 25g Protein, Fast-digesting whey Protein Isolate &"
        
        from backend.api.app import extract_weight_from_title
        result = extract_weight_from_title(title)
        print(f"extract_weight_from_title returns: {result}kg")
        
        if result > 0:
            print(f"❌ FOUND THE BUG! extract_weight_from_title returns {result}kg")
            print(f"💡 This is > 0, so fallback is never called")
            print(f"💡 The function should return 0.0 when it finds nutritional content")
        else:
            print(f"✅ Function correctly returns 0.0, should trigger fallback")
    else:
        print("❌ Won't trigger enhancement")

if __name__ == "__main__":
    test_category_fallback()
    test_full_weight_enhancement() 
    debug_why_not_working()