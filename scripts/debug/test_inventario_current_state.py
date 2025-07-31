"""
Debug Script - Test Current Inventario State
Tests the current inventario model and identifies any issues before migration.
"""

import sys
import os
import pyodbc
from datetime import datetime

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Database configuration
DATABASE_CONFIG = {
    'driver': 'ODBC Driver 17 for SQL Server',
    'server': 'localhost',
    'database': 'inventario',
    'trusted_connection': 'yes'
}

def get_database_connection():
    """Get database connection."""
    try:
        conn_str = (
            f"DRIVER={{{DATABASE_CONFIG['driver']}}};"
            f"SERVER={DATABASE_CONFIG['server']};"
            f"DATABASE={DATABASE_CONFIG['database']};"
            f"Trusted_Connection={DATABASE_CONFIG.get('trusted_connection', 'yes')}"
        )
        conn = pyodbc.connect(conn_str)
        print("[OK] Database connection established")
        return conn
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        return None

def test_legacy_inventario_model():
    """Test the legacy inventario model."""
    print("\n[TEST] Legacy InventarioModel...")
    
    try:
        from src.modules.inventario.model import InventarioModel
        
        # Test with database connection
        conn = get_database_connection()
        if not conn:
            print("  [SKIP] No database connection available")
            return False
        
        # Initialize model
        inventario = InventarioModel(db_connection=conn)
        print("  [OK] Legacy InventarioModel initialized")
        
        # Test basic functionality
        try:
            productos = inventario.obtener_todos_productos()
            print(f"  [OK] Retrieved {len(productos)} products from legacy model")
        except Exception as e:
            print(f"  [ERROR] Error getting products: {e}")
        
        # Test search functionality
        try:
            search_results = inventario.buscar_productos({"busqueda": "perfil"})
            print(f"  [OK] Search returned {len(search_results)} results")
        except Exception as e:
            print(f"  [ERROR] Error in search: {e}")
        
        # Test statistics
        try:
            stats = inventario.obtener_estadisticas_inventario()
            print(f"  [OK] Statistics retrieved: {len(stats)} metrics")
        except Exception as e:
            print(f"  [ERROR] Error getting statistics: {e}")
        
        conn.close()
        return True
        
    except ImportError as e:
        print(f"  [ERROR] Could not import InventarioModel: {e}")
        return False
    except Exception as e:
        print(f"  [ERROR] Legacy model test failed: {e}")
        return False

def test_consolidated_inventario_model():
    """Test the consolidated inventario model."""
    print("\n[TEST] Consolidated InventarioModel...")
    
    try:
        from src.modules.inventario.model_consolidado import InventarioModel
        
        # Test with database connection
        conn = get_database_connection()
        if not conn:
            print("  [SKIP] No database connection available")
            return False
        
        # Initialize model
        inventario = InventarioModel(db_connection=conn)
        print("  [OK] Consolidated InventarioModel initialized")
        
        # Test basic functionality
        try:
            productos = inventario.obtener_todos_productos()
            print(f"  [OK] Retrieved {len(productos)} products from consolidated model")
            
            # Show sample product structure
            if productos:
                sample = productos[0]
                print(f"  [INFO] Sample product structure: {list(sample.keys())[:10]}...")
        except Exception as e:
            print(f"  [ERROR] Error getting products: {e}")
        
        # Test category filtering
        try:
            herrajes = inventario.obtener_todos_productos({"categoria": "HERRAJE"})
            vidrios = inventario.obtener_todos_productos({"categoria": "VIDRIO"})
            perfiles = inventario.obtener_todos_productos({"categoria": "PERFIL"})
            materiales = inventario.obtener_todos_productos({"categoria": "MATERIAL"})
            
            print(f"  [OK] By category: HERRAJE={len(herrajes)}, VIDRIO={len(vidrios)}, PERFIL={len(perfiles)}, MATERIAL={len(materiales)}")
        except Exception as e:
            print(f"  [ERROR] Error in category filtering: {e}")
        
        # Test search functionality
        try:
            search_results = inventario.buscar_productos({"busqueda": "perfil"})
            print(f"  [OK] Search returned {len(search_results)} results")
        except Exception as e:
            print(f"  [ERROR] Error in search: {e}")
        
        # Test statistics
        try:
            stats = inventario.obtener_estadisticas_inventario()
            print(f"  [OK] Statistics retrieved: {stats.get('total_productos', 0)} total products")
        except Exception as e:
            print(f"  [ERROR] Error getting statistics: {e}")
        
        conn.close()
        return True
        
    except ImportError as e:
        print(f"  [ERROR] Could not import consolidated InventarioModel: {e}")
        return False
    except Exception as e:
        print(f"  [ERROR] Consolidated model test failed: {e}")
        return False

