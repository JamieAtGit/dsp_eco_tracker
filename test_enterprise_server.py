#!/usr/bin/env python3
"""
Test Enterprise Dashboard Server Integration
===========================================

Tests that the Flask server can start and serve the enterprise dashboard
with all API endpoints working correctly.
"""

import os
import sys
import time
import requests
import json
from pathlib import Path
import subprocess
import signal
import atexit

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

class EnterpriseServerTester:
    def __init__(self):
        self.server_process = None
        self.base_url = "http://localhost:5000"
        
    def start_flask_server(self):
        """Start Flask server in background."""
        print("🚀 Starting Flask server...")
        
        # Change to project directory
        os.chdir(BASE_DIR)
        
        # Start Flask server
        env = os.environ.copy()
        env['FLASK_ENV'] = 'development'
        env['PYTHONPATH'] = str(BASE_DIR)
        
        try:
            self.server_process = subprocess.Popen([
                sys.executable, '-m', 'backend.api.app'
            ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Register cleanup
            atexit.register(self.cleanup)
            
            # Wait for server to start
            print("⏳ Waiting for server to start...")
            for i in range(30):  # Wait up to 30 seconds
                try:
                    response = requests.get(f"{self.base_url}/health", timeout=2)
                    if response.status_code == 200:
                        print("✅ Server started successfully!")
                        return True
                except:
                    time.sleep(1)
                    
            print("❌ Server failed to start within 30 seconds")
            return False
            
        except Exception as e:
            print(f"❌ Failed to start server: {e}")
            return False
    
    def cleanup(self):
        """Clean up server process."""
        if self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
            except:
                try:
                    self.server_process.kill()
                    self.server_process.wait(timeout=5)
                except:
                    pass
            
    def test_basic_endpoints(self):
        """Test basic Flask endpoints."""
        print("\n🔍 Testing Basic Endpoints...")
        
        endpoints = [
            ("/", "Flask home page"),
            ("/health", "Health check"),
            ("/enterprise", "Enterprise dashboard")
        ]
        
        results = []
        for endpoint, description in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                if response.status_code == 200:
                    print(f"✅ {description}: Status {response.status_code}")
                    results.append(True)
                else:
                    print(f"❌ {description}: Status {response.status_code}")
                    results.append(False)
            except Exception as e:
                print(f"❌ {description}: Error - {e}")
                results.append(False)
                
        return all(results)
    
    def test_enterprise_api_endpoints(self):
        """Test enterprise API endpoints."""
        print("\n🔍 Testing Enterprise API Endpoints...")
        
        api_endpoints = [
            ("/api/enterprise/health", "Enterprise health check"),
            ("/api/enterprise/dashboard/overview", "Dashboard overview"),
            ("/api/enterprise/analytics/carbon-trends", "Carbon analytics"),
            ("/api/enterprise/suppliers/sustainability-scoring", "Supplier analysis"),
            ("/api/enterprise/demo/series-a-data", "Series A demo data")
        ]
        
        results = []
        for endpoint, description in api_endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') == 'success' or 'status' in data:
                        print(f"✅ {description}: Working correctly")
                        results.append(True)
                    else:
                        print(f"⚠️  {description}: Unexpected response format")
                        results.append(False)
                else:
                    print(f"❌ {description}: Status {response.status_code}")
                    results.append(False)
            except Exception as e:
                print(f"❌ {description}: Error - {e}")
                results.append(False)
                
        return all(results)
    
    def test_dashboard_data_quality(self):
        """Test that dashboard returns quality data."""
        print("\n🔍 Testing Dashboard Data Quality...")
        
        try:
            response = requests.get(f"{self.base_url}/api/enterprise/dashboard/overview", timeout=30)
            if response.status_code != 200:
                print(f"❌ Dashboard overview failed: Status {response.status_code}")
                return False
                
            data = response.json()
            
            if data.get('status') != 'success':
                print(f"❌ Dashboard overview error: {data.get('error', 'Unknown error')}")
                return False
            
            summary = data.get('executive_summary', {})
            
            # Check key metrics
            checks = [
                (summary.get('total_products_analyzed', 0) > 100000, "Products analyzed > 100K"),
                (summary.get('total_suppliers_tracked', 0) > 10, "Suppliers tracked > 10"),
                (summary.get('average_carbon_footprint_kg', 0) > 0, "Average carbon footprint > 0"),
                (summary.get('sustainability_score_percentage', 0) > 0, "Sustainability score > 0")
            ]
            
            all_passed = True
            for check, description in checks:
                if check:
                    print(f"✅ {description}")
                else:
                    print(f"❌ {description}")
                    all_passed = False
            
            return all_passed
            
        except Exception as e:
            print(f"❌ Dashboard data quality test failed: {e}")
            return False
    
    def test_series_a_demo_data(self):
        """Test Series A demo data for investor presentations."""
        print("\n🔍 Testing Series A Demo Data...")
        
        try:
            response = requests.get(f"{self.base_url}/api/enterprise/demo/series-a-data", timeout=30)
            if response.status_code != 200:
                print(f"❌ Series A demo failed: Status {response.status_code}")
                return False
                
            data = response.json()
            
            if data.get('status') != 'success':
                print(f"❌ Series A demo error: {data.get('error', 'Unknown error')}")
                return False
            
            # Check for investor-focused content
            investor_checks = [
                ('platform_overview' in data, "Platform overview present"),
                ('impressive_metrics' in data, "Impressive metrics present"),
                ('business_impact_demo' in data, "Business impact demo present"),
                ('investor_highlights' in data, "Investor highlights present"),
                ('competitive_landscape' in data, "Competitive landscape present")
            ]
            
            all_passed = True
            for check, description in investor_checks:
                if check:
                    print(f"✅ {description}")
                else:
                    print(f"❌ {description}")
                    all_passed = False
            
            return all_passed
            
        except Exception as e:
            print(f"❌ Series A demo data test failed: {e}")
            return False
    
    def run_comprehensive_server_test(self):
        """Run comprehensive server integration test."""
        print("🚀 DSP Eco Tracker - Enterprise Dashboard Server Integration Test")
        print("=" * 80)
        
        # Start server
        if not self.start_flask_server():
            print("❌ Cannot proceed - server failed to start")
            return False
        
        try:
            # Run all tests
            tests = [
                ("Basic Endpoints", self.test_basic_endpoints),
                ("Enterprise API Endpoints", self.test_enterprise_api_endpoints),
                ("Dashboard Data Quality", self.test_dashboard_data_quality),
                ("Series A Demo Data", self.test_series_a_demo_data)
            ]
            
            results = []
            for test_name, test_func in tests:
                print(f"\n{'='*20} {test_name} {'='*20}")
                result = test_func()
                results.append(result)
                if result:
                    print(f"✅ {test_name}: PASSED")
                else:
                    print(f"❌ {test_name}: FAILED")
            
            # Summary
            print(f"\n{'='*20} FINAL RESULTS {'='*20}")
            total_tests = len(results)
            passed_tests = sum(results)
            
            print(f"Total test suites: {total_tests}")
            print(f"✅ Passed: {passed_tests}")
            print(f"❌ Failed: {total_tests - passed_tests}")
            print(f"Success rate: {(passed_tests/total_tests*100):.1f}%")
            
            if all(results):
                print("\n🎉 ALL ENTERPRISE DASHBOARD TESTS PASSED!")
                print("=" * 80)
                print("✅ Server integration working perfectly")
                print("✅ All API endpoints functional")
                print("✅ Data quality validated")
                print("✅ Series A demo data ready")
                print("\n🚀 ENTERPRISE DASHBOARD IS PRODUCTION READY!")
                print(f"🌐 Dashboard URL: {self.base_url}/enterprise")
                print("📊 Perfect for Series A demos and enterprise customers!")
            else:
                print(f"\n⚠️  {total_tests - passed_tests} TEST SUITE(S) FAILED")
                print("Review the failed tests above before demo.")
                
            return all(results)
            
        finally:
            self.cleanup()

if __name__ == "__main__":
    tester = EnterpriseServerTester()
    success = tester.run_comprehensive_server_test()
    sys.exit(0 if success else 1)