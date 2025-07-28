#!/usr/bin/env python3
"""
Update brand_locations.json by removing automotive brands and integrating Amazon-focused brands
"""

import json
import os

def update_brand_locations():
    """Update the main brand_locations.json file"""
    
    # Automotive brands to remove (not sold on Amazon)
    automotive_brands = [
        "bmw", "mercedes-benz", "volkswagen", "audi", "porsche", 
        "toyota", "honda", "nissan", "mazda", "subaru", "mitsubishi",
        "ford", "general motors", "chevrolet", "cadillac"
    ]
    
    # Load existing brand_locations.json
    brand_locations_path = "/Users/jamie/Documents/University/dsp_eco_tracker/brand_locations.json"
    
    with open(brand_locations_path, 'r', encoding='utf-8') as f:
        existing_brands = json.load(f)
    
    print(f"📥 Loaded {len(existing_brands)} existing brands")
    
    # Remove automotive brands
    removed_count = 0
    for auto_brand in automotive_brands:
        if auto_brand in existing_brands:
            del existing_brands[auto_brand]
            removed_count += 1
            print(f"   Removed: {auto_brand}")
    
    print(f"🚗 Removed {removed_count} automotive brands")
    
    # Load Amazon-focused brands
    amazon_brands_path = "/Users/jamie/Documents/University/dsp_eco_tracker/backend/services/amazon_focused_brands.json"
    
    with open(amazon_brands_path, 'r', encoding='utf-8') as f:
        amazon_brands = json.load(f)
    
    print(f"🔄 Loading {len(amazon_brands)} Amazon-focused brands")
    
    # Merge Amazon brands with existing (Amazon brands take priority)
    added_count = 0
    updated_count = 0
    
    for brand_name, brand_data in amazon_brands.items():
        if brand_name in existing_brands:
            existing_brands[brand_name] = brand_data
            updated_count += 1
        else:
            existing_brands[brand_name] = brand_data
            added_count += 1
    
    print(f"➕ Added {added_count} new Amazon brands")
    print(f"🔄 Updated {updated_count} existing brands with Amazon data")
    
    # Export updated brand_locations.json
    with open(brand_locations_path, 'w', encoding='utf-8') as f:
        json.dump(existing_brands, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Updated brand_locations.json with {len(existing_brands)} total brands")
    
    # Statistics
    categories = {}
    amazon_specific = 0
    
    for brand, data in existing_brands.items():
        if 'amazon_categories' in data:
            amazon_specific += 1
            for cat in data.get('amazon_categories', []):
                categories[cat] = categories.get(cat, 0) + 1
    
    print(f"🛒 Brands with Amazon category data: {amazon_specific}")
    print(f"📊 Amazon categories covered: {len(categories)}")
    if categories:
        print(f"📍 Top Amazon categories: {dict(sorted(categories.items(), key=lambda x: x[1], reverse=True)[:10])}")

if __name__ == "__main__":
    update_brand_locations()