#!/usr/bin/env python3
"""
Test migration with a small sample of data first
"""
import pandas as pd
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_csv_read():
    """Test reading the CSV file"""
    print("🔍 Testing CSV file reading...")
    
    csv_path = 'common/data/csv/expanded_eco_dataset.csv'
    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found: {csv_path}")
        return False
    
    try:
        df = pd.read_csv(csv_path)
        print(f"✅ CSV loaded successfully: {len(df)} rows, {len(df.columns)} columns")
        print(f"📊 Columns: {list(df.columns)}")
        print(f"🎯 Sample row:")
        print(df.head(1).to_dict('records')[0])
        return df
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return False

def prepare_sample_data(df, sample_size=100):
    """Prepare a small sample for testing"""
    print(f"\n🔍 Preparing sample of {sample_size} products...")
    
    # Take a diverse sample
    sample_df = df.head(sample_size)
    
    # Clean any problematic data
    sample_df = sample_df.fillna('')  # Replace NaN with empty strings
    
    print(f"✅ Sample prepared: {len(sample_df)} products")
    print(f"📊 Materials in sample: {sample_df['material'].value_counts().head()}")
    
    return sample_df

def test_database_connection():
    """Test database connection (when ready)"""
    print("\n🔍 Testing database connection...")
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("⚠️ DATABASE_URL not set - will test when available")
        return False
    
    try:
        from sqlalchemy import create_engine, text
        
        engine = create_engine(database_url)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful")
            return True
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def main():
    """Run migration test"""
    print("🚀 DSP Eco Tracker - Migration Test\n")
    
    # Step 1: Test CSV reading
    df = test_csv_read()
    if df is False:
        return False
    
    # Step 2: Prepare sample
    sample_df = prepare_sample_data(df)
    
    # Step 3: Test database (when available)
    db_connected = test_database_connection()
    
    # Summary
    print(f"\n{'='*50}")
    print("MIGRATION TEST SUMMARY")
    print(f"{'='*50}")
    print(f"CSV Reading: ✅ SUCCESS ({len(df)} products)")
    print(f"Sample Prep: ✅ SUCCESS ({len(sample_df)} products)")
    print(f"Database: {'✅ SUCCESS' if db_connected else '⚠️ PENDING'}")
    
    if not db_connected:
        print("\n📋 Next steps:")
        print("1. Create PlanetScale database")
        print("2. Get connection string")
        print("3. Set DATABASE_URL in .env")
        print("4. Run this test again")
    else:
        print("\n🎉 Ready for full migration!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)