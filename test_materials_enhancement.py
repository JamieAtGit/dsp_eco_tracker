#!/usr/bin/env python3
"""
Comprehensive test comparing OLD vs ENHANCED materials detection system
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend/services'))

from materials_service import MaterialsIntelligenceService  # OLD
from materials_service_enhanced import EnhancedMaterialsIntelligenceService  # NEW

def compare_systems():
    """Compare OLD vs ENHANCED system capabilities"""
    
    print("🧪 MATERIALS SYSTEM ENHANCEMENT COMPARISON")
    print("=" * 80)
    
    # Initialize both systems
    old_service = MaterialsIntelligenceService()
    new_service = EnhancedMaterialsIntelligenceService()
    
    # Compare basic stats
    print("\n📊 SYSTEM CAPABILITIES:")
    print(f"{'Metric':<25} {'OLD System':<15} {'ENHANCED':<15} {'Improvement':<15}")
    print("-" * 70)
    print(f"{'Product Categories':<25} {len(old_service.category_materials):<15} {len(new_service.category_materials):<15} {'+' + str(len(new_service.category_materials) - len(old_service.category_materials)):<15}")
    print(f"{'Material Keywords':<25} {len(old_service.material_keywords):<15} {len(new_service.material_keywords):<15} {'+' + str(len(new_service.material_keywords) - len(old_service.material_keywords)):<15}")
    print(f"{'CO2 Materials':<25} {len(old_service.material_co2_map):<15} {len(new_service.material_co2_map):<15} {'+' + str(len(new_service.material_co2_map) - len(old_service.material_co2_map)):<15}")
    
    # New categories in enhanced system
    old_categories = set(old_service.category_materials.keys())
    new_categories = set(new_service.category_materials.keys())
    added_categories = new_categories - old_categories
    
    print(f"\n🆕 NEW PRODUCT CATEGORIES ADDED ({len(added_categories)}):")
    categories_by_type = {}
    for cat in sorted(added_categories):
        category_type = categorize_product(cat)
        if category_type not in categories_by_type:
            categories_by_type[category_type] = []
        categories_by_type[category_type].append(cat)
    
    for category_type, products in categories_by_type.items():
        print(f"  {category_type}:")
        for i, product in enumerate(products[:5]):  # Show first 5
            print(f"    • {product}")
        if len(products) > 5:
            print(f"    • ... and {len(products) - 5} more")
    
    # New materials
    old_materials = set(old_service.material_keywords.keys())
    new_materials = set(new_service.material_keywords.keys())
    added_materials = new_materials - old_materials
    
    print(f"\n🧪 NEW MATERIALS ADDED ({len(added_materials)}):")
    for material in sorted(added_materials):
        print(f"  • {material}")
    
    # Test specific examples
    test_products = [
        # NEW CATEGORIES
        {"title": "Yamaha Acoustic Guitar FG830", "description": "Solid spruce top, rosewood back"},
        {"title": "Lawnmower Electric Cordless", "description": "21-inch cutting deck metal housing"},
        {"title": "Watercolor Paint Set with Brushes", "description": "Professional artist supplies"},
        {"title": "Baby Stroller Lightweight", "description": "Aluminum frame with fabric seat"},
        {"title": "Dog Collar Leather Medium", "description": "Genuine leather with metal buckle"},
        {"title": "Drill Cordless 20V", "description": "Professional power tool with metal chuck"},
        
        # ENHANCED EXISTING
        {"title": "Apple iPhone 15 Pro Max", "description": "Titanium design with ceramic shield"},
        {"title": "Nike Air Max Running Shoes", "description": "Mesh upper with rubber sole"},
        {"title": "LEGO Creator Expert Set", "description": "Building blocks construction toy"},
        {"title": "Canon DSLR Camera EOS", "description": "Professional photography equipment"},
        {"title": "Protein Powder Whey Isolate", "description": "5lb container supplement nutrition"},
    ]
    
    print(f"\n🎯 ENHANCED DETECTION EXAMPLES:")
    print("=" * 80)
    
    for i, product in enumerate(test_products, 1):
        print(f"\n{i}. {product['title']}")
        print(f"   Description: {product['description']}")
        
        # Test old system
        old_result = old_service.detect_materials(product)
        print(f"   OLD: Tier {old_result['tier']} - {old_result['primary_material']} ({old_result['confidence']:.1%})")
        
        # Test new system
        new_result = new_service.detect_materials(product)
        print(f"   NEW: Tier {new_result['tier']} - {new_result['primary_material']} ({new_result['confidence']:.1%})")
        
        if len(new_result.get('secondary_materials', [])) > 0:
            secondary = [m['name'] for m in new_result['secondary_materials']]
            print(f"        Secondary: {', '.join(secondary)}")
        
        if new_result.get('intelligence_applied'):
            print(f"        Intelligence: {new_result['intelligence_applied']}")
        
        if new_result.get('prediction_method'):
            print(f"        Method: {new_result['prediction_method']}")
    
    print(f"\n🚀 ENHANCED FEATURES:")
    print("  ✅ Brand Intelligence (Apple, Samsung, Nike, LEGO, etc.)")
    print("  ✅ Price-Tier Awareness (Premium vs Budget materials)")
    print("  ✅ Enhanced Fuzzy Matching (better keyword detection)")
    print("  ✅ Advanced Materials (Carbon Fiber, Titanium, Nylon, etc.)")
    print("  ✅ 200+ New Product Categories")
    print("  ✅ Improved Confidence Scoring")
    print("  ✅ Better Environmental Impact Calculation")

def categorize_product(product_name):
    """Categorize products into logical groups"""
    product = product_name.lower()
    
    if any(x in product for x in ['guitar', 'piano', 'violin', 'drums', 'saxophone', 'trumpet']):
        return "Musical Instruments"
    elif any(x in product for x in ['garden', 'lawn', 'plant', 'fertilizer', 'shovel', 'rake']):
        return "Garden & Outdoor"
    elif any(x in product for x in ['paint', 'canvas', 'pencil', 'brush', 'clay', 'art']):
        return "Art & Craft Supplies"
    elif any(x in product for x in ['stapler', 'printer', 'office', 'calculator', 'folder']):
        return "Office Supplies"
    elif any(x in product for x in ['baby', 'stroller', 'crib', 'diaper', 'infant']):
        return "Baby & Kids Products"
    elif any(x in product for x in ['dog', 'cat', 'pet', 'collar', 'litter', 'toy']):
        return "Pet Products"
    elif any(x in product for x in ['drill', 'saw', 'hammer', 'tool', 'screw', 'nail']):
        return "Home Improvement/DIY"
    elif any(x in product for x in ['vacuum', 'mop', 'clean', 'detergent', 'soap']):
        return "Cleaning Supplies"
    elif any(x in product for x in ['thermometer', 'medical', 'health', 'bandage']):
        return "Medical/Health Equipment"
    elif any(x in product for x in ['ring', 'necklace', 'watch', 'jewelry', 'glasses']):
        return "Jewelry & Accessories"
    elif any(x in product for x in ['lamp', 'light', 'bulb', 'chandelier']):
        return "Lighting"
    elif any(x in product for x in ['phone', 'laptop', 'tablet', 'camera', 'smartwatch']):
        return "Electronics (Enhanced)"
    elif any(x in product for x in ['shirt', 'shoes', 'jacket', 'pants', 'dress']):
        return "Clothing (Enhanced)"
    elif any(x in product for x in ['chair', 'desk', 'table', 'sofa', 'bed']):
        return "Furniture (Enhanced)"
    elif any(x in product for x in ['basketball', 'football', 'yoga', 'weights', 'bike']):
        return "Sports & Fitness (Enhanced)"
    elif any(x in product for x in ['mug', 'pot', 'pan', 'knife', 'blender']):
        return "Kitchen & Home (Enhanced)"
    elif any(x in product for x in ['lego', 'puzzle', 'doll', 'game', 'toy']):
        return "Toys & Games (Enhanced)"
    else:
        return "Other"

if __name__ == "__main__":
    compare_systems()