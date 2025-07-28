#!/usr/bin/env python3
"""
Comprehensive System Stability Testing for DSP Eco Tracker
Tests all new features and existing system compatibility
"""

import sys
import os
import traceback
import json
import time
from typing import Dict, List, Any, Tuple

# Add the services directory to Python path
sys.path.append('/Users/jamie/Documents/University/dsp_eco_tracker/backend/services')

def test_module_imports():
    """Test if all modules can be imported successfully"""
    print("🔍 Testing Module Imports...")
    print("=" * 60)
    
    import_tests = {}
    
    # Test new features
    new_features = [
        "amazon_supply_chain_intelligence",
        "multi_tier_supply_chain_analysis", 
        "transportation_optimization_engine",
        "expanded_amazon_fulfillment_network",
        "ultimate_product_generator"
    ]
    
    # Test existing systems
    existing_systems = [
        "enhanced_materials_database",
        "manufacturing_complexity_multipliers"
    ]
    
    all_modules = new_features + existing_systems
    
    for module_name in all_modules:
        try:
            print(f"  Importing {module_name}...")
            module = __import__(module_name)
            import_tests[module_name] = {
                "status": "SUCCESS",
                "module": module,
                "error": None
            }
            print(f"    ✅ {module_name} imported successfully")
            
        except Exception as e:
            import_tests[module_name] = {
                "status": "FAILED",
                "module": None,
                "error": str(e)
            }
            print(f"    ❌ {module_name} failed: {str(e)}")
    
    success_count = sum(1 for test in import_tests.values() if test["status"] == "SUCCESS")
    total_count = len(import_tests)
    
    print(f"\n📊 Import Test Results: {success_count}/{total_count} successful")
    
    return import_tests

def test_class_initialization():
    """Test if all main classes can be initialized"""
    print("\n🏗️ Testing Class Initialization...")
    print("=" * 60)
    
    # Import modules first
    try:
        from amazon_supply_chain_intelligence import AmazonSupplyChainIntelligence
        from multi_tier_supply_chain_analysis import MultiTierSupplyChainAnalysis
        from transportation_optimization_engine import TransportationOptimizationEngine
        from expanded_amazon_fulfillment_network import ExpandedAmazonFulfillmentNetwork
        from ultimate_product_generator import UltimateProductGenerator
        from enhanced_materials_database import EnhancedMaterialsDatabase
        from manufacturing_complexity_multipliers import ManufacturingComplexityCalculator
    except ImportError as e:
        print(f"❌ Failed to import required modules: {e}")
        return {}
    
    init_tests = {}
    
    # Test class initializations
    test_classes = [
        ("AmazonSupplyChainIntelligence", AmazonSupplyChainIntelligence),
        ("MultiTierSupplyChainAnalysis", MultiTierSupplyChainAnalysis),
        ("TransportationOptimizationEngine", TransportationOptimizationEngine),
        ("ExpandedAmazonFulfillmentNetwork", ExpandedAmazonFulfillmentNetwork),
        ("UltimateProductGenerator", UltimateProductGenerator),
        ("EnhancedMaterialsDatabase", EnhancedMaterialsDatabase),
        ("ManufacturingComplexityCalculator", ManufacturingComplexityCalculator)
    ]
    
    for class_name, class_obj in test_classes:
        try:
            print(f"  Initializing {class_name}...")
            start_time = time.time()
            instance = class_obj()
            init_time = time.time() - start_time
            
            init_tests[class_name] = {
                "status": "SUCCESS",
                "instance": instance,
                "init_time": round(init_time, 3),
                "error": None
            }
            print(f"    ✅ {class_name} initialized in {init_time:.3f}s")
            
        except Exception as e:
            init_tests[class_name] = {
                "status": "FAILED",
                "instance": None,
                "init_time": None,
                "error": str(e)
            }
            print(f"    ❌ {class_name} failed: {str(e)}")
    
    success_count = sum(1 for test in init_tests.values() if test["status"] == "SUCCESS")
    total_count = len(init_tests)
    
    print(f"\n📊 Initialization Test Results: {success_count}/{total_count} successful")
    
    return init_tests

