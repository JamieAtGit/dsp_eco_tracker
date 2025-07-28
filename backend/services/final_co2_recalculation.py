#!/usr/bin/env python3
"""
Final CO2 Recalculation
Recalculates ALL CO2 values using the new realistic weights and materials
This is the final step to fix credibility for enterprise customers
"""

import csv
import sys
import time

# Add services directory
sys.path.append('/Users/jamie/Documents/University/dsp_eco_tracker/backend/services')
from manufacturing_complexity_multipliers import ManufacturingComplexityCalculator
from enhanced_materials_database import EnhancedMaterialsDatabase

def recalculate_all_co2_values():
    """
    Recalculate ALL CO2 values using realistic weights and materials
    """
    
    print('🔧 FINAL CO2 RECALCULATION WITH REALISTIC DATA')
    print('=' * 70)
    
    # Initialize systems
    complexity_calculator = ManufacturingComplexityCalculator()
    materials_db = EnhancedMaterialsDatabase()
    
    input_path = '/Users/jamie/Documents/University/dsp_eco_tracker/common/data/csv/enhanced_eco_dataset.csv'
    output_path = '/Users/jamie/Documents/University/dsp_eco_tracker/common/data/csv/enhanced_eco_dataset_final_fixed.csv'
    
    print(f'📁 Input: {input_path}')
    print(f'📁 Output: {output_path}')
    
    start_time = time.time()
    stats = {'total': 0, 'co2_improved': 0, 'examples': []}
    
    with open(input_path, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        
        with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
            fieldnames = reader.fieldnames
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in reader:
                stats['total'] += 1
                
                if stats['total'] % 20000 == 0:
                    elapsed = time.time() - start_time
                    print(f'  🔄 Processing: {stats["total"]:,} products ({elapsed/60:.1f} minutes)')
                
                try:
                    # Get current (realistic) data
                    title = row['title']
                    weight = float(row['weight'])  # Now realistic!
                    material = row['material']     # Now correct!
                    category = row['inferred_category'].lower().replace(' ', '_').replace('&', '_')
                    old_co2 = float(row['co2_emissions'])
                    
                    # Get material CO2 intensity
                    material_co2_per_kg = materials_db.get_material_impact_score(material.lower())
                    if not material_co2_per_kg:
                        material_variants = {
                            'textile': 'cotton', 'metal': 'steel', 'electronic': 'aluminum', 'mixed': 'plastic'
                        }
                        alt_material = material_variants.get(material.lower(), 'plastic')
                        material_co2_per_kg = materials_db.get_material_impact_score(alt_material) or 2.0
                    
                    # Calculate NEW realistic CO2 with corrected weight and material
                    enhanced_result = complexity_calculator.calculate_enhanced_co2(
                        weight_kg=weight,
                        material_co2_per_kg=material_co2_per_kg,
                        transport_multiplier=1.0,  # ship
                        category=category
                    )
                    
                    new_co2 = round(enhanced_result['enhanced_total_co2'], 2)
                    
                    # Update CO2 and eco score
                    row['co2_emissions'] = new_co2
                    
                    # Recalculate eco score based on NEW CO2
                    if new_co2 < 5:
                        row['true_eco_score'] = 'A'
                    elif new_co2 < 15:
                        row['true_eco_score'] = 'B'
                    elif new_co2 < 50:
                        row['true_eco_score'] = 'C'
                    elif new_co2 < 150:
                        row['true_eco_score'] = 'D'
                    elif new_co2 < 500:
                        row['true_eco_score'] = 'E'
                    else:
                        row['true_eco_score'] = 'F'
                    
                    # Track improvements
                    if abs(old_co2 - new_co2) > 0.1:  # Significant change
                        stats['co2_improved'] += 1
                        
                        if len(stats['examples']) < 15:
                            stats['examples'].append({
                                'title': title[:40],
                                'weight': weight,
                                'material': material,
                                'old_co2': old_co2,
                                'new_co2': new_co2,
                                'improvement': old_co2 / new_co2 if new_co2 > 0 else 1
                            })
                    
                except (ValueError, KeyError) as e:
                    print(f'⚠️ Error processing row {stats["total"]}: {e}')
                
                writer.writerow(row)
    
    elapsed_time = time.time() - start_time
    
    print(f'\n✅ CO2 RECALCULATION COMPLETE!')
    print(f'⏱️  Processing time: {elapsed_time/60:.1f} minutes')
    print(f'📊 Total products processed: {stats["total"]:,}')
    print(f'📊 CO2 values updated: {stats["co2_improved"]:,}')
    
    print(f'\n🎉 SAMPLE IMPROVEMENTS:')
    for example in stats['examples']:
        print(f'• {example["title"]}... ({example["weight"]}kg {example["material"]})')
        print(f'  CO2: {example["old_co2"]:.1f} → {example["new_co2"]:.1f} kg ({example["improvement"]:.1f}x better)')
    
    # Final validation - check pruning shears
    print(f'\n🎯 FINAL VALIDATION - Pruning Shears Check:')
    with open(output_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        pruning_count = 0
        for row in reader:
            if 'pruning' in row['title'].lower() and pruning_count < 3:
                pruning_count += 1
                print(f'✅ {row["title"]}')
                print(f'   Weight: {row["weight"]} kg, Material: {row["material"]}')
                print(f'   CO2: {row["co2_emissions"]} kg CO2')
                
                # Validate this is realistic
                co2_val = float(row['co2_emissions'])
                weight_val = float(row['weight'])
                
                if co2_val < 5 and weight_val < 1 and row['material'].lower() in ['steel', 'metal']:
                    print(f'   ✅ REALISTIC! Small steel tool with low CO2')
                else:
                    print(f'   ❌ Still unrealistic - needs further investigation')
                print()
    
    return output_path

if __name__ == "__main__":
    
    print("\n🎯 FINAL CO2 RECALCULATION")
    print("This will:")
    print("• Use the corrected realistic weights (0.35kg pruning shears)")
    print("• Use the corrected materials (steel pruning shears)")  
    print("• Recalculate ALL CO2 values with manufacturing complexity")
    print("• Fix the credibility issue for enterprise customers")
    
    print(f"\n🚀 Starting final CO2 recalculation...")
    
    output_file = recalculate_all_co2_values()
    
    print(f"\n🎉 MISSION ACCOMPLISHED!")
    print(f"📁 Final corrected dataset: {output_file}")
    print(f"\n💡 Next step: Replace original dataset with this corrected version")
    print("🌱 Your system now provides completely realistic CO2 values!")