#!/usr/bin/env python3
"""
Script to discover the exact structure of the users database
"""

import sys
import os

# Add rexus to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rexus'))

def discover_users_db_structure():
    """Discover the exact table structure of users database"""
    print("=== DESCUBRIENDO ESTRUCTURA DE BD USERS ===\n")
    
    try:
        # Load environment variables from .env file
        from dotenv import load_dotenv
        load_dotenv()
        
        # Verify required environment variables are set
        required_vars = ["DB_SERVER", "DB_USERNAME", "DB_PASSWORD", "DB_USERS"]
        for var in required_vars:
            if not os.getenv(var):
                print(f"ERROR: Environment variable {var} not set. Check your .env file.")
                return False
        
        from core.database import UsersDatabaseConnection
        
        print("1. Connecting to users database...")
        db = UsersDatabaseConnection()
        
        if not db.connect():
            print("   Connection failed")
            return False
        
        print("   Connected successfully!")
        cursor = db.cursor()
        
        print("\n2. Getting table structures...\n")
        
        # Get all tables
        cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
        """)
        tables = [t[0] for t in cursor.fetchall()]
        
        # Analyze each table structure
        for table_name in tables:
            print(f"--- TABLA: {table_name} ---")
            
            # Get column information
            cursor.execute(f"""
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT, CHARACTER_MAXIMUM_LENGTH
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = '{table_name}'
                ORDER BY ORDINAL_POSITION
            """)
            
            columns = cursor.fetchall()
            print("   Columns:")
            for col in columns:
                col_name, data_type, nullable, default, max_len = col
                nullable_str = "NULL" if nullable == "YES" else "NOT NULL"
                len_str = f"({max_len})" if max_len else ""
                default_str = f" DEFAULT {default}" if default else ""
                print(f"     {col_name:<20} {data_type}{len_str:<15} {nullable_str}{default_str}")
            
            # Get row count
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"   Row count: {count}")
                
                # Show sample data for key tables
                if table_name.lower() in ['usuarios'] and count > 0:
                    print("   Sample data:")
                    cursor.execute(f"SELECT TOP 3 * FROM {table_name}")
                    rows = cursor.fetchall()
                    col_names = [desc[0] for desc in cursor.description]
                    
                    for row in rows:
                        row_data = dict(zip(col_names, row))
                        # Hide sensitive data
                        for key in row_data:
                            if 'password' in key.lower() or 'hash' in key.lower():
                                row_data[key] = '[HIDDEN]'
                        print(f"     {row_data}")
                        
            except Exception as e:
                print(f"   Error getting row count: {e}")
            
            print()
        
        db.disconnect()
        print("=== STRUCTURE DISCOVERY COMPLETED ===")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = discover_users_db_structure()
    if success:
        print("\nStructure discovery completed successfully")
    else:
        print("\nStructure discovery failed")