def test_basic_functionality(init_tests):
    """Test basic functionality of each system"""
    print("\n⚡ Testing Basic Functionality...")
    print("=" * 60)
    
    functionality_tests = {}
    
    # Test Amazon Supply Chain Intelligence
    if init_tests.get("AmazonSupplyChainIntelligence", {}).get("status") == "SUCCESS":
        try:
            print("  Testing Amazon Supply Chain Intelligence...")
            sci = init_tests["AmazonSupplyChainIntelligence"]["instance"]
            
            # Test basic emissions calculation
            result = sci.calculate_supply_chain_emissions(
                product_weight_kg=1.0,
                manufacturing_location="china",
                customer_region="uk_london",
                delivery_speed="standard"
            )
            
            # Validate result structure
            assert "total_supply_chain_co2_g" in result
            assert "emissions_breakdown" in result
            assert result["total_supply_chain_co2_g"] > 0
            
            functionality_tests["AmazonSupplyChainIntelligence"] = {
                "status": "SUCCESS",
                "result": result,
                "error": None
            }
            print("    ✅ Amazon Supply Chain Intelligence working correctly")
            
        except Exception as e:
            functionality_tests["AmazonSupplyChainIntelligence"] = {
                "status": "FAILED",
                "result": None,
                "error": str(e)
            }
            print(f"    ❌ Amazon Supply Chain Intelligence failed: {str(e)}")
    
    # Test Multi-Tier Supply Chain Analysis
    if init_tests.get("MultiTierSupplyChainAnalysis", {}).get("status") == "SUCCESS":
        try:
            print("  Testing Multi-Tier Supply Chain Analysis...")
            mtsc = init_tests["MultiTierSupplyChainAnalysis"]["instance"]
            
            from multi_tier_supply_chain_analysis import ManufacturingStrategy
            
            # Test multi-tier analysis
            result = mtsc.analyze_multi_tier_emissions(
                product_category="smartphone",
                product_weight_kg=0.22,
                manufacturing_strategy=ManufacturingStrategy.HYBRID
            )
            
            # Validate result structure
            assert "total_multi_tier_co2_g" in result
            assert "tier_breakdown" in result
            assert result["total_multi_tier_co2_g"] > 0
            
            functionality_tests["MultiTierSupplyChainAnalysis"] = {
                "status": "SUCCESS",
                "result": result,
                "error": None
            }
            print("    ✅ Multi-Tier Supply Chain Analysis working correctly")
            
        except Exception as e:
            functionality_tests["MultiTierSupplyChainAnalysis"] = {
                "status": "FAILED",
                "result": None,
                "error": str(e)
            }
            print(f"    ❌ Multi-Tier Supply Chain Analysis failed: {str(e)}")
    
    # Test Transportation Optimization Engine
    if init_tests.get("TransportationOptimizationEngine", {}).get("status") == "SUCCESS":
        try:
            print("  Testing Transportation Optimization Engine...")
            toe = init_tests["TransportationOptimizationEngine"]["instance"]
            
            from transportation_optimization_engine import CargoType, OptimizationConstraints, UrgencyLevel
            
            # Test route optimization
            constraints = OptimizationConstraints(urgency_level=UrgencyLevel.STANDARD)
            result = toe.optimize_route(
                origin="Shanghai, China",
                destination="London, UK",
                cargo_weight_kg=100,
                cargo_type=CargoType.GENERAL,
                constraints=constraints
            )
            
            # Validate result structure
            assert hasattr(result, 'total_carbon_g')
            assert hasattr(result, 'total_cost')
            assert result.total_carbon_g > 0
            
            functionality_tests["TransportationOptimizationEngine"] = {
                "status": "SUCCESS",
                "result": {
                    "carbon_g": result.total_carbon_g,
                    "cost": result.total_cost,
                    "time_hours": result.total_time_hours
                },
                "error": None
            }
            print("    ✅ Transportation Optimization Engine working correctly")
            
        except Exception as e:
            functionality_tests["TransportationOptimizationEngine"] = {
                "status": "FAILED",
                "result": None,
                "error": str(e)
            }
            print(f"    ❌ Transportation Optimization Engine failed: {str(e)}")
    
    # Test Enhanced Materials Database
    if init_tests.get("EnhancedMaterialsDatabase", {}).get("status") == "SUCCESS":
        try:
            print("  Testing Enhanced Materials Database...")
            emd = init_tests["EnhancedMaterialsDatabase"]["instance"]
            
            # Test material lookup using correct method
            result = emd.get_material_impact_score("aluminum")
            
            # Validate result structure - it returns a float value
            assert isinstance(result, (int, float))
            assert result > 0
            
            functionality_tests["EnhancedMaterialsDatabase"] = {
                "status": "SUCCESS",
                "result": {"co2_score": result},
                "error": None
            }
            print("    ✅ Enhanced Materials Database working correctly")
            
        except Exception as e:
            functionality_tests["EnhancedMaterialsDatabase"] = {
                "status": "FAILED",
                "result": None,
                "error": str(e)
            }
            print(f"    ❌ Enhanced Materials Database failed: {str(e)}")
    
    # Test Manufacturing Complexity Calculator
    if init_tests.get("ManufacturingComplexityCalculator", {}).get("status") == "SUCCESS":
        try:
            print("  Testing Manufacturing Complexity Calculator...")
            mcc = init_tests["ManufacturingComplexityCalculator"]["instance"]
            
            # Test complexity calculation using correct method
            result = mcc.get_manufacturing_complexity("electronics")
            
            # Validate result structure - it returns a dict
            assert isinstance(result, dict)
            assert "complexity_factor" in result
            assert result["complexity_factor"] > 0
            
            functionality_tests["ManufacturingComplexityCalculator"] = {
                "status": "SUCCESS",
                "result": result,
                "error": None
            }
            print("    ✅ Manufacturing Complexity Calculator working correctly")
            
        except Exception as e:
            functionality_tests["ManufacturingComplexityCalculator"] = {
                "status": "FAILED",
                "result": None,
                "error": str(e)
            }
            print(f"    ❌ Manufacturing Complexity Calculator failed: {str(e)}")
    
    success_count = sum(1 for test in functionality_tests.values() if test["status"] == "SUCCESS")
    total_count = len(functionality_tests)
    
    print(f"\n📊 Functionality Test Results: {success_count}/{total_count} successful")
    
    return functionality_tests

