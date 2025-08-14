"""
Migration Validation Script - Rexus.app v2.0.0

Validates the results of database migration by checking created tables,
indexes, and data integrity.
"""

import os
import sys
import pyodbc
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Fallback database configuration
DATABASE_CONFIG = {
    'driver': 'ODBC Driver 17 for SQL Server',
    'server': 'localhost',
    'database': 'inventario',
    'trusted_connection': 'yes'
}


class MigrationValidator:
    """Validates database migration results."""

    def __init__(self):
        self.connection = None

    def connect_database(self):
        """Connect to database."""
        try:
            conn_str = (
                f"DRIVER={{{DATABASE_CONFIG['driver']}}};"
                f"SERVER={DATABASE_CONFIG['server']};"
                f"DATABASE={DATABASE_CONFIG['database']};"
                f"Trusted_Connection={DATABASE_CONFIG.get('trusted_connection', 'yes')}"
            )

            self.connection = pyodbc.connect(conn_str)
            print("[OK] Database connection established")
            return True

        except Exception as e:
            print(f"[ERROR] Database connection failed: {e}")
            return False

    def check_tables_created(self):
        """Check if consolidated tables were created."""
        print("\n[VALIDATION] Checking created tables...")

        expected_tables = [
            'productos',
            'pedidos_consolidado',
            'pedidos_detalle_consolidado',
            'productos_obra',
            'movimientos_inventario',
            'auditoria_consolidada'
        ]

        try:
            cursor = self.connection.cursor()

            # Get all user tables
            cursor.execute("""
                SELECT TABLE_NAME
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_NAME
            """)

            existing_tables = [row[0] for row in cursor.fetchall()]
            print(f"  [INFO] Found {len(existing_tables)} total tables")

            # Check each expected table
            results = {}
            for table in expected_tables:
                exists = table in existing_tables
                results[table] = exists
                status = "[OK]" if exists else "[MISSING]"
                print(f"  {status} {table}")

            # Check for legacy tables still present
            legacy_tables = [
                'inventario_perfiles', 'herrajes', 'vidrios', 'materiales',
                'pedidos', 'pedidos_detalle', 'herrajes_obra', 'vidrios_obra'
            ]

            print(f"\n  [INFO] Legacy tables still present:")
            for table in legacy_tables:
                exists = table in existing_tables
                status = "[EXISTS]" if exists else "[DROPPED]"
                print(f"  {status} {table}")

            return results

        except Exception as e:
            print(f"  [ERROR] Table validation failed: {e}")
            return {}

    def check_table_structure(self, table_name):
        """Check structure of a specific table."""
        try:
            cursor = self.connection.cursor()

            # Get column information
            cursor.execute(f"""
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = '{table_name}'
                ORDER BY ORDINAL_POSITION
            """)

            columns = cursor.fetchall()
            if columns:
                print(f"\n  [INFO] {table_name} structure ({len(columns)} columns):")
                for col in columns[:10]:  # Show first 10 columns
                    nullable = "NULL" if col[2] == "YES" else "NOT NULL"
                    default = f"DEFAULT {col[3]}" if col[3] else ""
                    print(f"    - {col[0]}: {col[1]} {nullable} {default}")

                if len(columns) > 10:
                    print(f"    ... and {len(columns) - 10} more columns")

            return len(columns)

        except Exception as e:
            print(f"  [ERROR] Structure check failed for {table_name}: {e}")
            return 0

    def check_indexes_created(self):
        """Check if indexes were created."""
        print("\n[VALIDATION] Checking indexes...")

        try:
            cursor = self.connection.cursor()

            # Get indexes for consolidated tables
            cursor.execute("""
                SELECT
                    t.name as table_name,
                    i.name as index_name,
                    i.type_desc as index_type
                FROM sys.indexes i
                INNER JOIN sys.tables t ON i.object_id = t.object_id
                WHERE t.name IN ('productos',
'pedidos_consolidado',
                    'productos_obra',
                    'movimientos_inventario')
                    AND i.name IS NOT NULL
                ORDER BY t.name, i.name
            """)

            indexes = cursor.fetchall()

            if indexes:
                print(f"  [INFO] Found {len(indexes)} indexes:")
                current_table = None
                for idx in indexes:
                    if current_table != idx[0]:
                        current_table = idx[0]
                        print(f"    {current_table}:")
                    print(f"      - {idx[1]} ({idx[2]})")
            else:
                print("  [WARNING] No indexes found for consolidated tables")

            return len(indexes)

        except Exception as e:
            print(f"  [ERROR] Index validation failed: {e}")
            return 0

    def check_data_migration(self):
        """Check if data was migrated successfully."""
        print("\n[VALIDATION] Checking data migration...")

        data_checks = [
            ("productos", "SELECT COUNT(*) FROM productos"),
            ("productos by category", "SELECT categoria, COUNT(*) FROM productos GROUP BY categoria"),
            ("pedidos_consolidado", "SELECT COUNT(*) FROM pedidos_consolidado"),
            ("productos_obra", "SELECT COUNT(*) FROM productos_obra"),
            ("movimientos_inventario", "SELECT COUNT(*) FROM movimientos_inventario")
        ]

        try:
            cursor = self.connection.cursor()
            results = {}

            for check_name, query in data_checks:
                try:
                    cursor.execute(query)

                    if "GROUP BY" in query:
                        # Handle grouped results
                        rows = cursor.fetchall()
                        if rows:
                            print(f"  [INFO] {check_name}:")
                            for row in rows:
                                print(f"    - {row[0]}: {row[1]} records")
                            results[check_name] = len(rows)
                        else:
                            print(f"  [INFO] {check_name}: No data")
                            results[check_name] = 0
                    else:
                        # Handle count results
                        result = cursor.fetchone()
                        count = result[0] if result else 0
                        print(f"  [INFO] {check_name}: {count} records")
                        results[check_name] = count

                except Exception as e:
                    print(f"  [ERROR] {check_name}: {e}")
                    results[check_name] = "error"

            return results

        except Exception as e:
            print(f"  [ERROR] Data validation failed: {e}")
            return {}

    def check_views_and_procedures(self):
        """Check if views and stored procedures were created."""
        print("\n[VALIDATION] Checking views and procedures...")

        try:
            cursor = self.connection.cursor()

            # Check views
            cursor.execute("""
                SELECT TABLE_NAME
                FROM INFORMATION_SCHEMA.VIEWS
                WHERE TABLE_NAME LIKE '%productos%' OR TABLE_NAME LIKE '%consolidado%'
                ORDER BY TABLE_NAME
            """)

            views = [row[0] for row in cursor.fetchall()]
            print(f"  [INFO] Views: {len(views)}")
            for view in views:
                print(f"    - {view}")

            # Check procedures
            cursor.execute("""
                SELECT ROUTINE_NAME
                FROM INFORMATION_SCHEMA.ROUTINES
                WHERE ROUTINE_TYPE = 'PROCEDURE'
                    AND (ROUTINE_NAME LIKE '%productos%' OR ROUTINE_NAME LIKE '%consolidado%')
                ORDER BY ROUTINE_NAME
            """)

            procedures = [row[0] for row in cursor.fetchall()]
            print(f"  [INFO] Procedures: {len(procedures)}")
            for proc in procedures:
                print(f"    - {proc}")

            return {"views": len(views), "procedures": len(procedures)}

        except Exception as e:
            print(f"  [ERROR] Views/procedures validation failed: {e}")
            return {}

    def run_validation(self):
        """Run complete validation."""
        print("="*60)
        print("DATABASE MIGRATION VALIDATION")
        print("="*60)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        if not self.connect_database():
            return False

        try:
            # Run all validation checks
            table_results = self.check_tables_created()

            # Check structure of key tables
            if 'productos' in table_results and table_results['productos']:
                self.check_table_structure('productos')

            if 'pedidos_consolidado' in table_results and \
                table_results['pedidos_consolidado']:
                self.check_table_structure('pedidos_consolidado')

            index_count = self.check_indexes_created()
            data_results = self.check_data_migration()
            view_proc_results = self.check_views_and_procedures()

            # Generate summary
            print("\n" + "="*60)
            print("VALIDATION SUMMARY")
            print("="*60)

            tables_created = sum(1 for v in table_results.values() if v)
            total_expected = len(table_results)

            print(f"Tables created: {tables_created}/{total_expected}")
            print(f"Indexes created: {index_count}")
            print(f"Views created: {view_proc_results.get('views', 0)}")
            print(f"Procedures created: {view_proc_results.get('procedures', 0)}")

            # Data summary
            productos_count = data_results.get('productos', 0)
            if isinstance(productos_count, int) and productos_count > 0:
                print(f"Products migrated: {productos_count}")
            else:
                print("Products migration: NEEDS ATTENTION")

            # Overall assessment
            success_rate = (tables_created / total_expected) * 100 if total_expected > 0 else 0

            if success_rate >= 80 and productos_count != "error":
                print("\n[SUCCESS] Migration validation passed!")
                print("The consolidated database structure is ready for use.")
                return True
            else:
                print("\n[WARNING] Migration validation found issues!")
                print("Some components may need manual attention.")
                return False

        finally:
            if self.connection:
                self.connection.close()
                print("\nDatabase connection closed.")


def main():
    """Main execution."""
    validator = MigrationValidator()
    success = validator.run_validation()

    if not success:
        print("\nRecommendations:")
        print("- Check migration logs for detailed errors")
        print("- Verify database permissions")
        print("- Consider running individual migration scripts manually")
        sys.exit(1)


if __name__ == "__main__":
    main()
