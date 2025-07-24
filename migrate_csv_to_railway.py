#!/usr/bin/env python3
"""
Migrate CSV data to Railway MySQL database
"""
import pandas as pd
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def migrate_products(test_mode=True, batch_size=100):
    """Migrate products from CSV to database"""
    print(f"🚀 Starting {'TEST' if test_mode else 'FULL'} migration...")
    
    try:
        from backend.api.app_production import create_app
        from backend.models.database import db, Product
        
        # Create app
        app = create_app('production')
        
        with app.app_context():
            # Load CSV data
            csv_path = 'common/data/csv/expanded_eco_dataset.csv'
            df = pd.read_csv(csv_path)
            
            # Use subset for testing
            if test_mode:
                df = df.head(batch_size)
                print(f"📊 Test mode: Processing {len(df)} products")
            else:
                print(f"📊 Full mode: Processing all {len(df)} products")
            
            # Clean data
            df = df.fillna('')  # Replace NaN with empty strings
            
            # Clear existing products (if any)
            if test_mode:
                Product.query.delete()
                db.session.commit()
                print("🧹 Cleared existing test data")
            
            # Migrate in batches
            total_migrated = 0
            batch_count = 0
            
            for start_idx in range(0, len(df), 1000):  # 1000 products per batch
                end_idx = min(start_idx + 1000, len(df))
                batch_df = df.iloc[start_idx:end_idx]
                batch_count += 1
                
                print(f"📦 Processing batch {batch_count}: rows {start_idx+1}-{end_idx}")
                
                # Create product objects
                products = []
                for _, row in batch_df.iterrows():
                    product = Product(
                        title=str(row.get('title', ''))[:500],  # Truncate to fit column
                        material=str(row.get('material', ''))[:100],
                        weight=float(row.get('weight', 0)) if pd.notna(row.get('weight')) and str(row.get('weight')).replace('.', '').isdigit() else None,
                        transport=str(row.get('transport', ''))[:50],
                        recyclability=str(row.get('recyclability', ''))[:50],
                        true_eco_score=str(row.get('true_eco_score', ''))[:10],
                        co2_emissions=float(row.get('co2_emissions', 0)) if pd.notna(row.get('co2_emissions')) and str(row.get('co2_emissions')).replace('.', '').isdigit() else None,
                        origin=str(row.get('origin', ''))[:100],
                        category=str(row.get('category', ''))[:100],
                        search_term=str(row.get('search_term', ''))[:200]
                    )
                    products.append(product)
                
                # Bulk insert batch
                db.session.bulk_save_objects(products)
                db.session.commit()
                
                total_migrated += len(products)
                print(f"✅ Batch {batch_count} completed: {len(products)} products")
            
            # Verify migration
            total_in_db = Product.query.count()
            print(f"\n📊 Migration Summary:")
            print(f"   - CSV rows processed: {len(df)}")
            print(f"   - Products migrated: {total_migrated}")
            print(f"   - Products in database: {total_in_db}")
            print(f"   - Batches processed: {batch_count}")
            
            # Show sample products
            sample_products = Product.query.limit(3).all()
            print(f"\n📋 Sample migrated products:")
            for product in sample_products:
                print(f"   - {product.title[:50]}... | {product.material} | {product.co2_emissions} kg CO2")
            
            return total_migrated == total_in_db
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_migration():
    """Verify the migration was successful"""
    print("\n🔍 Verifying migration...")
    
    try:
        from backend.api.app_production import create_app
        from backend.models.database import db, Product
        from sqlalchemy import text
        
        app = create_app('production')
        
        with app.app_context():
            # Basic counts
            total_products = Product.query.count()
            
            # Material distribution
            result = db.session.execute(text("""
                SELECT material, COUNT(*) as count 
                FROM products 
                WHERE material != '' 
                GROUP BY material 
                ORDER BY count DESC 
                LIMIT 5
            """))
            material_stats = list(result)
            
            # Origin distribution  
            result = db.session.execute(text("""
                SELECT origin, COUNT(*) as count 
                FROM products 
                WHERE origin != '' 
                GROUP BY origin 
                ORDER BY count DESC 
                LIMIT 5
            """))
            origin_stats = list(result)
            
            print(f"✅ Verification complete:")
            print(f"   - Total products: {total_products}")
            print(f"   - Top materials: {[(m, c) for m, c in material_stats]}")
            print(f"   - Top origins: {[(o, c) for o, c in origin_stats]}")
            
            return total_products > 0
            
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

def main():
    """Run migration"""
    print("🚀 DSP Eco Tracker - CSV to Railway Migration\n")
    
    # Ask user for migration mode
    print("Migration Options:")
    print("1. Test migration (100 products)")
    print("2. Full migration (50,000 products)")
    
    choice = input("\nChoose option (1 or 2): ").strip()
    
    if choice == "1":
        test_mode = True
        batch_size = 100
    elif choice == "2":
        test_mode = False
        batch_size = 50000
    else:
        print("Invalid choice. Running test migration.")
        test_mode = True
        batch_size = 100
    
    # Run migration
    success = migrate_products(test_mode=test_mode, batch_size=batch_size)
    
    if success:
        # Verify migration
        verify_success = verify_migration()
        
        if verify_success:
            print(f"\n🎉 Migration successful!")
            if test_mode:
                print("🔄 Ready for full migration when you're ready!")
            else:
                print("🚀 Ready for production deployment!")
        else:
            print(f"\n⚠️ Migration completed but verification failed")
    else:
        print(f"\n❌ Migration failed")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)