def test_integration_compatibility(init_tests):
    """Test integration between different systems"""
    print("\n🔗 Testing Integration Compatibility...")
    print("=" * 60)
    
    integration_tests = {}
    
    # Test Ultimate Product Generator with other systems
    if (init_tests.get("UltimateProductGenerator", {}).get("status") == "SUCCESS" and
        init_tests.get("EnhancedMaterialsDatabase", {}).get("status") == "SUCCESS" and
        init_tests.get("ManufacturingComplexityCalculator", {}).get("status") == "SUCCESS"):
        
        try:
            print("  Testing Ultimate Product Generator integration...")
            upg = init_tests["UltimateProductGenerator"]["instance"]
            
            # Test that it can access other systems
            materials_db = upg.materials_db
            complexity_calc = upg.complexity_calculator
            
            # Verify they are properly initialized
            assert materials_db is not None
            assert complexity_calc is not None
            
            integration_tests["UltimateProductGenerator_Integration"] = {
                "status": "SUCCESS",
                "details": "Successfully integrated with materials database and complexity calculator",
                "error": None
            }
            print("    ✅ Ultimate Product Generator integration working")
            
        except Exception as e:
            integration_tests["UltimateProductGenerator_Integration"] = {
                "status": "FAILED",
                "details": None,
                "error": str(e)
            }
            print(f"    ❌ Ultimate Product Generator integration failed: {str(e)}")
    
    # Test cross-system data compatibility
    try:
        print("  Testing cross-system data compatibility...")
        
        # Test that different systems can handle the same product data
        test_product_data = {
            "name": "Test Product",
            "weight_kg": 1.0,
            "materials": ["aluminum", "plastic"],
            "category": "electronics",
            "manufacturing_location": "china"
        }
        
        compatible_systems = []
        
        # Test with Enhanced Materials Database
        if init_tests.get("EnhancedMaterialsDatabase", {}).get("status") == "SUCCESS":
            emd = init_tests["EnhancedMaterialsDatabase"]["instance"]
            try:
                for material in test_product_data["materials"]:
                    material_data = emd.get_material_impact_score(material)
                    assert material_data is not None
                compatible_systems.append("EnhancedMaterialsDatabase")
            except:
                pass
        
        # Test with Manufacturing Complexity Calculator
        if init_tests.get("ManufacturingComplexityCalculator", {}).get("status") == "SUCCESS":
            mcc = init_tests["ManufacturingComplexityCalculator"]["instance"]
            try:
                complexity = mcc.get_manufacturing_complexity(
                    test_product_data["category"]
                )
                assert complexity is not None
                compatible_systems.append("ManufacturingComplexityCalculator")
            except:
                pass
        
        integration_tests["CrossSystemCompatibility"] = {
            "status": "SUCCESS" if len(compatible_systems) >= 2 else "PARTIAL",
            "compatible_systems": compatible_systems,
            "error": None
        }
        
        if len(compatible_systems) >= 2:
            print(f"    ✅ Cross-system compatibility working ({len(compatible_systems)} systems compatible)")
        else:
            print(f"    ⚠️ Partial cross-system compatibility ({len(compatible_systems)} systems compatible)")
            
    except Exception as e:
        integration_tests["CrossSystemCompatibility"] = {
            "status": "FAILED", 
            "compatible_systems": [],
            "error": str(e)
        }
        print(f"    ❌ Cross-system compatibility failed: {str(e)}")
    
    success_count = sum(1 for test in integration_tests.values() if test["status"] == "SUCCESS")
    total_count = len(integration_tests)
    
    print(f"\n📊 Integration Test Results: {success_count}/{total_count} successful")
    
    return integration_tests

