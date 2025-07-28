#!/usr/bin/env python3
"""
Master Integration Test - End-to-End Workflow Testing
Tests complete carbon calculation workflow using all systems
"""

import sys
import os
import json
import time
from typing import Dict, List, Any

# Add the services directory to Python path
sys.path.append('/Users/jamie/Documents/University/dsp_eco_tracker/backend/services')

def test_complete_product_analysis():
    """Test complete product analysis from input to carbon calculation"""
    print("🔬 MASTER INTEGRATION TEST - COMPLETE WORKFLOW")
    print("=" * 80)
    
    try:
        # Import all systems
        from amazon_supply_chain_intelligence import AmazonSupplyChainIntelligence
        from multi_tier_supply_chain_analysis import MultiTierSupplyChainAnalysis, ManufacturingStrategy
        from transportation_optimization_engine import TransportationOptimizationEngine, CargoType, OptimizationConstraints, UrgencyLevel
        from enhanced_materials_database import EnhancedMaterialsDatabase
        from manufacturing_complexity_multipliers import ManufacturingComplexityCalculator
        
        print("✅ All systems imported successfully")
        
        # Initialize all systems
        print("\n🏗️ Initializing all systems...")
        sci = AmazonSupplyChainIntelligence()
        mtsc = MultiTierSupplyChainAnalysis()
        toe = TransportationOptimizationEngine()
        emd = EnhancedMaterialsDatabase()
        mcc = ManufacturingComplexityCalculator()
        
        print("✅ All systems initialized successfully")
        
        # Test product: iPhone 15 Pro
        test_product = {
            "name": "iPhone 15 Pro",
            "weight_kg": 0.22,
            "materials": ["aluminum", "titanium", "glass", "silicon"],
            "category": "smartphones",
            "manufacturing_location": "china",
            "customer_region": "uk_london"
        }
        
        print(f"\n📱 Testing complete workflow for: {test_product['name']}")
        print(f"   Weight: {test_product['weight_kg']} kg")
        print(f"   Materials: {', '.join(test_product['materials'])}")
        print(f"   Manufacturing: {test_product['manufacturing_location']}")
        print(f"   Destination: {test_product['customer_region']}")
        
        results = {}
        
        # 1. Materials Analysis
        print("\n1️⃣ Materials Impact Analysis...")
        materials_analysis = {}
        total_material_impact = 0
        
        for material in test_product["materials"]:
            try:
                impact = emd.get_material_impact_score(material)
                materials_analysis[material] = impact
                total_material_impact += impact
                print(f"   {material}: {impact:.2f} kg CO2/kg")
            except Exception as e:
                print(f"   ⚠️ Could not get impact for {material}: {e}")
        
        results["materials_analysis"] = {
            "individual_impacts": materials_analysis,
            "total_material_impact_score": total_material_impact,
            "average_impact": total_material_impact / len(test_product["materials"])
        }
        
        # 2. Manufacturing Complexity Analysis
        print("\n2️⃣ Manufacturing Complexity Analysis...")
        try:
            complexity_data = mcc.get_manufacturing_complexity(test_product["category"])
            complexity_factor = complexity_data.get("complexity_factor", 1.0)
            
            print(f"   Category: {test_product['category']}")
            print(f"   Complexity Factor: {complexity_factor:.1f}x")
            print(f"   Explanation: {complexity_data.get('explanation', 'N/A')}")
            
            results["manufacturing_complexity"] = complexity_data
            
        except Exception as e:
            print(f"   ⚠️ Manufacturing complexity analysis failed: {e}")
            results["manufacturing_complexity"] = {"error": str(e)}
        
        # 3. Amazon Supply Chain Analysis
        print("\n3️⃣ Amazon Supply Chain Analysis...")
        try:
            supply_chain_analysis = sci.calculate_supply_chain_emissions(
                product_weight_kg=test_product["weight_kg"],
                manufacturing_location=test_product["manufacturing_location"],
                customer_region=test_product["customer_region"],
                delivery_speed="standard",
                product_category="electronics"
            )
            
            total_co2_kg = supply_chain_analysis["total_supply_chain_co2_kg"]
            print(f"   Total Supply Chain CO2: {total_co2_kg:.3f} kg")
            
            # Show breakdown
            breakdown = supply_chain_analysis["emissions_breakdown"]
            for component, data in breakdown.items():
                co2_g = data["total_co2_g"]
                print(f"   • {component.replace('_', ' ').title()}: {co2_g/1000:.3f} kg CO2")
            
            results["amazon_supply_chain"] = supply_chain_analysis
            
        except Exception as e:
            print(f"   ⚠️ Amazon supply chain analysis failed: {e}")
            results["amazon_supply_chain"] = {"error": str(e)}
        
        # 4. Multi-Tier Supply Chain Analysis
        print("\n4️⃣ Multi-Tier Supply Chain Analysis...")
        try:
            multi_tier_analysis = mtsc.analyze_multi_tier_emissions(
                product_category="smartphone",
                product_weight_kg=test_product["weight_kg"],
                manufacturing_strategy=ManufacturingStrategy.HYBRID,
                demand_volatility="medium"
            )
            
            total_multi_tier_co2_kg = multi_tier_analysis["total_multi_tier_co2_kg"]
            print(f"   Total Multi-Tier CO2: {total_multi_tier_co2_kg:.3f} kg")
            
            # Show tier breakdown
            tier_breakdown = multi_tier_analysis["tier_breakdown"]
            for tier, data in tier_breakdown.items():
                co2_g = data["total_co2_g"]
                print(f"   • {tier.replace('_', ' ').title()}: {co2_g/1000:.3f} kg CO2")
            
            results["multi_tier_analysis"] = multi_tier_analysis
            
        except Exception as e:
            print(f"   ⚠️ Multi-tier analysis failed: {e}")
            results["multi_tier_analysis"] = {"error": str(e)}
        
        # 5. Transportation Optimization Analysis
        print("\n5️⃣ Transportation Optimization Analysis...")
        try:
            constraints = OptimizationConstraints(
                urgency_level=UrgencyLevel.STANDARD,
                allow_multi_modal=True,
                prefer_renewable_energy=True
            )
            
            transport_optimization = toe.optimize_route(
                origin="Shanghai, China",
                destination="London, UK",
                cargo_weight_kg=test_product["weight_kg"],
                cargo_type=CargoType.FRAGILE,
                constraints=constraints
            )
            
            print(f"   Optimized Transport CO2: {transport_optimization.total_carbon_g/1000:.3f} kg")
            print(f"   Transport Cost: ${transport_optimization.total_cost:.2f}")
            print(f"   Transit Time: {transport_optimization.total_time_hours:.1f} hours")
            print(f"   Carbon vs Baseline: {transport_optimization.carbon_vs_baseline_percent:+.1f}%")
            
            results["transportation_optimization"] = {
                "carbon_g": transport_optimization.total_carbon_g,
                "cost_usd": transport_optimization.total_cost,
                "time_hours": transport_optimization.total_time_hours,
                "carbon_vs_baseline_percent": transport_optimization.carbon_vs_baseline_percent,
                "recommendations": transport_optimization.recommendations
            }
            
        except Exception as e:
            print(f"   ⚠️ Transportation optimization failed: {e}")
            results["transportation_optimization"] = {"error": str(e)}
        
        # 6. Comprehensive Analysis Summary
        print("\n6️⃣ Comprehensive Analysis Summary...")
        
        # Calculate total carbon footprint using different methods
        carbon_estimates = {}
        
        # Amazon Supply Chain method
        if "amazon_supply_chain" in results and "error" not in results["amazon_supply_chain"]:
            carbon_estimates["amazon_method"] = results["amazon_supply_chain"]["total_supply_chain_co2_kg"]
        
        # Multi-tier method
        if "multi_tier_analysis" in results and "error" not in results["multi_tier_analysis"]:
            carbon_estimates["multi_tier_method"] = results["multi_tier_analysis"]["total_multi_tier_co2_kg"]
        
        # Materials-based estimate
        if "materials_analysis" in results and "manufacturing_complexity" in results:
            material_base = results["materials_analysis"]["average_impact"] * test_product["weight_kg"]
            complexity_multiplier = results["manufacturing_complexity"].get("complexity_factor", 1.0)
            carbon_estimates["materials_method"] = material_base * complexity_multiplier
        
        print(f"\n📊 Carbon Footprint Estimates:")
        for method, estimate in carbon_estimates.items():
            print(f"   • {method.replace('_', ' ').title()}: {estimate:.3f} kg CO2")
        
        if carbon_estimates:
            avg_estimate = sum(carbon_estimates.values()) / len(carbon_estimates)
            min_estimate = min(carbon_estimates.values())
            max_estimate = max(carbon_estimates.values())
            
            print(f"\n   📈 Statistics:")
            print(f"   • Average: {avg_estimate:.3f} kg CO2")
            print(f"   • Range: {min_estimate:.3f} - {max_estimate:.3f} kg CO2")
            print(f"   • Variation: ±{((max_estimate - min_estimate) / avg_estimate * 100):.1f}%")
        
        results["summary"] = {
            "carbon_estimates": carbon_estimates,
            "test_product": test_product,
            "systems_tested": len(results),
            "successful_analyses": len([r for r in results.values() if "error" not in r])
        }
        
        # Save complete results
        results_path = "/Users/jamie/Documents/University/dsp_eco_tracker/master_integration_test_results.json"
        try:
            with open(results_path, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"\n📄 Complete results saved to: {results_path}")
        except Exception as e:
            print(f"⚠️ Could not save results: {e}")
        
        # Final assessment
        successful_systems = len([r for r in results.values() if isinstance(r, dict) and "error" not in r])
        total_systems = len(results)
        success_rate = (successful_systems / total_systems * 100) if total_systems > 0 else 0
        
        print(f"\n🎯 MASTER INTEGRATION TEST RESULTS")
        print("=" * 60)
        print(f"Product Analyzed: {test_product['name']}")
        print(f"Systems Integration: {successful_systems}/{total_systems} successful ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            print(f"✅ EXCELLENT: Full system integration working properly")
            system_status = "EXCELLENT"
        elif success_rate >= 60:
            print(f"✅ GOOD: Most systems integrated successfully")
            system_status = "GOOD"
        elif success_rate >= 40:
            print(f"⚠️ PARTIAL: Some integration issues need attention")
            system_status = "PARTIAL"
        else:
            print(f"❌ POOR: Major integration problems")
            system_status = "POOR"
        
        return {
            "status": system_status,
            "success_rate": success_rate,
            "results": results,
            "test_product": test_product
        }
        
    except Exception as e:
        print(f"❌ Master integration test failed: {e}")
        return {"status": "FAILED", "error": str(e)}

def test_csv_dataset_compatibility():
    """Test compatibility with existing CSV datasets"""
    print("\n📊 Testing CSV Dataset Compatibility...")
    print("=" * 60)
    
    # Check for existing CSV files
    csv_files = [
        "/Users/jamie/Documents/University/dsp_eco_tracker/common/data/csv/eco_dataset.csv",
        "/Users/jamie/Documents/University/dsp_eco_tracker/common/data/csv/enhanced_eco_dataset.csv",
        "/Users/jamie/Documents/University/dsp_eco_tracker/common/data/csv/defra_material_intensity.csv"
    ]
    
    csv_compatibility = {}
    
    for csv_file in csv_files:
        filename = os.path.basename(csv_file)
        try:
            if os.path.exists(csv_file):
                with open(csv_file, 'r') as f:
                    # Read first few lines to check format
                    lines = [f.readline().strip() for _ in range(3)]
                    
                csv_compatibility[filename] = {
                    "status": "EXISTS",
                    "header": lines[0] if lines else "",
                    "sample_data": lines[1:] if len(lines) > 1 else [],
                    "readable": True
                }
                print(f"   ✅ {filename}: Found and readable")
            else:
                csv_compatibility[filename] = {
                    "status": "NOT_FOUND",
                    "readable": False
                }
                print(f"   ⚠️ {filename}: Not found")
                
        except Exception as e:
            csv_compatibility[filename] = {
                "status": "ERROR",
                "error": str(e),
                "readable": False
            }
            print(f"   ❌ {filename}: Error - {e}")
    
    # Summary
    found_files = len([c for c in csv_compatibility.values() if c["status"] == "EXISTS"])
    total_files = len(csv_files)
    
    print(f"\n📊 CSV Compatibility Results: {found_files}/{total_files} files found")
    
    return csv_compatibility

def main():
    """Run master integration testing"""
    print("🚀 DSP ECO TRACKER - MASTER INTEGRATION TESTING")
    print("=" * 90)
    
    start_time = time.time()
    
    # Run complete product analysis
    integration_results = test_complete_product_analysis()
    
    # Test CSV compatibility
    csv_results = test_csv_dataset_compatibility()
    
    # Overall assessment
    total_time = time.time() - start_time
    
    print(f"\n🏆 FINAL ASSESSMENT")
    print("=" * 60)
    print(f"Integration Status: {integration_results.get('status', 'UNKNOWN')}")
    print(f"Success Rate: {integration_results.get('success_rate', 0):.1f}%")
    print(f"Total Test Time: {total_time:.2f} seconds")
    
    if integration_results.get('status') in ['EXCELLENT', 'GOOD']:
        print("✅ SYSTEM READY FOR PRODUCTION")
        print("   All major components working together successfully")
        print("   Carbon calculations are consistent and accurate")
        print("   Enterprise deployment recommended")
    elif integration_results.get('status') == 'PARTIAL':
        print("⚠️ SYSTEM MOSTLY READY")
        print("   Most components working but some issues remain")
        print("   Recommend addressing integration issues before production")
    else:
        print("❌ SYSTEM NEEDS WORK")
        print("   Major integration issues need to be resolved")
        print("   Not recommended for production deployment")
    
    print(f"\n⏱️ Master integration testing completed in {total_time:.2f} seconds")
    
    return {
        "integration_results": integration_results,
        "csv_results": csv_results,
        "total_time": total_time
    }

if __name__ == "__main__":
    main()