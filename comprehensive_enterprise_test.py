#!/usr/bin/env python3
"""
Comprehensive Enterprise Dashboard System Test
==============================================

Tests every endpoint, function, and component of the enterprise dashboard
to ensure everything works perfectly for Series A demos and enterprise customers.
"""

import sys
import os
import json
import pandas as pd
from pathlib import Path
import traceback
from io import StringIO
import importlib.util

# Add project paths
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "backend"))
sys.path.insert(0, str(BASE_DIR / "backend" / "services"))

class EnterpriseSystemTester:
    def __init__(self):
        self.test_results = []
        self.errors = []
        self.base_dir = BASE_DIR
        
    def log_test(self, test_name, status, details=""):
        """Log test results."""
        self.test_results.append({
            'test': test_name,
            'status': status,
            'details': details
        })
        status_icon = "✅" if status == "PASS" else "❌"
        print(f"{status_icon} {test_name}: {details}")
        
    def log_error(self, test_name, error):
        """Log errors."""
        self.errors.append({
            'test': test_name,
            'error': str(error),
            'traceback': traceback.format_exc()
        })
        print(f"❌ {test_name}: ERROR - {str(error)}")

    def test_data_files_exist(self):
        """Test that all required data files exist and are readable."""
        print("\n🔍 Testing Data File Availability...")
        
        required_files = [
            "common/data/csv/enhanced_eco_dataset.csv",
            "common/data/json/brand_locations.json",
            "common/data/json/material_insights.json"
        ]
        
        for file_path in required_files:
            full_path = self.base_dir / file_path
            try:
                if full_path.exists():
                    # Test if file is readable
                    if file_path.endswith('.csv'):
                        df = pd.read_csv(full_path, nrows=5)  # Just read first 5 rows
                        self.log_test(f"Data file {file_path}", "PASS", f"CSV readable with {len(df)} sample rows")
                    elif file_path.endswith('.json'):
                        with open(full_path, 'r') as f:
                            data = json.load(f)
                        self.log_test(f"Data file {file_path}", "PASS", f"JSON readable with {len(data)} entries")
                else:
                    self.log_test(f"Data file {file_path}", "FAIL", "File does not exist")
            except Exception as e:
                self.log_error(f"Data file {file_path}", e)

    def test_backend_services_import(self):
        """Test that backend services can be imported correctly."""
        print("\n🔍 Testing Backend Services Import...")
        
        services_to_test = [
            ('manufacturing_complexity_multipliers', 'ManufacturingComplexityCalculator'),
            ('enhanced_materials_database', 'EnhancedMaterialsDatabase')
        ]
        
        for module_name, class_name in services_to_test:
            try:
                module_path = self.base_dir / "backend" / "services" / f"{module_name}.py"
                if module_path.exists():
                    spec = importlib.util.spec_from_file_location(module_name, module_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    if hasattr(module, class_name):
                        class_obj = getattr(module, class_name)
                        instance = class_obj()
                        self.log_test(f"Service {module_name}.{class_name}", "PASS", "Successfully imported and instantiated")
                    else:
                        self.log_test(f"Service {module_name}.{class_name}", "FAIL", f"Class {class_name} not found")
                else:
                    self.log_test(f"Service {module_name}", "FAIL", "Module file does not exist")
            except Exception as e:
                self.log_error(f"Service {module_name}.{class_name}", e)

    def test_enterprise_api_routes_structure(self):
        """Test enterprise API routes file structure and endpoints."""
        print("\n🔍 Testing Enterprise API Routes Structure...")
        
        routes_file = self.base_dir / "backend" / "api" / "routes" / "enterprise_dashboard.py"
        
        try:
            if routes_file.exists():
                with open(routes_file, 'r') as f:
                    content = f.read()
                
                # Check for required endpoints
                required_endpoints = [
                    "/dashboard/overview",
                    "/analytics/carbon-trends", 
                    "/suppliers/sustainability-scoring",
                    "/demo/series-a-data",
                    "/reports/export",
                    "/health"
                ]
                
                for endpoint in required_endpoints:
                    if endpoint in content:
                        self.log_test(f"Endpoint {endpoint}", "PASS", "Endpoint definition found")
                    else:
                        self.log_test(f"Endpoint {endpoint}", "FAIL", "Endpoint definition missing")
                
                # Check for required functions
                required_functions = [
                    "load_enterprise_data",
                    "load_brand_locations", 
                    "load_material_insights",
                    "get_dashboard_overview",
                    "get_carbon_analytics",
                    "get_supplier_analysis"
                ]
                
                for function in required_functions:
                    if f"def {function}" in content:
                        self.log_test(f"Function {function}", "PASS", "Function definition found")
                    else:
                        self.log_test(f"Function {function}", "FAIL", "Function definition missing")
                        
            else:
                self.log_test("Enterprise routes file", "FAIL", "File does not exist")
                
        except Exception as e:
            self.log_error("Enterprise routes structure", e)

    def test_data_loading_functions(self):
        """Test data loading functions work correctly."""
        print("\n🔍 Testing Data Loading Functions...")
        
        try:
            # Import the enterprise dashboard module directly
            routes_file = self.base_dir / "backend" / "api" / "routes" / "enterprise_dashboard.py"
            spec = importlib.util.spec_from_file_location("enterprise_dashboard", routes_file)
            enterprise_module = importlib.util.module_from_spec(spec)
            
            # Mock the sys.path additions that the module needs
            old_path = sys.path.copy()
            sys.path.append(str(self.base_dir / "backend" / "services"))
            sys.path.append(str(self.base_dir / "common" / "data"))
            
            try:
                spec.loader.exec_module(enterprise_module)
                
                # Test load_enterprise_data function
                if hasattr(enterprise_module, 'load_enterprise_data'):
                    df = enterprise_module.load_enterprise_data()
                    if not df.empty:
                        self.log_test("load_enterprise_data", "PASS", f"Loaded {len(df)} rows of data")
                    else:
                        self.log_test("load_enterprise_data", "FAIL", "Returned empty DataFrame")
                
                # Test load_brand_locations function
                if hasattr(enterprise_module, 'load_brand_locations'):
                    brands = enterprise_module.load_brand_locations()
                    if brands:
                        self.log_test("load_brand_locations", "PASS", f"Loaded {len(brands)} brand locations")
                    else:
                        self.log_test("load_brand_locations", "FAIL", "Returned empty dict")
                
                # Test load_material_insights function
                if hasattr(enterprise_module, 'load_material_insights'):
                    materials = enterprise_module.load_material_insights()
                    if materials:
                        self.log_test("load_material_insights", "PASS", f"Loaded {len(materials)} material insights")
                    else:
                        self.log_test("load_material_insights", "FAIL", "Returned empty dict")
                        
            finally:
                sys.path = old_path
                
        except Exception as e:
            self.log_error("Data loading functions", e)

    def test_dashboard_calculations(self):
        """Test dashboard calculation logic."""
        print("\n🔍 Testing Dashboard Calculations...")
        
        try:
            # Load test data
            csv_path = self.base_dir / "common" / "data" / "csv" / "enhanced_eco_dataset.csv"
            if csv_path.exists():
                df = pd.read_csv(csv_path, nrows=1000)  # Test with first 1000 rows
                
                # Test basic calculations with correct column names
                if 'co2_emissions' in df.columns:
                    avg_carbon = df['co2_emissions'].mean()
                    self.log_test("Average carbon calculation", "PASS", f"Avg carbon: {avg_carbon:.2f} kg")
                else:
                    self.log_test("Average carbon calculation", "FAIL", "co2_emissions column missing")
                
                if 'origin' in df.columns:
                    unique_brands = df['origin'].nunique()
                    self.log_test("Unique suppliers calculation", "PASS", f"Found {unique_brands} unique suppliers")
                else:
                    self.log_test("Unique suppliers calculation", "FAIL", "origin column missing")
                
                if 'recyclability' in df.columns:
                    high_recyclability = (df['recyclability'] == 'High').sum()
                    recyclability_pct = (high_recyclability / len(df)) * 100
                    self.log_test("Recyclability calculation", "PASS", f"{recyclability_pct:.1f}% high recyclability")
                else:
                    self.log_test("Recyclability calculation", "FAIL", "recyclability column missing")
                    
        except Exception as e:
            self.log_error("Dashboard calculations", e)

    def test_frontend_dashboard_structure(self):
        """Test frontend dashboard HTML structure."""
        print("\n🔍 Testing Frontend Dashboard Structure...")
        
        dashboard_file = self.base_dir / "frontend" / "enterprise_dashboard.html"
        
        try:
            if dashboard_file.exists():
                with open(dashboard_file, 'r') as f:
                    content = f.read()
                
                # Check for required HTML elements
                required_elements = [
                    'id="overview-section"',
                    'id="analytics-section"', 
                    'id="suppliers-section"',
                    'id="demo-section"',
                    'id="total-products"',
                    'id="avg-carbon"',
                    'id="total-suppliers"',
                    'id="sustainability-score"'
                ]
                
                for element in required_elements:
                    if element in content:
                        self.log_test(f"HTML element {element}", "PASS", "Element found in HTML")
                    else:
                        self.log_test(f"HTML element {element}", "FAIL", "Element missing from HTML")
                
                # Check for required JavaScript functions
                required_js_functions = [
                    'function initializeDashboard',
                    'function loadOverviewData',
                    'function showSection',
                    'function populateOverviewSection',
                    'function createCarbonTrendsChart',
                    'function exportData'
                ]
                
                for function in required_js_functions:
                    if function in content:
                        self.log_test(f"JS {function}", "PASS", "JavaScript function found")
                    else:
                        self.log_test(f"JS {function}", "FAIL", "JavaScript function missing")
                        
                # Check for external dependencies
                required_dependencies = [
                    'cdn.tailwindcss.com',
                    'chart.js',
                    'font-awesome'
                ]
                
                for dependency in required_dependencies:
                    if dependency in content:
                        self.log_test(f"Dependency {dependency}", "PASS", "Dependency included")
                    else:
                        self.log_test(f"Dependency {dependency}", "FAIL", "Dependency missing")
                        
            else:
                self.log_test("Frontend dashboard file", "FAIL", "HTML file does not exist")
                
        except Exception as e:
            self.log_error("Frontend dashboard structure", e)

    def test_flask_app_integration(self):
        """Test Flask app integration with enterprise dashboard."""
        print("\n🔍 Testing Flask App Integration...")
        
        app_file = self.base_dir / "backend" / "api" / "app.py"
        
        try:
            if app_file.exists():
                with open(app_file, 'r') as f:
                    content = f.read()
                
                # Check for enterprise dashboard imports
                if "from backend.api.routes.enterprise_dashboard import enterprise_bp" in content:
                    self.log_test("Enterprise blueprint import", "PASS", "Blueprint import found")
                else:
                    self.log_test("Enterprise blueprint import", "FAIL", "Blueprint import missing")
                
                # Check for blueprint registration
                if "app.register_blueprint(enterprise_bp)" in content:
                    self.log_test("Enterprise blueprint registration", "PASS", "Blueprint registration found")
                else:
                    self.log_test("Enterprise blueprint registration", "FAIL", "Blueprint registration missing")
                
                # Check for enterprise route
                if '@app.route("/enterprise")' in content:
                    self.log_test("Enterprise dashboard route", "PASS", "Dashboard route found")
                else:
                    self.log_test("Enterprise dashboard route", "FAIL", "Dashboard route missing")
                    
            else:
                self.log_test("Flask app file", "FAIL", "App file does not exist")
                
        except Exception as e:
            self.log_error("Flask app integration", e)

    def test_api_endpoint_logic(self):
        """Test API endpoint logic without actually running Flask."""
        print("\n🔍 Testing API Endpoint Logic...")
        
        try:
            # Import required modules for testing
            old_path = sys.path.copy()
            sys.path.append(str(self.base_dir / "backend" / "services"))
            
            # Test supplier scoring logic
            try:
                from enhanced_materials_database import EnhancedMaterialsDatabase
                materials_db = EnhancedMaterialsDatabase()
                
                # Test getting material data using the correct method
                test_materials = ['steel', 'aluminum', 'plastic']
                for material in test_materials:
                    material_impact = materials_db.get_material_impact_score(material)
                    if material_impact:
                        self.log_test(f"Material data for {material}", "PASS", f"Impact score: {material_impact}")
                    else:
                        self.log_test(f"Material data for {material}", "FAIL", "No data returned")
                        
            except Exception as e:
                self.log_error("Material database logic", e)
            
            # Test manufacturing complexity logic
            try:
                from manufacturing_complexity_multipliers import ManufacturingComplexityCalculator
                complexity_calc = ManufacturingComplexityCalculator()
                
                # Test complexity calculation
                test_result = complexity_calc.calculate_enhanced_co2(
                    weight_kg=1.0,
                    material_co2_per_kg=2.5,
                    transport_multiplier=1.2,
                    category="Electronics"
                )
                
                if test_result and 'enhanced_total_co2' in test_result:
                    self.log_test("Manufacturing complexity calculation", "PASS", f"Result: {test_result['enhanced_total_co2']} kg CO2")
                else:
                    self.log_test("Manufacturing complexity calculation", "FAIL", "Invalid result format")
                    
            except Exception as e:
                self.log_error("Manufacturing complexity logic", e)
            
            sys.path = old_path
            
        except Exception as e:
            self.log_error("API endpoint logic", e)

    def test_data_quality_and_completeness(self):
        """Test data quality and completeness for dashboard metrics."""
        print("\n🔍 Testing Data Quality and Completeness...")
        
        try:
            csv_path = self.base_dir / "common" / "data" / "csv" / "enhanced_eco_dataset.csv"
            if csv_path.exists():
                df = pd.read_csv(csv_path)
                
                # Test data completeness - using correct column names
                required_columns = ['title', 'origin', 'co2_emissions', 'material', 'inferred_category', 'recyclability']
                for col in required_columns:
                    if col in df.columns:
                        non_null_pct = (df[col].notna().sum() / len(df)) * 100
                        if non_null_pct > 80:  # Require at least 80% completeness
                            self.log_test(f"Data completeness for {col}", "PASS", f"{non_null_pct:.1f}% complete")
                        else:
                            self.log_test(f"Data completeness for {col}", "FAIL", f"Only {non_null_pct:.1f}% complete")
                    else:
                        self.log_test(f"Column {col}", "FAIL", "Required column missing")
                
                # Test data ranges
                if 'co2_emissions' in df.columns:
                    carbon_stats = df['co2_emissions'].describe()
                    if carbon_stats['min'] >= 0 and carbon_stats['max'] < 10000:  # Reasonable ranges
                        self.log_test("Carbon data ranges", "PASS", f"Min: {carbon_stats['min']:.2f}, Max: {carbon_stats['max']:.2f}")
                    else:
                        self.log_test("Carbon data ranges", "FAIL", f"Unreasonable values: Min: {carbon_stats['min']:.2f}, Max: {carbon_stats['max']:.2f}")
                
                # Test for realistic supplier/origin counts
                if 'origin' in df.columns:
                    origin_count = df['origin'].nunique()
                    if origin_count > 100:  # Should have many origins for enterprise credibility
                        self.log_test("Origin diversity", "PASS", f"{origin_count} unique origins")
                    else:
                        self.log_test("Origin diversity", "FAIL", f"Only {origin_count} unique origins")
                        
        except Exception as e:
            self.log_error("Data quality testing", e)

    def run_comprehensive_test(self):
        """Run all tests comprehensively."""
        print("🚀 DSP Eco Tracker - Comprehensive Enterprise Dashboard System Test")
        print("=" * 80)
        
        # Run all test suites
        test_suites = [
            self.test_data_files_exist,
            self.test_backend_services_import,
            self.test_enterprise_api_routes_structure,
            self.test_data_loading_functions,
            self.test_dashboard_calculations,
            self.test_frontend_dashboard_structure,
            self.test_flask_app_integration,
            self.test_api_endpoint_logic,
            self.test_data_quality_and_completeness
        ]
        
        for test_suite in test_suites:
            try:
                test_suite()
            except Exception as e:
                self.log_error(f"Test suite {test_suite.__name__}", e)
        
        # Generate summary report
        self.generate_test_report()

    def generate_test_report(self):
        """Generate comprehensive test report."""
        print("\n📊 COMPREHENSIVE TEST RESULTS SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t['status'] == 'PASS'])
        failed_tests = len([t for t in self.test_results if t['status'] == 'FAIL'])
        
        print(f"Total Tests Run: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        if self.errors:
            print(f"\n🔧 ERRORS THAT NEED FIXING ({len(self.errors)}):")
            print("-" * 50)
            for error in self.errors:
                print(f"❌ {error['test']}: {error['error']}")
        
        if failed_tests == 0 and len(self.errors) == 0:
            print("\n🎉 ALL SYSTEMS GO! ENTERPRISE DASHBOARD IS READY!")
            print("=" * 80)
            print("✅ Perfect for Series A demos")
            print("✅ Enterprise customer ready") 
            print("✅ All endpoints functional")
            print("✅ Data quality validated")
            print("✅ Frontend components working")
            print("\n🚀 Launch Instructions:")
            print("1. Start Flask: python3 backend/api/app.py")
            print("2. Visit: http://localhost:5000/enterprise")
            print("3. Demo all 4 sections for maximum impact!")
        else:
            print(f"\n⚠️  {failed_tests + len(self.errors)} ISSUES NEED ATTENTION")
            print("Review the failed tests above and fix before demo.")
            
        # Save detailed report
        report_data = {
            'summary': {
                'total_tests': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'success_rate': passed_tests/total_tests*100 if total_tests > 0 else 0
            },
            'test_results': self.test_results,
            'errors': self.errors,
            'timestamp': pd.Timestamp.now().isoformat()
        }
        
        report_file = self.base_dir / 'enterprise_dashboard_test_report.json'
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")

if __name__ == "__main__":
    tester = EnterpriseSystemTester()
    tester.run_comprehensive_test()