def test_performance_and_memory():
    """Test performance and memory efficiency"""
    print("\n⚡ Testing Performance and Memory Efficiency...")
    print("=" * 60)
    
    performance_tests = {}
    
    try:
        import psutil
        import gc
        
        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        print(f"  Initial memory usage: {initial_memory:.1f} MB")
        
        # Test multiple product generation cycles
        print("  Testing multiple calculation cycles...")
        
        start_time = time.time()
        calculation_count = 0
        
        # Try to import and use systems
        try:
            from enhanced_materials_database import EnhancedMaterialsDatabase
            from manufacturing_complexity_multipliers import ManufacturingComplexityCalculator
            
            emd = EnhancedMaterialsDatabase()
            mcc = ManufacturingComplexityCalculator()
            
            # Run multiple calculations
            for i in range(10):
                # Material impact calculations
                materials = ["aluminum", "plastic", "steel", "copper"]
                for material in materials:
                    try:
                        result = emd.get_material_impact_score(material)
                        calculation_count += 1
                    except:
                        pass
                
                # Complexity calculations
                try:
                    complexity = mcc.get_manufacturing_complexity("electronics")
                    calculation_count += 1
                except:
                    pass
            
            end_time = time.time()
            calculation_time = end_time - start_time
            
            # Check final memory usage
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            # Run garbage collection
            gc.collect()
            
            performance_tests["PerformanceAndMemory"] = {
                "status": "SUCCESS",
                "calculations_per_second": round(calculation_count / calculation_time, 2),
                "total_calculations": calculation_count,
                "total_time": round(calculation_time, 3),
                "initial_memory_mb": round(initial_memory, 1),
                "final_memory_mb": round(final_memory, 1),
                "memory_increase_mb": round(memory_increase, 1),
                "error": None
            }
            
            print(f"    ✅ Performance test completed:")
            print(f"      • {calculation_count} calculations in {calculation_time:.3f}s")
            print(f"      • {calculation_count / calculation_time:.1f} calculations/second")
            print(f"      • Memory increase: {memory_increase:.1f} MB")
            
        except ImportError:
            performance_tests["PerformanceAndMemory"] = {
                "status": "SKIPPED",
                "error": "Required modules not available for performance testing"
            }
            print("    ⚠️ Performance test skipped - modules not available")
            
    except ImportError:
        performance_tests["PerformanceAndMemory"] = {
            "status": "SKIPPED",
            "error": "psutil not available for memory testing"
        }
        print("    ⚠️ Performance test skipped - psutil not available")
    
    except Exception as e:
        performance_tests["PerformanceAndMemory"] = {
            "status": "FAILED",
            "error": str(e)
        }
        print(f"    ❌ Performance test failed: {str(e)}")
    
    return performance_tests

