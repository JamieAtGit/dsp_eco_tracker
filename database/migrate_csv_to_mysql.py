#!/usr/bin/env python3
"""
Migrate CSV data to MySQL production database
"""
import pandas as pd
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.production')

def connect_to_mysql():
    """Create database connection"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='dsp_eco_tracker',
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD')
        )
        if connection.is_connected():
            print("✅ Connected to MySQL database")
            return connection
    except Error as e:
        print(f"❌ Error connecting to MySQL: {e}")
        return None

def migrate_products_data():
    """Migrate expanded_eco_dataset.csv to products table"""
    connection = connect_to_mysql()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        # Load CSV data
        csv_path = 'common/data/csv/expanded_eco_dataset.csv'
        if not os.path.exists(csv_path):
            print(f"❌ CSV file not found: {csv_path}")
            return False
            
        df = pd.read_csv(csv_path)
        print(f"📊 Loaded {len(df)} products from CSV")
        
        # Insert data into products table
        insert_query = """
        INSERT INTO products (title, material, weight, transport, recyclability, 
                            true_eco_score, co2_emissions, origin, category, search_term)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # Convert DataFrame to list of tuples
        data_tuples = []
        for _, row in df.iterrows():
            data_tuples.append((
                row.get('title', ''),
                row.get('material', ''),
                float(row.get('weight', 0)) if pd.notna(row.get('weight')) else None,
                row.get('transport', ''),
                row.get('recyclability', ''),
                row.get('true_eco_score', ''),
                float(row.get('co2_emissions', 0)) if pd.notna(row.get('co2_emissions')) else None,
                row.get('origin', ''),
                row.get('category', ''),
                row.get('search_term', '')
            ))
        
        # Execute batch insert
        cursor.executemany(insert_query, data_tuples)
        connection.commit()
        
        print(f"✅ Successfully migrated {len(data_tuples)} products to MySQL")
        return True
        
    except Error as e:
        print(f"❌ Error migrating data: {e}")
        return False
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def create_admin_user():
    """Create default admin user"""
    connection = connect_to_mysql()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        # Check if admin user exists
        cursor.execute("SELECT COUNT(*) FROM users WHERE email = 'admin@eco-tracker.com'")
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Create admin user (password: admin123 - change in production!)
            import hashlib
            password_hash = hashlib.sha256('admin123'.encode()).hexdigest()
            
            insert_query = """
            INSERT INTO users (email, password_hash, role) 
            VALUES ('admin@eco-tracker.com', %s, 'admin')
            """
            cursor.execute(insert_query, (password_hash,))
            connection.commit()
            print("✅ Created admin user (admin@eco-tracker.com / admin123)")
        else:
            print("ℹ️ Admin user already exists")
            
        return True
        
    except Error as e:
        print(f"❌ Error creating admin user: {e}")
        return False
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def verify_migration():
    """Verify the migration was successful"""
    connection = connect_to_mysql()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        # Check products count
        cursor.execute("SELECT COUNT(*) FROM products")
        products_count = cursor.fetchone()[0]
        
        # Check users count
        cursor.execute("SELECT COUNT(*) FROM users")
        users_count = cursor.fetchone()[0]
        
        print(f"📊 Database contains:")
        print(f"   - {products_count} products")
        print(f"   - {users_count} users")
        
        # Show sample products
        cursor.execute("SELECT title, material, co2_emissions FROM products LIMIT 5")
        sample_products = cursor.fetchall()
        
        print(f"\n📋 Sample products:")
        for product in sample_products:
            print(f"   - {product[0][:50]}... | {product[1]} | {product[2]} kg CO2")
            
        return True
        
    except Error as e:
        print(f"❌ Error verifying migration: {e}")
        return False
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    print("🚀 Starting CSV to MySQL migration...")
    
    # Step 1: Migrate products data
    if migrate_products_data():
        print("✅ Products migration completed")
    else:
        print("❌ Products migration failed")
        exit(1)
    
    # Step 2: Create admin user
    if create_admin_user():
        print("✅ Admin user setup completed")
    else:
        print("❌ Admin user setup failed")
    
    # Step 3: Verify migration
    if verify_migration():
        print("✅ Migration verification completed")
        print("\n🎉 Database migration successful!")
        print("\n📋 Next steps:")
        print("1. Update Flask app to use MySQL instead of CSV")
        print("2. Test API endpoints with database")
        print("3. Deploy to production server")
    else:
        print("❌ Migration verification failed")