def check_database_tables():
    """Check what tables exist in the database."""
    print("\n[TEST] Database Table Structure...")
    
    conn = get_database_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
        """)
        
        all_tables = [row[0] for row in cursor.fetchall()]
        
        # Check for legacy tables
        legacy_tables = ['inventario_perfiles', 'herrajes', 'vidrios', 'materiales']
        print("  [INFO] Legacy Tables:")
        for table in legacy_tables:
            status = "EXISTS" if table in all_tables else "MISSING"
            print(f"    - {table}: {status}")
        
        # Check for consolidated tables
        consolidated_tables = ['productos', 'pedidos_consolidado', 'productos_obra', 'movimientos_inventario']
        print("  [INFO] Consolidated Tables:")
        for table in consolidated_tables:
            status = "EXISTS" if table in all_tables else "MISSING"
            print(f"    - {table}: {status}")
            
            # Get row count if table exists
            if table in all_tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"      └─ {count} records")
                except:
                    print(f"      └─ Unable to count records")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"  [ERROR] Database table check failed: {e}")
        return False

def compare_model_performance():
    """Compare performance between legacy and consolidated models."""
    print("\n[TEST] Model Performance Comparison...")
    
    conn = get_database_connection()
    if not conn:
        return False
    
    try:
        # Test legacy model performance
        start_time = datetime.now()
        try:
            from src.modules.inventario.model import InventarioModel as LegacyModel
            legacy = LegacyModel(db_connection=conn)
            legacy_products = legacy.obtener_todos_productos()
            legacy_time = (datetime.now() - start_time).total_seconds()
            print(f"  [INFO] Legacy model: {len(legacy_products)} products in {legacy_time:.3f}s")
        except Exception as e:
            print(f"  [ERROR] Legacy model performance test failed: {e}")
            legacy_time = None
        
        # Test consolidated model performance
        start_time = datetime.now()
        try:
            from src.modules.inventario.model_consolidado import InventarioModel as ConsolidatedModel
            consolidated = ConsolidatedModel(db_connection=conn)
            consolidated_products = consolidated.obtener_todos_productos()
            consolidated_time = (datetime.now() - start_time).total_seconds()
            print(f"  [INFO] Consolidated model: {len(consolidated_products)} products in {consolidated_time:.3f}s")
        except Exception as e:
            print(f"  [ERROR] Consolidated model performance test failed: {e}")
            consolidated_time = None
        
        # Compare performance
        if legacy_time and consolidated_time:
            if consolidated_time < legacy_time:
                improvement = ((legacy_time - consolidated_time) / legacy_time) * 100
                print(f"  [SUCCESS] Consolidated model is {improvement:.1f}% faster")
            else:
                degradation = ((consolidated_time - legacy_time) / legacy_time) * 100
                print(f"  [WARNING] Consolidated model is {degradation:.1f}% slower")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"  [ERROR] Performance comparison failed: {e}")
        return False

def main():
    """Main debug execution."""
    print("="*70)
    print("INVENTARIO DEBUG - CURRENT STATE ANALYSIS")
    print("="*70)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Database Table Structure", check_database_tables),
        ("Legacy InventarioModel", test_legacy_inventario_model),
        ("Consolidated InventarioModel", test_consolidated_inventario_model),
        ("Model Performance Comparison", compare_model_performance)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*25} {test_name} {'='*25}")
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "="*70)
    print("DEBUG SUMMARY")
    print("="*70)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    success_rate = (passed / total * 100) if total > 0 else 0
    print(f"\nTotal tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success rate: {success_rate:.1f}%")
    
    # Recommendations
    print("\n" + "="*70)
    print("RECOMMENDATIONS")
    print("="*70)
    
    if success_rate >= 75:
        print("✅ System is ready for production migration")
        print("- Consolidated models are working correctly")
        print("- Database structure is properly set up")
        print("- Performance is acceptable")
    elif success_rate >= 50:
        print("⚠️  System has some issues but is partially functional")
        print("- Review failed tests and address issues")
        print("- Consider gradual migration approach")
    else:
        print("❌ System has significant issues")
        print("- Address critical failures before proceeding")
        print("- Review database structure and model implementations")
    
    return success_rate >= 75

if __name__ == "__main__":
    main()