def test_error_handling():
    """Test error handling and edge cases"""
    print("\n🛡️ Testing Error Handling...")
    print("=" * 60)
    
    error_tests = {}
    
    # Test invalid inputs
    try:
        from enhanced_materials_database import EnhancedMaterialsDatabase
        
        print("  Testing invalid material lookup...")
        emd = EnhancedMaterialsDatabase()
        
        # Test with invalid material
        try:
            result = emd.get_material_impact_score("nonexistent_material_xyz")
            if result is None or "error" in str(result).lower():
                error_tests["InvalidMaterialHandling"] = {
                    "status": "SUCCESS",
                    "details": "Properly handles invalid material names",
                    "error": None
                }
                print("    ✅ Invalid material handling working correctly")
            else:
                error_tests["InvalidMaterialHandling"] = {
                    "status": "PARTIAL",
                    "details": "Returns result for invalid material (may use fallback)",
                    "error": None
                }
                print("    ⚠️ Invalid material handling uses fallback")
        except Exception as e:
            error_tests["InvalidMaterialHandling"] = {
                "status": "FAILED",
                "details": None,
                "error": str(e)
            }
            print(f"    ❌ Invalid material handling failed: {str(e)}")
            
    except ImportError:
        error_tests["InvalidMaterialHandling"] = {
            "status": "SKIPPED",
            "error": "EnhancedMaterialsDatabase not available"
        }
        print("    ⚠️ Error handling test skipped - module not available")
    
    # Test edge case inputs
    try:
        from manufacturing_complexity_multipliers import ManufacturingComplexityCalculator
        
        print("  Testing edge case complexity calculations...")
        mcc = ManufacturingComplexityCalculator()
        
        # Test with invalid category
        try:
            result = mcc.get_manufacturing_complexity("nonexistent_category")
            error_tests["EmptyMaterialsHandling"] = {
                "status": "SUCCESS",
                "details": "Handles invalid category properly",
                "error": None
            }
            print("    ✅ Invalid category handling working")
        except Exception as e:
            error_tests["EmptyMaterialsHandling"] = {
                "status": "FAILED",
                "details": None,
                "error": str(e)
            }
            print(f"    ❌ Invalid category handling failed: {str(e)}")
            
    except ImportError:
        error_tests["EmptyMaterialsHandling"] = {
            "status": "SKIPPED",
            "error": "ManufacturingComplexityCalculator not available"
        }
        print("    ⚠️ Edge case test skipped - module not available")
    
    success_count = sum(1 for test in error_tests.values() if test["status"] == "SUCCESS")
    total_count = len(error_tests)
    
    print(f"\n📊 Error Handling Test Results: {success_count}/{total_count} successful")
    
    return error_tests

