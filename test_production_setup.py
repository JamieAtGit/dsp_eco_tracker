#!/usr/bin/env python3
"""
Test script for production setup
Tests database models, app creation, and basic functionality
"""
import os
import sys
sys.path.append('.')

def test_imports():
    """Test that all imports work correctly"""
    print("🔍 Testing imports...")
    
    try:
        from backend.models.database import db, User, Product, ScrapedProduct
        print("✅ Database models imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import database models: {e}")
        return False
    
    try:
        from backend.api.app_production import create_app
        print("✅ Production app imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import production app: {e}")
        return False
    
    return True

def test_app_creation():
    """Test Flask app creation with SQLite (for testing)"""
    print("\n🔍 Testing app creation...")
    
    try:
        from backend.api.app_production import create_app
        
        # Create test app with SQLite
        app = create_app('development')
        
        with app.app_context():
            from backend.models.database import db
            db.create_all()
            print("✅ Test database tables created successfully")
        
        print("✅ Flask app created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create app: {e}")
        return False

def test_database_operations():
    """Test basic database operations"""
    print("\n🔍 Testing database operations...")
    
    try:
        from backend.api.app_production import create_app
        from backend.models.database import db, Product, save_scraped_product
        
        app = create_app('development')
        
        with app.app_context():
            # Test adding a product
            test_product = Product(
                title="Test Reusable Water Bottle",
                material="Steel",
                weight=1.5,
                transport="Ship",
                recyclability="High",
                true_eco_score="B",
                co2_emissions=2.3,
                origin="China",
                category="Home & Garden"
            )
            
            db.session.add(test_product)
            db.session.commit()
            
            # Test querying
            products = Product.query.all()
            print(f"✅ Database operations successful - {len(products)} products in database")
            
            # Test scraped product saving
            scraped_data = {
                'amazon_url': 'https://amazon.com/test',
                'title': 'Test Product',
                'material': 'Plastic',
                'weight': 0.5,
                'scraping_status': 'success'
            }
            
            saved_product = save_scraped_product(scraped_data)
            print(f"✅ Scraped product saved with ID: {saved_product.id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database operations failed: {e}")
        return False

def test_requirements():
    """Test that required packages are installed"""
    print("\n🔍 Testing requirements...")
    
    required_packages = [
        'flask', 'flask_sqlalchemy', 'flask_cors', 'flask_migrate',
        'pandas', 'numpy', 'sklearn', 'xgboost', 'selenium',
        'beautifulsoup4', 'requests', 'pgeocode', 'pymysql'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            # Handle special package names
            import_name = package.replace('-', '_')
            if package == 'beautifulsoup4':
                import_name = 'bs4'
            elif package == 'sklearn':
                import_name = 'sklearn'
            
            __import__(import_name)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - NOT INSTALLED")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r backend/requirements.txt")
        return False
    
    print("✅ All required packages are installed")
    return True

def main():
    """Run all tests"""
    print("🚀 DSP Eco Tracker - Production Setup Test\n")
    
    tests = [
        ("Requirements Check", test_requirements),
        ("Import Test", test_imports),
        ("App Creation", test_app_creation),
        ("Database Operations", test_database_operations)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print(f"{'='*50}")
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*50}")
    print("SUMMARY")
    print(f"{'='*50}")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Ready for production deployment.")
        return True
    else:
        print(f"\n⚠️ {len(results) - passed} tests failed. Fix issues before deploying.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)