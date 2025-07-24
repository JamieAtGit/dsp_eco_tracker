#!/usr/bin/env python3
"""
Verify and clean up migration
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

def check_migration_status():
    """Check the current state of the database"""
    print("🔍 Checking migration status...")
    
    try:
        from backend.api.app_production import create_app
        from backend.models.database import db, Product
        from sqlalchemy import text
        
        app = create_app('production')
        
        with app.app_context():
            # Get total count
            total_products = Product.query.count()
            print(f"📊 Total products in database: {total_products}")
            
            # Check for duplicates
            result = db.session.execute(text("""
                SELECT title, material, weight, COUNT(*) as count
                FROM products 
                GROUP BY title, material, weight
                HAVING COUNT(*) > 1
                LIMIT 10
            """))
            duplicates = list(result)
            
            if duplicates:
                print(f"⚠️ Found {len(duplicates)} potential duplicate groups")
                for title, material, weight, count in duplicates:
                    print(f"   - '{title[:30]}...' | {material} | {weight} ({count} copies)")
            else:
                print("✅ No duplicates found")
            
            # Check data distribution
            result = db.session.execute(text("""
                SELECT material, COUNT(*) as count 
                FROM products 
                WHERE material != '' 
                GROUP BY material 
                ORDER BY count DESC 
                LIMIT 10
            """))
            material_stats = list(result)
            
            print(f"📈 Material distribution:")
            for material, count in material_stats:
                percentage = (count / total_products) * 100
                print(f"   - {material}: {count} ({percentage:.1f}%)")
            
            return total_products, len(duplicates) == 0
            
    except Exception as e:
        print(f"❌ Error checking migration: {e}")
        return 0, False

def clean_test_data():
    """Remove any test data if needed"""
    print("\n🧹 Cleaning up potential test data...")
    
    try:
        from backend.api.app_production import create_app
        from backend.models.database import db, Product
        from sqlalchemy import text
        
        app = create_app('production')
        
        with app.app_context():
            # Check if we have exactly 50,000 + some test records
            total_before = Product.query.count()
            
            if total_before > 50000:
                # Remove oldest 100 records (likely test data)
                result = db.session.execute(text("""
                    DELETE FROM products 
                    ORDER BY created_at ASC 
                    LIMIT 100
                """))
                db.session.commit()
                
                total_after = Product.query.count()
                removed = total_before - total_after
                
                print(f"✅ Removed {removed} old records")
                print(f"📊 Products now: {total_after}")
                
                return total_after == 50000
            else:
                print(f"✅ Database looks clean: {total_before} products")
                return True
                
    except Exception as e:
        print(f"❌ Error cleaning data: {e}")
        return False

def test_api_connection():
    """Test that our production app can connect to the database"""
    print("\n🔌 Testing API connection...")
    
    try:
        from backend.api.app_production import create_app
        
        app = create_app('production')
        
        with app.test_client() as client:
            # Test health endpoint
            response = client.get('/health')
            
            if response.status_code == 200:
                data = response.get_json()
                print(f"✅ API health check: {data}")
                return True
            else:
                print(f"❌ API health check failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

def main():
    """Verify migration and prepare for deployment"""
    print("🚀 DSP Eco Tracker - Migration Verification\n")
    
    # Step 1: Check migration status
    total_products, no_duplicates = check_migration_status()
    
    # Step 2: Clean up if needed
    if total_products > 50000:
        clean_success = clean_test_data()
    else:
        clean_success = True
    
    # Step 3: Test API
    api_works = test_api_connection()
    
    # Summary
    print(f"\n{'='*50}")
    print("VERIFICATION SUMMARY")
    print(f"{'='*50}")
    print(f"Database Status: {'✅ GOOD' if total_products >= 50000 else '❌ INCOMPLETE'}")
    print(f"Data Quality: {'✅ CLEAN' if no_duplicates else '⚠️ HAS DUPLICATES'}")
    print(f"Cleanup: {'✅ SUCCESS' if clean_success else '❌ FAILED'}")
    print(f"API Connection: {'✅ WORKING' if api_works else '❌ FAILED'}")
    
    if all([total_products >= 50000, no_duplicates, clean_success, api_works]):
        print(f"\n🎉 Migration verification successful!")
        print(f"📊 Database ready with ~50,000 products")
        print(f"🚀 Ready for deployment to Railway!")
        return True
    else:
        print(f"\n⚠️ Some issues found - check details above")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)