def generate_comprehensive_report(import_tests, init_tests, functionality_tests, 
                                integration_tests, performance_tests, error_tests):
    """Generate comprehensive test report"""
    print("\n📋 Generating Comprehensive Report...")
    print("=" * 60)
    
    # Calculate overall statistics
    all_tests = {
        "imports": import_tests,
        "initialization": init_tests,
        "functionality": functionality_tests,
        "integration": integration_tests,
        "performance": performance_tests,
        "error_handling": error_tests
    }
    
    total_success = 0
    total_tests = 0
    
    category_results = {}
    
    for category, tests in all_tests.items():
        success = sum(1 for test in tests.values() if test.get("status") == "SUCCESS")
        total = len(tests)
        category_results[category] = {
            "success": success,
            "total": total,
            "success_rate": round((success / total * 100) if total > 0 else 0, 1)
        }
        total_success += success
        total_tests += total
    
    overall_success_rate = round((total_success / total_tests * 100) if total_tests > 0 else 0, 1)
    
    # Generate detailed report
    report = {
        "test_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "overall_results": {
            "total_tests": total_tests,
            "successful_tests": total_success,
            "success_rate_percent": overall_success_rate,
            "system_status": "STABLE" if overall_success_rate >= 80 else "UNSTABLE"
        },
        "category_results": category_results,
        "detailed_results": all_tests,
        "recommendations": []
    }
    
    # Generate recommendations
    if overall_success_rate >= 90:
        report["recommendations"].append("✅ System is highly stable and ready for production")
    elif overall_success_rate >= 80:
        report["recommendations"].append("⚠️ System is mostly stable with minor issues to address")
    elif overall_success_rate >= 60:
        report["recommendations"].append("🔧 System needs significant improvements before production")
    else:
        report["recommendations"].append("❌ System is unstable and requires major fixes")
    
    # Add specific recommendations based on test results
    if category_results["imports"]["success_rate"] < 100:
        report["recommendations"].append("🔍 Fix import issues - check dependencies and file paths")
    
    if category_results["functionality"]["success_rate"] < 80:
        report["recommendations"].append("⚡ Address functionality issues in failing components")
    
    if category_results["integration"]["success_rate"] < 80:
        report["recommendations"].append("🔗 Improve integration between system components")
    
    # Save report to file
    report_path = "/Users/jamie/Documents/University/dsp_eco_tracker/system_stability_test_report.json"
    try:
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"📄 Detailed report saved to: {report_path}")
    except Exception as e:
        print(f"⚠️ Could not save report: {e}")
    
    # Print summary
    print(f"\n🎯 COMPREHENSIVE TEST SUMMARY")
    print("=" * 60)
    print(f"Overall Success Rate: {overall_success_rate}% ({total_success}/{total_tests})")
    print(f"System Status: {report['overall_results']['system_status']}")
    
    print(f"\nCategory Breakdown:")
    for category, results in category_results.items():
        status_icon = "✅" if results["success_rate"] >= 80 else "⚠️" if results["success_rate"] >= 60 else "❌"
        print(f"  {status_icon} {category.title()}: {results['success_rate']}% ({results['success']}/{results['total']})")
    
    print(f"\nRecommendations:")
    for rec in report["recommendations"]:
        print(f"  {rec}")
    
    return report

def main():
    """Run comprehensive system stability testing"""
    print("🚀 DSP ECO TRACKER - COMPREHENSIVE SYSTEM STABILITY TESTING")
    print("=" * 90)
    print("Testing all new features and existing system compatibility")
    print("=" * 90)
    
    start_time = time.time()
    
    # Run all tests
    import_tests = test_module_imports()
    init_tests = test_class_initialization()
    functionality_tests = test_basic_functionality(init_tests)
    integration_tests = test_integration_compatibility(init_tests)
    performance_tests = test_performance_and_memory()
    error_tests = test_error_handling()
    
    # Generate comprehensive report
    report = generate_comprehensive_report(
        import_tests, init_tests, functionality_tests,
        integration_tests, performance_tests, error_tests
    )
    
    total_time = time.time() - start_time
    
    print(f"\n⏱️ Total testing time: {total_time:.2f} seconds")
    print("🏁 Comprehensive system stability testing completed!")
    
    return report

if __name__ == "__main__":
    main()